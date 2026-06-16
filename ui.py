import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from graph import build_graph
import time
from fpdf import FPDF, XPos, YPos
import io

load_dotenv()

st.set_page_config(page_title="Multi-Agent Auditor", layout="wide")

@st.cache_data
def get_available_models(api_key):
    try:
        # If no key, we can't fetch models
        if not api_key:
            return ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
            
        client = genai.Client(api_key=api_key)
        models = []
        for m in client.models.list():
            # LangChain ChatGoogleGenerativeAI prefers model name without 'models/' prefix 
            # though it supports both. We'll strip it for cleaner UI.
            name = m.name.replace("models/", "")
            models.append(name)
        return models if models else ["gemini-2.5-flash", "gemini-1.5-pro"]
    except Exception as e:
        return ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

st.title("🛡️ Multi-Agent Technical Auditor System")

# Sidebar
st.sidebar.header("Configuration")

# Add API Key input
user_api_key = st.sidebar.text_input("Google API Key", type="password", value=os.environ.get("GOOGLE_API_KEY", ""))
if user_api_key:
    os.environ["GOOGLE_API_KEY"] = user_api_key

available_models = get_available_models(user_api_key)
default_ix = available_models.index("gemini-2.5-flash") if "gemini-2.5-flash" in available_models else 0
selected_model = st.sidebar.selectbox("Select Gemini Model", available_models, index=default_ix)

standard_choice = st.sidebar.selectbox(
    "Target Standard",
    ["MISRA C:2012", "OWASP Top 10", "GDPR", "AUTOSAR C++14", "Custom"]
)
if standard_choice == "Custom":
    target_standard = st.sidebar.text_input("Enter Custom Standard", "My Standard")
else:
    target_standard = standard_choice

# Main Area
st.subheader("Source Code to Audit")

uploaded_files = st.file_uploader("Upload files (optional)", accept_multiple_files=True)

code_input = ""
if uploaded_files:
    for file in uploaded_files:
        content = file.read().decode("utf-8", errors="replace")
        code_input += f"\n--- File: {file.name} ---\n{content}\n"
    st.info(f"Loaded {len(uploaded_files)} file(s).")
else:
    default_code = """#include <stdio.h>
#include <stdlib.h>

void process_data(int *data) {
    if (data == NULL) return;
    
    // MISRA Violation: dynamic memory allocation (Rule 21.3)
    int *buffer = (int*)malloc(10 * sizeof(int));
    
    // MISRA Violation: pointer arithmetic (Rule 18.4)
    buffer = buffer + 1;
    
    // MISRA Violation: unsafe casting
    float f = (float)(*data);
    
    printf("Processed %f\\n", f);
}

int main() {
    int val = 42;
    process_data(&val);
    return 0;
}
"""
    code_input = st.text_area("Or Input Code Manually", default_code, height=300)

if st.button("Start Audit"):
    st.divider()
    st.subheader("Audit Progress")
    
    # Initialize graph
    workflow = build_graph()
    initial_state = {
        "raw_input": code_input,
        "target_standard": target_standard,
        "selected_model": selected_model,
        "parsed_blocks": [],
        "violations": [],
        "proposed_fixes": [],
        "validation_logs": "",
        "validation_attempts": 0,
        "validation_passed": False,
        "next_step": "",
        "payload_to_pass": "",
        "final_report": "",
        "last_agent": "None"
    }
    
    # Create placeholders for dynamic updates
    progress_bar = st.progress(0, text="Initializing Audit...")
    progress_container = st.container()
    current_progress = 0
    final_state = {}
    
    with st.spinner("Auditing..."):
        for output in workflow.stream(initial_state, {"recursion_limit": 30}):
            for node_name, state_update in output.items():
                final_state.update(state_update)
                
                # Update progress bar
                current_progress = min(current_progress + 12, 95)
                progress_bar.progress(current_progress, text=f"Active Agent: {node_name.replace('_Agent', '').replace('_', ' ')}")
                
                with progress_container:
                    if node_name == "Orchestrator":
                        st.markdown(f"**🤖 Orchestrator**: Routing to `{state_update.get('next_step')}`")
                    elif node_name == "AST_Parser_Agent":
                        blocks = state_update.get("parsed_blocks", [])
                        st.markdown(f"**🧩 AST Parser**: Parsed `{len(blocks)}` structural blocks.")
                    elif node_name == "Compliance_Judge_Agent":
                        violations = state_update.get("violations", [])
                        st.markdown(f"**⚖️ Compliance Judge**: Found `{len(violations)}` violations.")
                        for v in violations:
                            st.error(f"Line {v.get('lines')} | {v.get('rule_id')}: {v.get('justification')}")
                    elif node_name == "Remediation_Engineer_Agent":
                        fixes = state_update.get("proposed_fixes", [])
                        st.markdown(f"**🛠️ Remediation Engineer**: Generated `{len(fixes)}` proposed fixes.")
                        for f in fixes:
                            st.code(f.get('diff'), language='diff')
                    elif node_name == "Quality_Gate_Agent":
                        passed = state_update.get("validation_passed", False)
                        if passed:
                            st.success(f"**✅ Quality Gate**: Validation Passed!")
                        else:
                            st.warning(f"**❌ Quality Gate**: Validation Failed. Routing back to remediation.")
                            st.text(state_update.get("validation_logs", ""))
                
                # Sleep to prevent rapid free-tier quota exhaustion
                time.sleep(10)
        
    progress_bar.progress(100, text="Audit Complete!")
    st.balloons()
    st.success("Audit Complete!")
    
    # Generate PDF Report
    try:
        import textwrap
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=16, style='B')
        pdf.cell(200, 10, text="Multi-Agent Technical Audit Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, text=f"Standard: {target_standard}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(10)
        
        violations = final_state.get("violations", [])
        fixes = final_state.get("proposed_fixes", [])
        
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(200, 10, text=f"Violations Found ({len(violations)}):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=10)
        for v in violations:
            raw_text = f"- Line {v.get('lines')} [{v.get('rule_id')}]: {v.get('justification')}"
            safe_text = raw_text.encode('latin-1', 'replace').decode('latin-1')
            wrapped_lines = textwrap.wrap(safe_text, width=90)
            for wline in wrapped_lines:
                pdf.cell(0, 6, text=wline, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(3)
            
        pdf.ln(5)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(200, 10, text=f"Proposed Fixes ({len(fixes)}):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Courier", size=9)
        for f in fixes:
            sig_text = f"Signature: {f.get('block_signature')}".encode('latin-1', 'replace').decode('latin-1')
            for wline in textwrap.wrap(sig_text, width=90):
                pdf.cell(0, 5, text=wline, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            diff_text = f.get('diff', '').encode('latin-1', 'replace').decode('latin-1')
            for line in diff_text.split('\n'):
                # Truncate rather than wrap diffs so the code remains readable
                safe_line = line[:100] + "..." if len(line) > 100 else line
                pdf.cell(0, 5, text=safe_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            
        pdf_bytes = pdf.output()
        
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="audit_report.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Failed to generate PDF: {e}")
