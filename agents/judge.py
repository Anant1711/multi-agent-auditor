import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from utils import robust_invoke

class Violation(BaseModel):
    lines: str = Field(description="The exact line number(s)")
    rule_id: str = Field(description="The specific rule identifier (e.g., 'MISRA C:2012 Rule 11.3')")
    justification: str = Field(description="A technical justification detailing why this violates the standard")
    block_signature: str = Field(description="The signature of the block where the violation occurred")

class ComplianceOutput(BaseModel):
    violations: list[Violation]

judge_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Compliance Judge Agent. Your job is to strictly evaluate the parsed code structures against the rules defined by the {target_standard} specification.

You will be provided with:
1. Parsed structural blocks from the AST_Parser_Agent.
2. Contextual reference snippets retrieved via RAG from the {target_standard} documentation database. (MOCKED for this demo: Assume strict standard rules).

Rules of Engagement:
- You must analyze the code line-by-line for explicit violations.
- Do not assume intent; if a code block breaks a strict safety rule (such as unchecked pointer arithmetic or dynamic memory allocation in safety-critical systems), flag it.
- For every violation detected, you must provide the exact line number(s), rule identifier, and technical justification.

Parsed Blocks:
{parsed_blocks}"""),
    ("human", "Analyze the blocks and return any violations. Return an empty array if no violations are found.")
])

def run_compliance_judge(state: dict):
    model_name = state.get("selected_model", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    structured_llm = llm.with_structured_output(ComplianceOutput)
    chain = judge_prompt | structured_llm
    
    parsed_blocks_json = json.dumps(state.get("parsed_blocks", []), indent=2)
    
    result = robust_invoke(chain, {
        "target_standard": state.get("target_standard", "Standard"),
        "parsed_blocks": parsed_blocks_json
    })
    
    violations = [v.dict() for v in result.violations]
    return {"violations": violations, "last_agent": "Compliance_Judge_Agent"}
