import argparse
import os
from dotenv import load_dotenv
from graph import build_graph

# Example buggy C code to test MISRA C compliance
SAMPLE_CODE = """
#include <stdio.h>
#include <stdlib.h>

void process_data(int *data) {
    if (data == NULL) return;
    
    // MISRA Violation: dynamic memory allocation
    int *buffer = (int*)malloc(10 * sizeof(int));
    
    // MISRA Violation: pointer arithmetic
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

def main():
    load_dotenv()
    
    if "GOOGLE_API_KEY" not in os.environ:
        print("Please set GOOGLE_API_KEY in your environment or .env file")
        return

    parser = argparse.ArgumentParser(description="Multi-Agent Technical Auditor System")
    parser.add_argument("--file", type=str, help="Path to the file to audit. If not provided, a sample will be used.")
    parser.add_argument("--standard", type=str, default="MISRA C:2012", help="The compliance standard to audit against.")
    args = parser.parse_args()

    raw_input = SAMPLE_CODE
    if args.file:
        try:
            with open(args.file, "r") as f:
                raw_input = f.read()
        except Exception as e:
            print(f"Error reading file {args.file}: {e}")
            return

    # Initialize graph and state
    workflow = build_graph()
    
    initial_state = {
        "raw_input": raw_input,
        "target_standard": args.standard,
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

    print(f"Starting audit against {args.standard}...")
    print("-" * 50)
    
    # Stream the graph execution
    import time
    for output in workflow.stream(initial_state, {"recursion_limit": 30}):
        for node_name, state_update in output.items():
            print(f"--- Node Executed: {node_name} ---")
            if node_name == "Orchestrator":
                print(f"Decision: Routing to {state_update.get('next_step')}")
            elif node_name == "AST_Parser_Agent":
                blocks = state_update.get("parsed_blocks", [])
                print(f"Parsed {len(blocks)} structural blocks.")
            elif node_name == "Compliance_Judge_Agent":
                violations = state_update.get("violations", [])
                print(f"Found {len(violations)} violations.")
            elif node_name == "Remediation_Engineer_Agent":
                fixes = state_update.get("proposed_fixes", [])
                print(f"Generated {len(fixes)} proposed fixes.")
            elif node_name == "Quality_Gate_Agent":
                passed = state_update.get("validation_passed", False)
                print(f"Validation Passed: {passed}")
            
            # Sleep for 10 seconds to absolutely guarantee we stay under 20 RPM free tier
            time.sleep(10)

    print("-" * 50)
    print("Audit Complete.")
    
if __name__ == "__main__":
    main()
