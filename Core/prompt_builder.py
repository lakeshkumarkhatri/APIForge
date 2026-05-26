import json
import re


# ─────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────

def count_body_fields(body) -> int:
    if not body:
        return 0
    if isinstance(body, dict):
        return len(body)
    if isinstance(body, str):
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                return len(parsed)
        except Exception:
            pass
    return 0


def get_scenario_count(body, override: int = None) -> int:
    """
    Returns the MINIMUM number of scenarios to generate.
    This is a floor — the model must generate more if field analysis finds typed fields.

    Breakdown:
      0 fields  → 2  (valid + no-auth)
      1 field   → 3  (valid + empty + field-specific)
      2-3 fields → base 5 (valid + empty + null + missing body + missing field)
                   + field-specific count (1 per field type found)
      4+ fields  → base 5 + field-specific + auth = typically 8+

    Pass override to force a specific count (e.g. to match a client's style).
    """
    if override is not None:
        return override

    field_count = count_body_fields(body)
    if field_count == 0:
        return 2
    elif field_count == 1:
        return 3
    elif field_count <= 3:
        # base 5 + at minimum 1 field-specific scenario
        return 6
    else:
        # base 5 + multiple field-specific + auth
        return 8


def _extract_field_names(body) -> str:
    """
    Returns a comma-separated string of field names from body.
    Used to inject exact field names into prompts as a grounding constraint.
    """
    if not body:
        return "none"
    if isinstance(body, dict):
        return ", ".join(body.keys())
    if isinstance(body, str):
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                return ", ".join(parsed.keys())
        except Exception:
            pass
    return str(body)


def parse_raw_input(raw_input: str) -> dict:
    """
    Parses free-text API descriptions in Python BEFORE sending to the model.
    Extracts endpoint, method, auth, and body fields from the raw string.

    This is the core fix for the hallucination problem:
    - Model used to extract fields itself → could drift or invent new ones
    - Now Python extracts them deterministically → model gets locked values

    Handles formats like:
      /sd/pre-url POST | auth Request body: { "file_name": "string", ... }
      POST /api/users/register
      curl -X POST https://api.example.com/login -d '{"email":"","password":""}'
      Any other free-text description
    """
    import re

    result = {
        "endpoint": None,
        "method": None,
        "auth_required": False,
        "fields": [],        # list of field name strings, order preserved
        "body_raw": None,    # the raw JSON object string if found
    }

    text = raw_input.strip()

    # ── METHOD detection ──────────────────────────────────────────────
    method_match = re.search(
        r'\b(GET|POST|PUT|PATCH|DELETE)\b', text, re.IGNORECASE
    )
    if method_match:
        result["method"] = method_match.group(1).upper()

    # ── ENDPOINT detection ────────────────────────────────────────────
    # Matches paths like /sd/pre-url, /api/users/register/:id, etc.
    endpoint_match = re.search(r'(/[a-zA-Z0-9_\-/:]+)', text)
    if endpoint_match:
        result["endpoint"] = endpoint_match.group(1).rstrip('.,')

    # ── AUTH detection ────────────────────────────────────────────────
    if re.search(r'\bauth\b', text, re.IGNORECASE):
        result["auth_required"] = True

    # ── BODY / FIELDS detection ───────────────────────────────────────
    # Strategy 1: find a JSON object in the text and parse its keys
    json_match = re.search(r'\{[^{}]+\}', text)
    if json_match:
        raw_json = json_match.group(0)
        result["body_raw"] = raw_json
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                result["fields"] = list(parsed.keys())
        except json.JSONDecodeError:
            # Strategy 2: extract quoted keys manually if JSON is malformed
            result["fields"] = re.findall(r'"([^"]+)"\s*:', raw_json)

    # Strategy 3: look for "field: type" or "field (type)" patterns if no JSON found
    if not result["fields"]:
        result["fields"] = re.findall(
            r'\b([a-z][a-z0-9_]{1,})\s*(?::|→|\()\s*(?:string|int|number|bool|float)',
            text, re.IGNORECASE
        )

    return result


