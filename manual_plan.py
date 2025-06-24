import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from portia import (
    Config,
    LLMTool,
    PlanBuilder,
    Portia,
    PortiaToolRegistry,
    open_source_tool_registry,
)
from utils import Tee, get_product_details, get_manual_plan

AI_MODEL = "openai/gpt-4.1-nano"


def main():
    """Main function to run the market research agent with a manual plan."""
    load_dotenv()

    if not all(
        [
            os.getenv("PORTIA_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("TAVILY_API_KEY"),
        ]
    ):
        print("---")
        print("ERROR: Missing one or more required API keys in your .env file.")
        print("Please create a '.env' file in this directory with the following content:")
        print("PORTIA_API_KEY=your_key_here")
        print("OPENAI_API_KEY=your_key_here")
        print("TAVILY_API_KEY=your_key_here")
        print("---")
        sys.exit(1)

    product_details = get_product_details()
    query = f"Run a TAM/SAM analysis for the following product: {product_details['name']}"

    # --- Manually Build the Plan using PlanBuilder ---
    print("Constructing manual plan. Please wait...")
    plan = get_manual_plan(query, product_details)

    # --- Execute the Manually Built Plan ---
    my_config = Config.from_default(default_model=AI_MODEL)
    tool_registry = open_source_tool_registry + PortiaToolRegistry(my_config).replace_tool(
        LLMTool(model=AI_MODEL)
    )
    portia = Portia(config=my_config, tools=tool_registry)

    print("\n--- MANUAL PLAN CONSTRUCTED ---")
    print(plan.pretty_print())
    print("-----------------------------\n")

    print("\nExecuting the manual plan. This may take several minutes...")
    plan_run = portia.run_plan(plan)

    if plan_run.outputs and plan_run.outputs.final_output:
        print("\n--- FINAL REPORT ---")
        print(plan_run.outputs.final_output.value)
        print("--------------------")
    else:
        print("\n--- EXECUTION FINISHED ---")
        print("The plan run completed, but no final output was generated.")
        print("Here is the final state of the plan run for debugging:")
        print(plan_run.model_dump_json(indent=2))


if __name__ == "__main__":
    log_dir = "logs_manual"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(
        log_dir, f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )

    original_stdout = sys.stdout
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        sys.stdout = Tee(original_stdout, log_file)
        print(
            f"--- Console output for this run is being mirrored to {log_file_path} ---\n"
        )
        try:
            main()
        finally:
            # Restore stdout to its original state
            sys.stdout = original_stdout
