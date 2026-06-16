from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from utils import robust_invoke

class ParsedBlock(BaseModel):
    block_type: str = Field(description="Type of the block, e.g., 'function', 'struct', 'assignment'")
    start_line: int = Field(description="Starting line number")
    end_line: int = Field(description="Ending line number")
    signature: str = Field(description="Identified signature or name")
    content: str = Field(description="The actual code content of the block")

class ASTParserOutput(BaseModel):
    blocks: list[ParsedBlock]

ast_parser_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the AST (Abstract Syntax Tree) & Structural Parser Agent. 

Your objective is to ingest raw source code or data payloads, break them down into functional blocks, and extract critical structural metadata.

Instructions:
- Strip away irrelevant components (e.g., boilerplate code, basic comments) that do not impact logical compliance.
- Isolate functions, data structures, type castings, pointer assignments, or configuration objects.
- Map out line numbers and token relationships accurately.
- Target compliance scope: Focus intensely on structural anomalies related to {target_standard}.

Raw Input Code:
{raw_input}"""),
    ("human", "Parse the structural components and return the mapping.")
])

def run_ast_parser(state: dict):
    model_name = state.get("selected_model", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    structured_llm = llm.with_structured_output(ASTParserOutput)
    chain = ast_parser_prompt | structured_llm
    
    result = robust_invoke(chain, {
        "target_standard": state.get("target_standard", "Standard"),
        "raw_input": state.get("raw_input", "")
    })
    
    # Convert Pydantic objects to dicts for the LangGraph state
    parsed_blocks = [block.dict() for block in result.blocks]
    return {"parsed_blocks": parsed_blocks, "last_agent": "AST_Parser_Agent"}
