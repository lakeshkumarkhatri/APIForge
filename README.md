# 🚀 APIForge

### AI-Powered API Code Generation, Execution and Repair

APIForge is an AI-powered developer tool that generates, executes, classifies and repairs API integration code using natural inputs or curl commands.

Built to simplify API integration workflows through intelligent code generation and agent-assisted debugging.

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

---

# 🧠 Agent Intelligence

APIForge is more than a code generator.

It includes agentic capabilities such as:

- Error classification
- Session-based repair memory
- Repair history viewer
- Privacy-safe repair tracking
- Technical error inspection
- Agent-assisted debugging workflow

---

# 🎨 UI Features

- Professional Streamlit interface
- Sidebar controls
- Structured workflow sections
- Generated → Execute → Repair flow
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

---

## 2. Move Into Project

```bash
cd APIForge
```

---

## 3. Create Virtual Environment

```bash
python -m venv venv
```

---

## 4. Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Add Environment Variables

Create a `.env` file.

Add:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

---

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

Live URL:

https://apiforge.streamlit.app

---

# 🧪 Supported Workflows

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

---

# 🔧 Error Intelligence

APIForge classifies execution failures into readable categories.

| Error Type | Classification |
|------------|---------------|
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

Repair history is:

- Session-based
- Privacy-safe
- Non-persistent across users
- Session-only storage
- No cross-user exposure
- Memory cleared after session ends

---

# 📸 Screenshots

### Home UI
![Home UI](Screenshots/Home%20UI.png)

### Manual Mode
![Manual Mode](Screenshots/Manual%20Mode.png)

### Smart Paste Mode
![Smart Paste](Screenshots/Smart%20Paste%20Mode.png)

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

## Current

✅ Code generation  
✅ Execution  
✅ Repair agent  
✅ Error classification  
✅ Session repair history  
✅ Smart Paste  
✅ UI polish  
✅ GitHub integration  
✅ Live Streamlit deployment  

## Planned

- Auto-repair loop (V2)
- Smarter repair strategies
- Multi-model support
- Enhanced agent workflows

---

# 🤝 Contributing

Contributions, improvements and feedback are welcome.

1. Fork repository  
2. Create feature branch  
3. Commit changes  
4. Open pull request  

---

# 📜 License

MIT License

See `LICENSE` file for details.

---

# 👨‍💻 Author

**Lakesh Kumar**

Built with Python, AI and curiosity.

---

# ⭐ Support

If you find APIForge useful, consider starring the repository.