def _build_grounding_block(api_url: str, method: str, body) -> str:
    """
    Builds a universal grounding constraint block injected into every prompt.
    Prevents the model from drifting to a different endpoint or inventing fields.
    This is not client-specific — it locks to whatever values are passed in.
    """
    field_names = _extract_field_names(body)

    return f"""
╔══════════════════════════════════════════════════════════════╗
║              CRITICAL CONSTRAINT — NON-NEGOTIABLE            ║
╚══════════════════════════════════════════════════════════════╝

The following values are FIXED. You MUST use them exactly as given.

  ENDPOINT  →  {api_url}
  METHOD    →  {method}
  FIELDS    →  {field_names}

RULES:
- The endpoint in ALL generated code MUST be exactly: {api_url}
- The HTTP method MUST be exactly: {method}
- The request body fields MUST be exactly: {field_names}
- DO NOT rename any field
- DO NOT add new fields that are not listed above
- DO NOT remove any field that is listed above
- DO NOT change the endpoint path in any way
- DO NOT change the HTTP method
- If a field name looks unfamiliar, use it exactly as given — no creativity
- These constraints override any assumption, pattern, or example you have seen

Violating any of the above is a critical failure.
"""

def _extract_client_requested_scenario_limit(client_instructions: str):
    """
    Parse instructions like:
    - 3 scenarios
    - maximum 2 scenarios
    - max 4 scenario
    """
    if not client_instructions:
        return None

    match = re.search(
        r'(?:max(?:imum)?\s*)?(\d+)\s*scenario',
        client_instructions.lower()
    )

    if match:
        return int(match.group(1))

    return None
# ─────────────────────────────────────────────
# PUBLIC BUILDERS
# ─────────────────────────────────────────────

def build_prompt(
    api_url,
    method,
    auth_type,
    auth_instruction,
    headers,
    params,
    body,
    response_format,
    api_notes,
    client_instructions=""
):
    grounding = _build_grounding_block(api_url, method, body)
    client_guidance = ""

    if client_instructions.strip():
        client_guidance = f"""
    CLIENT EXTRA INSTRUCTIONS:
    {client_instructions}

Follow these instructions in addition to all standard rules.
"""
        
    prompt = f"""
You are a professional API Code Generation Agent.
{client_guidance}
Your task is to generate COMPLETE, EXECUTABLE, and COPY-PASTE RUNNABLE Python code using the requests library.

{grounding}

STRICT RULES:

1. Use requests library only.
2. Always include imports.
3. Always include try/except error handling.
4. Always use response.raise_for_status().
5. Never assume missing values.
6. Use ONLY the information provided.
7. If auth type is public, do not add auth.
8. If method is GET, prefer params instead of request body.
9. If method is POST/PUT/PATCH, use request body when provided.
10. Match response handling to response format.
11. Return executable Python code only.
12. No markdown.
13. No explanations.
14. No placeholder guessing.
15. Code must be runnable immediately.
16. Avoid printing excessively large responses.
17. Prefer concise and readable output.
18. If response is large, show summary or limited preview.

API DETAILS:

API URL:
{api_url}

HTTP METHOD:
{method}

AUTHENTICATION TYPE:
{auth_type}

Authentication Instruction:
{auth_instruction}

HEADERS:
{headers}

QUERY PARAMETERS:
{params}

REQUEST BODY:
{body}

RESPONSE FORMAT:
{response_format}

API DOCUMENTATION / NOTES:

{api_notes}

Generate final Python code now.
"""
    return prompt


def build_scenario_prompt(
    api_url,
    method,
    auth_type,
    auth_instruction,
    headers,
    params,
    body,
    response_format,
    api_notes,
    output_language="python",
    scenario_count_override=None,
    client_instructions=""
):
    scenario_count = get_scenario_count(body, override=scenario_count_override)

    if output_language == "cypress":
        return _build_cypress_scenario_prompt(
            api_url,
            method,
            auth_type,
            headers,
            params,
            body,
            scenario_count,
            api_notes,
            client_instructions
        )
    else:
        return _build_python_scenario_prompt(
            api_url,
            method,
            auth_type,
            auth_instruction,
            headers,
            params,
            body,
            response_format,
            scenario_count,
            api_notes,
            client_instructions
        )


