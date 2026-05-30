# 🚀 APIForge

### AI-Powered API Code Generation, Execution, Repair and Test Scenario Generation

APIForge is an AI-powered developer tool that generates, executes, classifies and repairs API integration code — and automatically generates professional Cypress and Python test scenarios from any API input.

Built to simplify API integration and testing workflows through intelligent code generation and agent-assisted debugging.

🌐 **Live App:** https://apiforge.streamlit.app

---

# ✨ Features

## Core Features

- Manual API input mode
- Smart Paste (curl parsing)
- API request validation
- Authentication handling
- AI-powered code generation
- Generated code execution
- Repair agent for failed code
- Download generated and repaired code
- Session-safe repair history

## Scenario Generator (New)

- Generate Cypress or Python test scenarios from any API input
- Accepts raw text, curl commands, plain English, mixed language
- Intelligent field type detection and analysis
- Auto-detects auth, endpoint, method and body fields
- Scoped fixture data pattern (`data.[resource].field`)
- Client instructions support for custom test style
- Download generated scenarios as `.cy.js` or `.py`

---

# 🧠 Agent Intelligence

APIForge is more than a code generator.

It includes agentic capabilities:

- Error classification
- Session-based repair memory
- Repair history viewer
- Privacy-safe repair tracking
- Technical error inspection
- Agent-assisted debugging workflow
- Universal API input parser
- Semantic field type analysis
- Instruction-aware scenario generation

---

# 🎨 UI Features

- Professional Streamlit interface
- Sidebar controls with client instruction panel
- Structured workflow sections
- Generated → Execute → Repair flow
- Scenario Generator mode
- Raw input and structured input modes
- Cypress and Python output toggle
- Expandable input sections
- Clean execution UX
- Download buttons
- Smart Paste workflow
- Repair history panel
- Technical error viewer

---

# 🏗 Architecture

APIForge follows a modular agent workflow:

```text
Input
→ Parse
→ Validate
→ Build Prompt
→ Generate Code
→ Execute
→ Detect Error
→ Classify Error
→ Repair
→ Session Repair History
```

Scenario Generator workflow:

```text
Raw Input (any format)
→ Python Parser (extracts endpoint, method, auth, fields)
→ Field Analysis (semantic type classification)
→ Client Instructions (applied if set)
→ Gemini Scenario Generation
→ Download as .cy.js or .py
```

---

# ⚙ Tech Stack

- Python
- Streamlit
- Google Gemini API
- Requests
- Modular architecture

---

# 📂 Project Structure

```text
APIForge/
│
├── app.py
├── main.py
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── Core/
│   ├── parser.py
│   ├── validator.py
│   ├── prompt_builder.py
│   ├── executor.py
│   ├── file_handler.py
│   ├── curl_parser.py
│   └── auth_handler.py
│
├── Agents/
│   ├── code_generator.py
│   ├── repair_agent.py
│   ├── repair_memory.py
│   └── error_classifier.py
│
├── Config/
│   └── config.py
│
├── Generated/
│   └── generated_code.py
│
└── Screenshots/
```

---

# 🚀 Getting Started

## 1. Clone Repository

```bash
git clone https://github.com/lakeshkumarkhatri/APIForge.git
```

## 2. Move Into Project

```bash
cd APIForge
```

## 3. Create Virtual Environment

```bash
python -m venv venv
```

## 4. Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## 6. Add Environment Variables

Create a `.env` file and add:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

## 7. Run APIForge

### Streamlit UI

```bash
streamlit run app.py
```

### Core Engine

```bash
python main.py
```

---

# 🌐 Live Deployment

APIForge is deployed on Streamlit Cloud.

Live URL: https://apiforge.streamlit.app

---

# 🧪 Supported Workflows

## Manual Mode

- API URL
- HTTP Method
- Authentication
- Headers
- Query Parameters
- Request Body
- Response Format
- API Notes

## Smart Paste Mode

Paste curl commands and APIForge automatically:

- Parses curl
- Detects authentication
- Extracts headers
- Extracts parameters
- Extracts request body
- Generates runnable code

Example:

```bash
curl --request GET \
--url "https://jsonplaceholder.typicode.com/posts?userId=1" \
--header "Accept: application/json"
```

