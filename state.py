from typing import Annotated, TypedDict
import operator

class AuditState(TypedDict):
    # Input data
    raw_input: str
    target_standard: str
    selected_model: str
    
    # AST Parser output
    parsed_blocks: list[dict]
    
    # Compliance Judge output
    violations: list[dict]
    
    # Remediation Engineer output
    proposed_fixes: list[dict]
    
    # Quality Gate output
    validation_logs: str
    validation_attempts: int
    validation_passed: bool
    
    # Orchestrator routing output
    next_step: str
    payload_to_pass: str
    
    # Final Output
    final_report: str
    
    # Tracking
    last_agent: str