def build_universal_scenario_prompt(
    raw_input: str,
    output_language: str = "cypress",
    scenario_count_override: int = None,
    client_instructions: str = ""
):
    """
    Accepts raw API description in ANY format.

    ROOT CAUSE FIX:
    Previously the model was asked to extract the endpoint and fields itself,
    which allowed it to drift to training examples like /api/payments or /api/invoices.

    Now Python parses the raw input FIRST via parse_raw_input(), extracts endpoint,
    method, auth, and exact field names deterministically, then injects them as
    pre-locked values into the prompt. The model never gets to decide what the
    endpoint or fields are — they are already decided before the prompt is built.

    Falls back gracefully if input is too ambiguous to parse.
    """
    scenario_rules = _get_scenario_rules()
    naming_rules = _get_naming_rules()
    analysis_rules = _get_analysis_rules()

    if output_language == "cypress":
        output_rules = _get_cypress_output_rules()
    else:
        output_rules = _get_python_output_rules()

    # ── Parse in Python before the model sees anything ────────────────
    parsed = parse_raw_input(raw_input)

    endpoint  = parsed["endpoint"] or "NOT FOUND — extract carefully from user input"
    method    = parsed["method"]   or "NOT FOUND — extract from user input"
    auth_line = "YES — use 'auth' in helper function" if parsed["auth_required"] else "NO — pass null"
    body_raw  = parsed["body_raw"] or "none found"

    if parsed["fields"]:
        fields_locked = ", ".join(parsed["fields"])
        fields_count  = len(parsed["fields"])
        fields_note   = "FINAL — extracted by Python parser, do not change"
    else:
        fields_locked = "NOT FOUND — extract exactly from user input, then treat as final"
        fields_count  = 0
        fields_note   = "parser could not find fields — extract carefully"

    # Build a proxy dict so get_scenario_count can count fields correctly
    _body_proxy = {f: None for f in parsed["fields"]} if parsed["fields"] else {}
    scenario_count = get_scenario_count(_body_proxy, override=scenario_count_override)

    effective_scenario_count = scenario_count
    requested_limit = _extract_client_requested_scenario_limit(client_instructions)

    if requested_limit:
        effective_scenario_count = min(requested_limit, scenario_count)

    client_guidance = ""

    if client_instructions.strip():
        client_guidance = f"""
    ══════════════════════════════════════════
    CLIENT EXTRA INSTRUCTIONS
    ══════════════════════════════════════════

    {client_instructions}

    These instructions are additional constraints and must be followed.
    """

    prompt = f"""    
You are a universal API test scenario generator with deep understanding of REST APIs, QA testing, and real-world backend behavior.

╔══════════════════════════════════════════════════════════════════════╗
║         PRE-EXTRACTED API CONTRACT — LOCKED — DO NOT CHANGE         ║
╚══════════════════════════════════════════════════════════════════════╝

These values were extracted from the user input by a Python parser BEFORE this prompt was built.
They are already final. Your only job is to use them exactly as shown.

  ENDPOINT    →  {endpoint}
  METHOD      →  {method}
  AUTH        →  {auth_line}
  FIELDS      →  {fields_locked}
  FIELD COUNT →  {fields_count}  ({fields_note})
  RAW BODY    →  {body_raw}

ABSOLUTE RULES — VIOLATION = CRITICAL FAILURE:
1. Every line of generated code MUST use endpoint: {endpoint}
2. Every line of generated code MUST use method: {method}
3. The helper function body MUST contain ONLY these fields: {fields_locked}
4. DO NOT add any field that is not in the list above
5. DO NOT rename any field — use the exact names as given
6. DO NOT remove any field from the list above
7. DO NOT use any endpoint from your training data (e.g. /api/payments, /api/invoices, /api/orders)
8. If a field name looks unusual — use it exactly anyway
9. Default scenario count = {scenario_count}. Final generation count after client limits = {effective_scenario_count}.

══════════════════════════════════════════════════════════════════
FIELD ANALYSIS — apply to the {fields_count} fields listed above
══════════════════════════════════════════════════════════════════

{analysis_rules}

══════════════════════════════════════════
NAMING AND AUTH RULES
══════════════════════════════════════════

{naming_rules}

══════════════════════════════════════════
SCENARIO GENERATION RULES
══════════════════════════════════════════

{scenario_rules}

══════════════════════════════════════════
OUTPUT FORMAT
══════════════════════════════════════════

{output_rules}
{client_guidance}
FINAL CHECKS BEFORE GENERATING:
- Is the endpoint in every apiRequest call exactly: {endpoint}? If not, fix it.
- Does the helper function body contain exactly these fields: {fields_locked}? If not, fix it.
- Is cy.log(JSON.stringify(res.body)) the last line in every .then() block? If not, fix it.

ORIGINAL USER INPUT (reference only — values already extracted above):
{raw_input}

Generate exactly {effective_scenario_count} scenario(s) now.
"""
    return prompt


