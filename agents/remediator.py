import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from utils import robust_invoke

class ProposedFix(BaseModel):
    block_signature: str = Field(description="The signature of the block being fixed")
    diff: str = Field(description="A clean unified diff (git diff format) showing exactly what lines to delete and what lines to insert")
    explanation: str = Field(description="Brief explanation of the fix")

class RemediationOutput(BaseModel):
    fixes: list[ProposedFix]

remediator_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Remediation Engineer Agent. Your task is to fix the compliance violations identified by the Compliance_Judge_Agent without changing the core business logic or functionality of the original code.

Instructions:
- Review the original code block and the accompanying violation report.
- Rewrite the violating code segment to be 100% compliant with {target_standard}.
- Ensure your code rewrite fixes memory leaks, type safety issues, or security flaws while maintaining optimal execution performance.
- Provide a clean unified diff (`git diff` format) showing exactly what lines to delete and what lines to insert.

Constraints:
- Do not introduce new dependencies or external libraries unless explicitly required by the standard.
- The output code block must be fully standalone and ready to pass through a strict linter/compiler quality gate.

Parsed Blocks (Context):
{parsed_blocks}

Violation Report:
{violations}

Previous Validation Logs (If you failed a previous attempt, FIX these errors!):
{validation_logs}"""),
    ("human", "Generate the fixes for the violations.")
])

def run_remediation_engineer(state: dict):
    model_name = state.get("selected_model", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    structured_llm = llm.with_structured_output(RemediationOutput)
    chain = remediator_prompt | structured_llm
    
    parsed_blocks_json = json.dumps(state.get("parsed_blocks", []), indent=2)
    violations_json = json.dumps(state.get("violations", []), indent=2)
    validation_logs = state.get("validation_logs", "None")
    
    result = robust_invoke(chain, {
        "target_standard": state.get("target_standard", "Standard"),
        "parsed_blocks": parsed_blocks_json,
        "violations": violations_json,
        "validation_logs": validation_logs
    })
    
    fixes = [f.dict() for f in result.fixes]
    return {"proposed_fixes": fixes, "last_agent": "Remediation_Engineer_Agent"}
