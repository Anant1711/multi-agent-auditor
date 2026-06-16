import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from utils import robust_invoke

class RoutingDecision(BaseModel):
    next_step: str = Field(description="The next agent or tool to invoke: 'AST_Parser_Agent', 'Compliance_Judge_Agent', 'Remediation_Engineer_Agent', 'Quality_Gate_Agent', or 'Complete'")
    payload_to_pass: str = Field(description="JSON string containing relevant state data to pass")

orchestrator_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Master Orchestrator for the Multi-Agent Technical Auditor System. 

Your goal is to coordinate a team of three specialized AI agents to audit code or text documents for compliance against a specific standard (e.g., MISRA C, OWASP Top 10, GDPR).

You must manage the conversation state using the following workflow loop:
1. Receive raw input and target compliance standards from the user.
2. Route the input to the AST_Parser_Agent to break down the syntax and isolate target blocks.
3. Pass the parsed output to the Compliance_Judge_Agent to flag exact violations.
4. If violations are found, route the findings to the Remediation_Engineer_Agent to generate a fix.
5. ROUTE TO QUALITY GATE: Pass the proposed fix back to the AST_Parser_Agent or local compilers/linters to verify validity (Quality_Gate_Agent).
6. If validation fails, route back to the Remediation_Engineer_Agent with the failure logs. Repeat up to 3 times max.
7. If validation passes, compile the final unified Audit Report for the user and return 'Complete'.

CRITICAL ROUTING RULES:
- If 'last_agent' was 'AST_Parser_Agent', you MUST route to 'Compliance_Judge_Agent'.
- If 'last_agent' was 'Compliance_Judge_Agent' and violations exist, you MUST route to 'Remediation_Engineer_Agent'. If no violations, return 'Complete'.
- If 'last_agent' was 'Remediation_Engineer_Agent', you MUST route to 'Quality_Gate_Agent' to verify the fix.
- If 'last_agent' was 'Quality_Gate_Agent' and validation failed, you MUST route to 'Remediation_Engineer_Agent'. HOWEVER, if 'validation_attempts' is 3 or more, return 'Complete' to prevent infinite loops.
- If 'last_agent' was 'Quality_Gate_Agent' and validation passed, return 'Complete'.

Current State Data:
{current_state_json}

Determine the next logical agent or tool to invoke."""),
    ("human", "Determine the next step based on the current state.")
])

def run_orchestrator(state: dict):
    model_name = state.get("selected_model", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    structured_llm = llm.with_structured_output(RoutingDecision)
    chain = orchestrator_prompt | structured_llm
    
    current_state_json = json.dumps(state, indent=2)
    decision = robust_invoke(chain, {"current_state_json": current_state_json})
    
    return {"next_step": decision.next_step, "payload_to_pass": decision.payload_to_pass}