# ─────────────────────────────────────────────
# INTERNAL BUILDERS
# ─────────────────────────────────────────────

def _build_python_scenario_prompt(
    api_url,
    method,
    auth_type,
    auth_instruction,
    headers,
    params,
    body,
    response_format,
    scenario_count,
    api_notes,
    client_instructions=""
):
    scenario_rules = _get_scenario_rules()
    naming_rules = _get_naming_rules()
    analysis_rules = _get_analysis_rules()
    output_rules = _get_python_output_rules()
    grounding = _build_grounding_block(api_url, method, body)
    client_guidance = ""

    if client_instructions.strip():
        client_guidance = f"""
    CLIENT EXTRA INSTRUCTIONS:
    {client_instructions}

    Follow these instructions in addition to all rules.
    """
    prompt = f"""
You are a professional API Test Scenario Generation Agent with deep QA expertise.

{grounding}

GLOBAL RULES:
1. Always use flat executable scripts — never wrap in functions.
2. Every scenario must have a clear comment block header.
3. Every scenario must state the expected HTTP status code.
4. Use realistic test values — no placeholders.
5. No markdown. No explanations outside comments.
6. Code must be runnable immediately.

API DETAILS:

API URL:
{api_url}

HTTP METHOD:
{method}

AUTHENTICATION TYPE:
{auth_type}

Authentication Instruction:
{auth_instruction}

HEADERS:
{headers}

QUERY PARAMETERS:
{params}

REQUEST BODY:
{body}

RESPONSE FORMAT:
{response_format}

API NOTES:
{api_notes}

FIELD ANALYSIS RULES:

{analysis_rules}

NAMING AND AUTH RULES:

{naming_rules}

SCENARIO GENERATION RULES:

{scenario_rules}

OUTPUT FORMAT:

{output_rules}
{client_guidance}

Generate exactly {effective_scenario_count} scenario(s) now.
"""
    return prompt


def _build_cypress_scenario_prompt(
    api_url,
    method,
    auth_type,
    headers,
    params,
    body,
    scenario_count,
    api_notes,
    client_instructions=""
):
    scenario_rules = _get_scenario_rules()
    naming_rules = _get_naming_rules()
    analysis_rules = _get_analysis_rules()
    output_rules = _get_cypress_output_rules()
    grounding = _build_grounding_block(api_url, method, body)
    client_guidance = ""

    if client_instructions.strip():
        client_guidance = f"""
    CLIENT EXTRA INSTRUCTIONS:
    {client_instructions}

    Follow these instructions in addition to all rules.
    """
    prompt = f"""
You are a professional Cypress API Test Scenario Generation Agent with deep QA expertise.

Your task is to generate COMPLETE Cypress API test scenarios.

{grounding}

GLOBAL RULES:
1. getData().then() pattern is MANDATORY — never use Promise.resolve() or object literals with .then()
2. cy.log(JSON.stringify(res.body)) is MANDATORY in EVERY single .then() block
3. Scenario 1 (valid) MUST call the helper function with NO arguments
4. failOnStatusCode = false for ALL negative test cases
5. Apply ALL Analysis, Naming, and Scenario Rules before generating
6. ALWAYS follow scenario order strictly

API DETAILS:

API URL:
{api_url}

HTTP METHOD:
{method}

AUTHENTICATION TYPE:
{auth_type}

HEADERS:
{headers}

QUERY PARAMETERS:
{params}

REQUEST BODY:
{body}

API NOTES:
{api_notes}

FIELD ANALYSIS RULES — READ EVERY FIELD CAREFULLY:

{analysis_rules}

NAMING AND AUTH RULES:

{naming_rules}

SCENARIO GENERATION RULES:

{scenario_rules}

OUTPUT FORMAT:

{output_rules}
{client_guidance}

Generate exactly {effective_scenario_count} scenario(s) now.
"""
    return prompt


