# 🕵️‍♂️ Multi-Agent AI Code Auditor

An advanced AI-powered technical auditing system that uses a multi-agent workflow to analyze source code for compliance violations (e.g., MISRA C:2012) and automatically generate remediations. Built with LangGraph, LangChain, Google Gemini API, and Streamlit.

## 🌟 Features

- **Agentic Workflow:** Orchestrates specialized AI agents (AST Parser, Compliance Judge, Remediation Engineer, Quality Gate) using LangGraph to evaluate code iteratively.
- **Self-Healing Code:** Automatically parses static analysis violations, generates syntax-level patches, and strictly validates them against a simulated quality gate to prevent regressions.
- **Interactive Web UI:** Clean, responsive Streamlit dashboard for uploading source code, dynamically configuring LLM parameters, and viewing the live state-machine execution.
- **PDF Reporting:** Automatically compiles findings, diffs, and compliance judgements into a downloadable, professional PDF technical report.
- **Dynamic Model Selection:** Switch seamlessly between Google Gemini models (e.g., `gemini-1.5-pro`, `gemini-2.5-flash`) via the UI.

## 🛠️ Tech Stack

- **Python 3.10+**
- **LangGraph & LangChain:** For defining the multi-agent state graph and LLM orchestration.
- **Google GenAI / Gemini API:** Powering the specialized reasoning of each agent node.
- **Streamlit:** Frontend dashboard.
- **fpdf2:** Generating automated compliance reports.

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Anant1711/multi-agent-auditor.git
cd multi-agent-auditor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
The application requires a Google Gemini API Key. You can either:
- Create a `.env` file in the root directory and add: `GOOGLE_API_KEY=your_api_key_here`
- OR enter the API key directly in the sidebar of the Streamlit Web UI.

### 4. Run the Application
```bash
streamlit run ui.py
```
This will launch the web server. Navigate to `http://localhost:8501` in your browser.

## 🧠 System Architecture

The workflow is managed by a central **Orchestrator** node that routes code through the following agents:
1. **AST Parser Agent**: Breaks down large files into logical, testable blocks.
2. **Compliance Judge Agent**: Scans blocks against configured standards (e.g., MISRA C) and flags precise violations.
3. **Remediation Engineer Agent**: Synthesizes `git diff`-style code patches to resolve the violations without altering business logic.
4. **Quality Gate Agent**: Validates the patched code to ensure zero new warnings are introduced, acting as a strict feedback loop.

## 📄 License

This project is open-source and available under the MIT License.
