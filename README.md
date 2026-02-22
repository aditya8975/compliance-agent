# 🛡️ Autonomous SEBI Compliance Agent

> An AI-powered agent that monitors SEBI regulatory circulars 24/7, extracts compliance obligations using LLM, and auto-assigns tasks to teams — built to understand what funded Indian fintech startups like OnFinance AI ($4.2M raised) are solving.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20Llama%203.3%2070B-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![Cost](https://img.shields.io/badge/Cost-₹0%20Free-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 What Problem Does This Solve?

Every time SEBI (India's stock market regulator) releases a new circular, compliance teams at banks, mutual funds, and brokerages must:

- Manually check the SEBI website
- Read and interpret dense legal PDFs
- Figure out what the company must do, by when, and who is responsible
- Assign work to legal, compliance, and operations teams

**This takes hours. Every single time. For every circular.**

This agent does it all automatically in seconds.

---

## ✨ Features

- 🔄 **Autonomous Monitoring** — Wakes up every hour, checks SEBI website for new circulars
- 🧠 **AI-Powered Extraction** — Llama 3.3 70B reads actual circular PDFs and extracts obligations, deadlines, penalties
- 📋 **Auto Task Creation** — Creates tasks for compliance, legal, and ops teams with priorities
- 💾 **Memory** — Remembers processed circulars, never duplicates work
- 📊 **Live Dashboard** — Streamlit UI with metrics, filters, and export to JSON/CSV
- 💰 **Zero Cost** — Built entirely on free APIs and free hosting

---

## 🏗️ Architecture & Workflow

```
SEBI Website (sebi.gov.in)
         ↓
  SEBIScraper fetches new circulars
         ↓
  Filter — already processed? Skip
         ↓
  Fetch actual PDF/HTML content
         ↓
  Groq AI (Llama 3.3 70B) reads & extracts:
  • Key obligations
  • Deadlines
  • Penalties
  • Applicable entities
  • Affected departments
  • Impact level (HIGH/MEDIUM/LOW)
         ↓
  Auto-create 3 tasks per circular
  (Compliance Team / Legal Team / Ops Team)
         ↓
  Save state + Update Streamlit Dashboard
         ↓
  Wait 1 hour → Repeat
```

---

## 🛠️ Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| LLM Brain | Groq API — Llama 3.3 70B | ₹0 Free |
| Web Scraping | BeautifulSoup + Requests | ₹0 Free |
| PDF Extraction | PyPDF2 | ₹0 Free |
| UI Dashboard | Streamlit | ₹0 Free |
| Hosting | Streamlit Community Cloud | ₹0 Free |

**Total infrastructure cost: ₹0**

---

## 📁 Project Structure

```
compliance-agent/
├── autonomous_agent.py      # Main agent loop & orchestration
├── sebi_scraper.py          # SEBI website scraper & PDF fetcher
├── groq_extractor.py        # Groq LLM integration & requirement extraction
├── streamlit_app.py         # Streamlit dashboard UI
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Free Groq API key from [console.groq.com](https://console.groq.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/aditya8975/compilance-agent.git
cd compilance-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your Groq API key to .env
```

### Run Locally

```bash
# Run the Streamlit dashboard
streamlit run streamlit_app.py

# Or run the agent directly
python autonomous_agent.py
```

### Environment Variables

```env
GROQ_API_KEY=your_groq_api_key_here
MONITORING_INTERVAL=3600
LOG_LEVEL=INFO
```

---

## 📸 Demo

### Dashboard Overview
- Real-time compliance metrics
- Latest SEBI circulars with AI-extracted obligations
- Task management with priority levels
- Export reports as JSON or CSV

### What the AI Extracts from Each Circular
```json
{
  "circular_id": "SEBI/HO/OIAE/2024/001",
  "title": "Guidelines on Disclosure of Material Information",
  "key_obligations": [
    "Disclose material information within 30 minutes of board decision",
    "Appoint a dedicated compliance officer for disclosures"
  ],
  "deadline": "01-04-2024",
  "applicable_to": ["All Listed Entities"],
  "penalties": ["Fine up to ₹25 Crore", "Trading suspension"],
  "impact_level": "HIGH",
  "affected_departments": ["Compliance", "Legal", "Board Secretariat"]
}
```

---

## 🧠 Why This Is a Real AI Agent

Three things separate this from a plain script:

1. **Autonomous** — Runs continuously without human triggers
2. **Memory** — Tracks processed circulars in `.agent_state.json`, never duplicates work
3. **Action** — Doesn't just answer questions, actively creates tasks and reports

---

## 📈 Inspired By

This project was built to understand the problem space that funded Indian AI startups are solving:

- **OnFinance AI** — Raised $4.2M for BFSI compliance automation, built NeoGPT (fine-tuned on SEBI/RBI/IRDAI data) and 70+ compliance agents
- **ClearTax** — Tax and GST compliance automation
- **Setu** — Financial data APIs for Indian market

The key insight: the real moat for production systems is **domain-specific fine-tuned models** trained on decades of regulatory data — not general-purpose LLMs. This project is a starting point that demonstrates the agent architecture.

---

## 🔮 Roadmap

- [ ] Add RBI and IRDAI circular monitoring
- [ ] Fine-tune model on historical SEBI circulars
- [ ] Email/Slack notifications for high priority circulars
- [ ] Multi-language support (Hindi + English)
- [ ] Compliance scoring dashboard
- [ ] Integration with HRMS for task assignment

---

## 🤝 Contributing

Feel free to open issues and pull requests. Areas where contribution is welcome:
- Better SEBI scraping logic
- More regulatory sources
- Improved AI prompts for extraction accuracy
- UI enhancements

---

## 📝 License

MIT License — use freely for personal and commercial projects.

---

## 👨‍💻 Author

**Aditya** — Building in public, learning by doing.

Open to opportunities in AI/ML engineering at Indian startups working on agentic workflows, fintech, or compliance automation.

[LinkedIn](https://linkedin.com/in/adityakatare35) • [GitHub](https://github.com/aditya8975)

---