# ─────────────────────────────────────────────
# RULE BLOCKS
# ─────────────────────────────────────────────

def _get_analysis_rules() -> str:
    return """
FIELD ANALYSIS — DO THIS FOR EVERY FIELD IN THE BODY:

For each field, determine its semantic type by reading its name carefully:

MONETARY FIELDS — any field that represents money or value:
- Names like: amount, price, total, fee, cost, credit, debit, balance,
  charge, rate, salary, budget, revenue, tax, discount, tip, fare
- Test: zero value → expect 400
- Test: negative value → expect 400
- Test: extremely large value → expect 400

FILE FIELDS — any field related to file upload:
- Names like: file_name, filename, file_type, file_size, filesize,
  mime_type, content_type, extension, attachment, upload_size
- Test: unsupported MIME type like exe/application → expect 400/415
- Test: file size = 0 → expect 400
- Test: file size = 999999999 (too large) → expect 400/413
- Test: negative file size → expect 400

EMAIL FIELDS — any field that holds an email address:
- Names like: email, email_address, user_email, contact_email,
  from_email, to_email, reply_to
- Test: invalid format like notanemail → expect 400/422
- Test: non-existent email where relevant → expect 401/404

PASSWORD FIELDS — any field for authentication secret:
- Names like: password, pass, passwd, secret, pin, passcode
- Test: weak password like "123" → expect 400
- Test: too short like "ab" → expect 400

ENUM FIELDS — any field with limited allowed values:
- Names like: status, type, role, category, method, mode, plan,
  tier, level, gender, payment_method, currency, language, timezone,
  product_type, file_type, notification, permission
- Test: a clearly invalid value for that type → expect 400/422
- Example: payment_method → try "crypto_barter"
- Example: file_type → try "exe/application"
- Example: language → try "xx-ZZ"
- Example: timezone → try "Mars/Olympus"

ID FIELDS — any field referencing a resource:
- Names like: id, user_id, product_id, order_id, cart_id,
  folder_id, parent_id, reference_id, uuid
- Test: non-existent id like 99999 → expect 404
- Test: invalid format like "abc-xyz" → expect 400/422

DATE / TIME FIELDS — any field for dates or times:
- Names like: date, time, datetime, created_at, expires_at,
  start_date, end_date, due_date, scheduled_at, birth_date
- Test: past date when future expected → expect 400
- Test: invalid format like "31-13-2024" → expect 400/422

NUMERIC FIELDS — any field with a number:
- Names like: quantity, count, stock, age, limit, page,
  duration, length, width, height, weight, capacity
- Test: negative value → expect 400
- Test: zero when not allowed → expect 400
- Test: extremely large value when relevant → expect 400

APPLY THIS ANALYSIS BEFORE GENERATING ANY SCENARIO.
Every field must be classified and tested appropriately.
Do not rely on a fixed list — use your understanding of the field name.
"""