## Scenario Generator Mode

Paste anything — API docs, curl, plain English, mixed language — and APIForge generates complete test scenarios.

Example input formats:

```text
POST /api/orders | auth
Request body: { "product_id": "string", "quantity": 0 }
```

```bash
curl -X POST https://api.example.com/users/register \
-d '{"email":"test@example.com","password":"pass123"}'
```

```text
// ye API karna hai login ke liye
POST /auth/login
body: email aur password chahiye
```

Generated output includes:

- Helper function with `overrideBody` pattern
- Scoped fixture data access (`data.[resource].field`)
- Valid request scenario
- Empty fields scenario
- Null values scenario
- Missing body scenario
- Missing required field scenario
- Field-specific scenarios (email, enum, numeric, date, file, monetary)
- No auth scenario

---

# 📋 Client Instructions Panel

Set generation guidance in the sidebar that applies to every scenario generated.

Examples:

```text
Keep tests concise
One field-specific invalid only
Focus on request contract
Avoid duplicate validations
```

Instructions are session-based and cleared on browser refresh.

---

# 🔧 Error Intelligence

APIForge classifies execution failures into readable categories.

| Error Type | Classification |
|---|---|
| DNS Failure | 🌐 Connection Error |
| Invalid Token | 🔐 Unauthorized |
| Timeout | ⏳ Timeout Error |
| JSON Mismatch | 📄 JSON Parsing Error |
| HTTP Failure | ⚠ HTTP Error |

---

# 🛠 Repair System

When execution fails:

```text
Run
→ Error Detection
→ Error Classification
→ Repair Agent
→ Repair History
→ Re-run
```

Repair history is session-based, privacy-safe, and cleared after session ends.

---

# 🧬 Scenario Generation Intelligence

APIForge analyses each field in the request body semantically:

| Field Type | Examples | Test Generated |
|---|---|---|
| Email | email, user_email | Invalid format |
| Password | password, passcode | Weak password |
| Monetary | amount, price, total, fee | Zero + negative |
| File | file_name, file_size, file_type | Invalid MIME + oversized + zero |
| Enum | status, type, role, ticket_type | Invalid enum value |
| Numeric | quantity, age, count, attendee_count | Negative value |
| Date | start_date, check_in_date | Invalid format |
| ID | event_id, product_id, user_id | Non-existent ID |

---

# 📸 Screenshots

### Home UI
![Home UI](Screenshots/Home%20UI.png)

### Manual Mode
![Manual Mode](Screenshots/Manual%20Mode.png)

### Smart Paste Mode
![Smart Paste](Screenshots/Smart%20Paste%20Mode.png)

### Scenario Generator
![Scenario Generator](Screenshots/Scenario%20Generator.png)

### Client Instructions Panel
![Client Instructions](Screenshots/Client%20Instructions.png)

### Generated Code
![Generated Code](Screenshots/Generated%20Code.png)

### Error Classification
![Error Classification](Screenshots/Error%20Classification.png)

### Repair Flow
![Repair Flow](Screenshots/Repair%20Flow.png)

### Repair History
![Repair History](Screenshots/Repair%20History.png)

---

# 🛣 Roadmap

## V1 — Completed

✅ Code generation
✅ Execution
✅ Repair agent
✅ Error classification
✅ Session repair history
✅ Smart Paste
✅ UI polish
✅ GitHub integration
✅ Live Streamlit deployment

## V2 — Completed

✅ Scenario Generator mode
✅ Cypress test generation
✅ Python test generation
✅ Universal input parser
✅ Semantic field type analysis
✅ Scoped fixture data pattern
✅ Client instructions panel
✅ Auth-aware scenario generation
✅ Instruction-compliant output

## V3 — Planned

- Auto-repair loop
- Smarter repair strategies
- Multi-model support
- Enhanced agent workflows
- Scenario history and versioning
- Team collaboration features

---

# 🤝 Contributing

Contributions, improvements and feedback are welcome.

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open pull request

---

# 📜 License

MIT License — see `LICENSE` file for details.

---

# 👨‍💻 Author

**Lakesh Kumar**

Built with Python, AI and curiosity.

---

# ⭐ Support

If you find APIForge useful, consider starring the repository.