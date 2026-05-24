# 🚀 APIForge

### AI-Powered API Code Generation, Execution and Repair

APIForge is an AI-powered developer tool that generates, executes, classifies and repairs API integration code using natural inputs or curl commands.

Built to simplify API integration workflows through intelligent code generation and agent-assisted debugging.

---

## ✨ Features

## Core Features

- Manual API input mode
- Smart Paste (curl parsing)
- API request validation
- Authentication handling
- AI-powered code generation
- Generated code execution
- Repair agent for failed code
- Download generated and repaired code

---

## 🧠 Agent Intelligence

APIForge is more than a code generator.

It includes agentic capabilities such as:

- Error classification
- Session-based repair memory
- Repair history viewer
- Privacy-safe repair tracking
- Technical error inspection
- Agent-assisted debugging workflow

---

## 🎨 UI Features

- Professional Streamlit interface
- Sidebar controls
- Tabs for Code / Execution / Repair
- Expandable input sections
- Cleaner execution UX
- Download buttons
- Smart Paste experience

---

## 🏗 Architecture

APIForge follows a modular agent workflow:

```text
Input
→ Parse
→ Validate
→ Build Prompt
→ Generate Code
→ Execute
→ Detect Error
→ Repair
→ Session Memory
```

---

## ⚙ Tech Stack

- Python
- Streamlit
- Google Gemini API
- Requests
- Modular architecture

---

## 📂 Project Structure

```text
APIForge/
│
├── app.py
├── main.py
├── config.py
├── parser.py
├── curl_parser.py
├── validator.py
├── auth_handler.py
├── prompt_builder.py
├── code_generator.py
├── executor.py
├── repair_agent.py
├── repair_memory.py
├── error_classifier.py
├── file_handler.py
├── requirements.txt
├── README.md
└── .env
```

---

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/lakeshkumarkhatri/APIForge.git
```

---

### 2. Move Into Project

```bash
cd APIForge
```

---

### 3. Create Virtual Environment

```bash
python -m venv venv
```

---

### 4. Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 6. Add Environment Variables

Create a `.env` file.

Add:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

---

### 7. Run APIForge

Streamlit UI:

```bash
streamlit run app.py
```

CLI version:

```bash
python main.py
```

---

## 🧪 Supported Workflows

## Manual Mode

APIForge supports:

- API URL
- HTTP Method
- Authentication
- Headers
- Query Parameters
- Request Body
- Response Format
- API Notes

---

## Smart Paste Mode

Paste curl commands and APIForge automatically:

- Parses curl
- Detects auth
- Extracts headers
- Extracts params
- Extracts request body
- Generates runnable code

Example:

```bash
curl --request GET \
--url "https://jsonplaceholder.typicode.com/posts?userId=1" \
--header "Accept: application/json"
```

---

## 🔧 Error Intelligence

APIForge classifies execution failures into human-readable categories.

Examples:

| Error Type | Classification |
|------------|---------------|
| DNS failure | 🌐 Connection Error |
| Invalid token | 🔐 Unauthorized |
| Timeout | ⏳ Timeout Error |
| JSON mismatch | 📄 JSON Parsing Error |
| HTTP failures | ⚠ HTTP Error |

---

## 🛠 Repair System

When execution fails:

```text
Run
→ Error Detection
→ Repair Agent
→ Repair History
→ Re-run
```

Repair history is:

- Session-based
- Privacy-safe
- Non-persistent across users

---

## 📸 Screenshots

Add screenshots here after deployment.

Suggested:

- Home UI
- Smart Paste Mode
- Generated Code
- Error Classification
- Repair Flow

---

## 🛣 Roadmap

### Current

✅ Code generation  
✅ Execution  
✅ Repair  
✅ Error intelligence  
✅ Session memory  
✅ UI polish  
✅ GitHub integration  

### Planned

- Auto-repair loop (V2)
- Deployment
- Smarter repair strategies
- Multi-model support
- Enhanced agent workflow

---

## 🤝 Contributing

Contributions, improvements and feedback are welcome.

Fork the repository and create a pull request.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Lakesh Kumar**

Built with Python, AI and curiosity.

---

# ⭐ Support

If you find APIForge useful, consider starring the repository.