def _get_naming_rules() -> str:
    return """
FUNCTION NAMING RULE — MANDATORY:
- NEVER use "apiHelperFunction" as the function name
- Derive a specific descriptive camelCase function name from the endpoint

STEP 1 — CHECK IF THE ENDPOINT RETRIEVES SOMETHING:
Before applying any verb pattern, ask: does this endpoint RETURN something that already exists
or gets GENERATED (a URL, token, link, redirect, OTP, code)?
If YES → always use "get" prefix, regardless of HTTP method.
  POST /sd/pre-url        → getPresignedUrl     (returns a generated URL)
  POST /auth/token        → getToken            (returns a generated token)
  POST /sd/download-url   → getDownloadUrl      (returns a generated URL)
  POST /otp/generate      → getOtp              (returns a generated code)
If NO → proceed to Step 2.

STEP 2 — APPLY VERB BY METHOD:
  GET    → get, fetch, list, search
  POST   → create, add, upload, send, submit, register, login, checkout
  PUT    → update, replace
  PATCH  → update, patch
  DELETE → delete, remove

- Common examples:
  POST /sd/pre-url              → getPresignedUrl
  POST /api/auth/login          → loginUser
  POST /api/users/register      → registerUser
  DELETE /api/posts/:id         → deletePost
  GET /api/users/:id            → getUserById
  GET /api/products/search      → searchProducts
  PATCH /api/settings           → updateSettings
  PUT /user/profile             → updateUserProfile
  POST /api/orders              → createOrder
  POST /api/payments            → processPayment
  POST /api/checkout            → checkout
  POST /api/files/upload        → uploadFile
  POST /api/media/upload        → uploadMedia
  POST /auth/forgot-password    → forgotPassword
  POST /auth/reset-password     → resetPassword
  POST /api/wallet/topup        → topupWallet
  POST /api/kyc/verify          → verifyKyc
  POST /api/invoices            → createInvoice
  GET /api/reports              → getReports
  GET /api/dashboard            → getDashboard

- If no pattern matches: read the last meaningful path segment
  and combine with the HTTP method to create a logical name

AUTH TOKEN RULE — MANDATORY:
- NEVER hardcode 'Bearer token_here' or any fake token string
- ALWAYS use 'auth' as the auth parameter for authenticated endpoints
- For no-auth scenarios pass null
- Correct positive: 'auth'
- Correct negative: null

RESPONSE PROPERTY RULE — MANDATORY:
- Do NOT guess from a fixed list
- Read the endpoint name and determine what a real backend would return
- Use your understanding of the API purpose:
  presigned URL API      → url (and it should start with https)
  login API              → token or access_token (string)
  register API           → id (the new resource id)
  file upload API        → file_id or url
  order/checkout API     → order_id
  payment API            → transaction_id
  profile update API     → updated_at
  search/list API        → items or results array
  single GET API         → id and resource fields
  forgot-password API    → message string
  any creation API       → id of created resource

RESPONSE ASSERTION STRENGTH RULE — MANDATORY:
- Always add TWO assertions for valid scenario response:
  1. Property exists:  expect(res.body).to.have.property('url')
  2. Value check:      expect(res.body.url).to.include('https')

- Assertion by type:
  url property      → .to.include('https')
  token/string      → .to.be.a('string')
  id property       → .to.exist
  array property    → .to.be.an('array')
  message property  → .to.be.a('string')
"""


