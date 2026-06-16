from langgraph.graph import StateGraph, START, END
from state import AuditState
from agents.orchestrator import run_orchestrator
from agents.ast_parser import run_ast_parser
from agents.judge import run_compliance_judge
from agents.remediator import run_remediation_engineer
from tools.quality_gate import run_quality_gate

def build_graph():
    graph = StateGraph(AuditState)
    
    # Add nodes
    graph.add_node("Orchestrator", run_orchestrator)
    graph.add_node("AST_Parser_Agent", run_ast_parser)
    graph.add_node("Compliance_Judge_Agent", run_compliance_judge)
    graph.add_node("Remediation_Engineer_Agent", run_remediation_engineer)
    graph.add_node("Quality_Gate_Agent", run_quality_gate)
    
    # Add edges
    graph.add_edge(START, "Orchestrator")
    
    def route(state):
        next_step = state.get("next_step")
        
        # Hard stop if we hit validation limits to prevent LLM routing loops
        if state.get("validation_attempts", 0) >= 3:
            return END
            
        if next_step == "Complete":
            return END
        # Ensure it matches one of the expected nodes, otherwise go to END to prevent infinite loops on error
        valid_nodes = ["AST_Parser_Agent", "Compliance_Judge_Agent", "Remediation_Engineer_Agent", "Quality_Gate_Agent"]
        if next_step in valid_nodes:
            return next_step
        return END
        
    graph.add_conditional_edges(
        "Orchestrator",
        route,
        {
            "AST_Parser_Agent": "AST_Parser_Agent",
            "Compliance_Judge_Agent": "Compliance_Judge_Agent",
            "Remediation_Engineer_Agent": "Remediation_Engineer_Agent",
            "Quality_Gate_Agent": "Quality_Gate_Agent",
            END: END
        }
    )
    
    # All agents return to the Orchestrator to decide the next step
    graph.add_edge("AST_Parser_Agent", "Orchestrator")
    graph.add_edge("Compliance_Judge_Agent", "Orchestrator")
    graph.add_edge("Remediation_Engineer_Agent", "Orchestrator")
    graph.add_edge("Quality_Gate_Agent", "Orchestrator")
    
    return graph.compile()