def _get_scenario_rules() -> str:
    return """
SCENARIO ORDER — STRICTLY FOLLOW THIS ORDER ALWAYS:
Step 1 → Valid Request              (always first)
Step 2 → Empty Fields               (always if body exists)
Step 3 → Null Values                (always if 2+ fields)
Step 4 → Missing Body               (always for POST/PUT/PATCH)
Step 5 → Missing Required Field     (always if 2+ body fields)
Step 6 → Field-specific scenarios   (from field analysis — NEVER skip)
Step 7 → No Auth Token              (always last if auth required)

NONE of steps 1-5 are optional.
Step 6 is also NON-OPTIONAL — if field analysis finds any classified field type,
at least one field-specific scenario MUST be generated.

SCENARIO COUNT RULE:
- Base scenarios (1–5) = always included
- Step 6 adds AT LEAST 1 scenario per field type found
- Step 7 adds 1 scenario if auth is required
- Total = base + field-specific + auth
- Do NOT stop at 5 if field analysis found file, monetary, email, enum, or other typed fields

═══════════════════════════════════════════

BASE SCENARIOS — NEVER SKIP ANY:

SCENARIO 1 — Valid Request
- Call helper function with NO arguments
- Auth = 'auth' if required
- TWO assertions: property check + value/type check
- cy.log(JSON.stringify(res.body)) MUST be last line

STATUS CODE SELF-CHECK — do this before writing Scenario 1:
  Ask: what is the HTTP method?
  POST (creates or retrieves) → eq(201)   ← default for ALL POST endpoints
  GET                         → eq(200)
  PUT                         → eq(200)
  PATCH                       → eq(200)
  DELETE                      → eq(200) or eq(204)
  If you wrote eq(200) for a POST endpoint — that is WRONG. Change it to eq(201).

SCENARIO 2 — Empty Fields
- All string fields = ""
- All number fields = ""  ← use empty string "", NOT zero (0 may be a valid value)
- All fields must be set to "" — the goal is to send invalid types, not valid-but-empty values
- failOnStatusCode = false
- Expected: 400 or 422
- cy.log(JSON.stringify(res.body)) MUST be last line

SCENARIO 3 — Null Values
- All fields = null
- failOnStatusCode = false
- Expected: 400 or 422
- cy.log(JSON.stringify(res.body)) MUST be last line

SCENARIO 4 — Missing Body (POST/PUT/PATCH only)
- Send completely empty body {}
- Use direct apiRequest() — NOT helper function
- Pass 'auth' for auth
- failOnStatusCode = false
- Expected: 400 or 422
- cy.log(JSON.stringify(res.body)) MUST be present

SCENARIO 5 — Missing Required Field (if 2+ body fields)
- Pick the most critical field
- Build body WITHOUT that field — do not use undefined or null
- Use direct apiRequest() with field completely absent
- failOnStatusCode = false
- Expected: 400 or 422
- cy.log(JSON.stringify(res.body)) MUST be present

═══════════════════════════════════════════

FIELD-SPECIFIC SCENARIOS — FROM ANALYSIS:

Generate one scenario per field type found in the body.
Use the FIELD ANALYSIS rules to determine what to test.
Do not skip any field type — test every classification found.

Examples of field-specific scenarios:
- monetary field found → zero amount scenario + negative amount scenario
- file field found     → oversized file + zero size + invalid MIME
- email field found    → invalid email format scenario
- password field found → weak password scenario
- enum field found     → invalid enum value scenario
- date field found     → invalid date format scenario
- numeric field found  → negative value scenario

═══════════════════════════════════════════

ENDPOINT-BASED SCENARIOS:

IF endpoint contains "register" or "signup":
- Auth: PUBLIC — no token, only overrideBody and failOnStatusCode params
- Add: Duplicate email → 409
- Add: Weak password → 400

IF endpoint contains "login":
- Auth: PUBLIC — no token, only overrideBody and failOnStatusCode params
- Add: Wrong password → 401
- Add: Non-existent email → 401 or 404

IF endpoint contains "forgot-password" or "reset-password":
- Auth: PUBLIC — no token
- Add: Invalid email format → 400/422
- Add: Non-existent email → 200 or 404

IF endpoint contains "delete" or method is DELETE:
- No request body needed
- Add: Resource not found (id = 99999) → 404
- Add: Already deleted (call twice) → 404

IF method is GET with URL param (/:id):
- No body scenarios needed
- Generate: valid → not found → invalid id format → no auth

IF params contain "limit" or "page":
- Add: limit too large (99999) → 400 or capped
- Add: page negative (-1) → 400

IF method is PUT or PATCH:
- Expected success: 200 not 201
- Expected response property: updated_at

AUTH DETECTION:
- register, signup, login, forgot-password, reset-password → PUBLIC
- All others with auth mentioned → use 'auth'
- No auth mentioned → null
"""


def _get_cypress_output_rules() -> str:
    return """
// ============================================
// API HELPER FUNCTION
// ============================================

export const [descriptiveFunctionName] = (
    overrideBody = {},
    failOnStatusCode = true
) => {
    return getData().then((data) => {
        return apiRequest(
            'METHOD',
            '/endpoint',
            {
                field1: data.[inferredNamespace].field1,
                field2: data.[inferredNamespace].field2,
                // inferredNamespace = logical resource name derived from the endpoint path
                // e.g. /api/orders → data.order.field1
                // e.g. /api/auth/login → data.auth.field1
                // NEVER use flat data.field1 — always data.[namespace].field1
                // NEVER add || fallback values
                ...overrideBody
            },
            'auth',
            {},
            failOnStatusCode
        )
    })
}

// DATA ACCESS PATTERN RULE — MANDATORY:
//
// CORRECT:   data.[namespace].fieldName
// WRONG:     data.fieldName
// WRONG:     data.fieldName || 'fallback'
// WRONG:     data.fieldName !== undefined ? data.fieldName : 1024
//
// The namespace is derived from the resource domain of the endpoint.
// It is NOT a fixed value — infer it from the endpoint path:
//   /sd/pre-url            → data.fileUpload.field   or data.presignedUrl.field
//   /api/auth/login        → data.auth.field
//   /api/users/register    → data.user.field
//   /api/orders            → data.order.field
//   /api/payments          → data.payment.field
//   /api/products          → data.product.field
//   /api/wallet/topup      → data.wallet.field
//
// Rules:
// 1. ALWAYS use data.[namespace].fieldName — never flat data.fieldName
// 2. NEVER add || fallback values of any kind — fixture provides real values
// 3. NEVER use ternary fallbacks like field !== undefined ? field : default
// 4. NEVER hardcode a specific project namespace from training data
// 5. Infer namespace from the endpoint path — use the resource noun

// ============================================
// TEST SCENARIOS
// ============================================

describe('METHOD /endpoint', () => {

    // SCENARIO 1 — Valid Request
    it('should successfully [action] with valid data', () => {
        [descriptiveFunctionName]()
        .then((res) => {
            expect(res.status).to.eq(201) // POST → 201 always | GET/PUT/PATCH → 200 | DELETE → 200 or 204
            expect(res.body).to.have.property('property_name')
            expect(res.body.property_name).to.include('https') // or .to.be.a('string') etc
            cy.log(JSON.stringify(res.body))
        })
    })

    // SCENARIO 2 — Empty Fields
    it('should return 400 when all fields are empty strings', () => {
        [descriptiveFunctionName]({ field1: "", field2: "" }, false)
        .then((res) => {
            expect(res.status).to.be.oneOf([400, 422])
            cy.log(JSON.stringify(res.body))
        })
    })

    // SCENARIO 3 — Null Values
    it('should return 400 when all fields are null', () => {
        [descriptiveFunctionName]({ field1: null, field2: null }, false)
        .then((res) => {
            expect(res.status).to.be.oneOf([400, 422])
            cy.log(JSON.stringify(res.body))
        })
    })

    // SCENARIO 4 — Missing Body
    it('should return 400 when body is completely empty', () => {
        apiRequest('METHOD', '/endpoint', {}, 'auth', {}, false)
        .then((res) => {
            expect(res.status).to.be.oneOf([400, 422])
            cy.log(JSON.stringify(res.body))
        })
    })

    // SCENARIO 5 — Missing Required Field
    it('should return 400 when required field is absent', () => {
        apiRequest('METHOD', '/endpoint', {
            field2: 'realistic_value'
            // field1 intentionally absent
        }, 'auth', {}, false)
        .then((res) => {
            expect(res.status).to.be.oneOf([400, 422])
            cy.log(JSON.stringify(res.body))
        })
    })

    // SCENARIO 6+ — Field specific (monetary, file, email, enum etc)
    it('should return 400 when [field] has invalid value', () => {
        [descriptiveFunctionName]({ field1: invalid_value }, false)
        .then((res) => {
            expect(res.status).to.be.oneOf([400, 415, 422])
            cy.log(JSON.stringify(res.body))
        })
    })

    // SCENARIO N — No Auth Token
    it('should return 401 when auth token is missing', () => {
        apiRequest('METHOD', '/endpoint', {
            field1: 'realistic_value',
            field2: 'realistic_value'
        }, null, {}, false)
        .then((res) => {
            expect(res.status).to.be.oneOf([401, 403])
            cy.log(JSON.stringify(res.body))
        })
    })

})

REMEMBER:
- cy.log(JSON.stringify(res.body)) LAST line in EVERY .then() block
- Scenario 1 helper function takes NO arguments
- getData().then() ALWAYS used — never replaced
- failOnStatusCode = false for ALL negative scenarios
- Auth ALWAYS 'auth' for positive — null for no-auth negative
- Public endpoints NEVER get auth in helper function
- Steps 1-5 are NEVER skipped
- Function name ALWAYS descriptive — NEVER apiHelperFunction
- TWO assertions in Scenario 1 — property check + value/type check
- Missing Required Field uses apiRequest() with field COMPLETELY ABSENT
- Field analysis drives Step 6 scenarios — cover every field type found
"""


def _get_python_output_rules() -> str:
    return """
# ============================================
# SCENARIO N — Title
# ============================================
# Description of what this scenario tests
# Expected Status: XXX
# ============================================

import requests

url = "..."
headers = { ... }
payload = { ... }

try:
    response = requests.METHOD(url, json=payload, headers=headers)
    response.raise_for_status()
    print("Status:", response.status_code)
    print("Response:", response.json())
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
"""