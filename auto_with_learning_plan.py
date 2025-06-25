import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from portia import (
    Config,
    LLMTool,
    Portia,
    PortiaToolRegistry,
    open_source_tool_registry,
)
from prompts import SIMPLIFIED_RESEARCH_PROMPT_TEMPLATE
from utils import Tee, get_product_details

from constants import (
    default_model,
    execution_model,
    introspection_model,
    planning_model,
    summarizer_model,
    tool_model,
)


def generate_and_display_plan(portia_config, prompt):
    print("Generating a plan for the research task. Please wait...")

    example_plans = portia_config.storage.get_similar_plans(prompt)
    if not example_plans:
        print(
            "No example plans were found in Portia storage. Did you remember to create and 'like' the plans from the previous step?"
        )
    else:
        print(f"{len(example_plans)} similar plans were found.")
    new_plan = portia_config.plan(
        prompt,
        example_plans=example_plans,
    )

    print("\n--- PLAN GENERATED ---")
    print(new_plan.pretty_print())
    print("----------------------\n")
    return new_plan


def main():
    """Main function to run the market research agent."""
    load_dotenv()

    # Check for necessary API keys
    if not all(
        [
            os.getenv("PORTIA_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("TAVILY_API_KEY"),
            os.getenv("GOOGLE_API_KEY"),
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

    # Format the prompt from the template with the product details
    prompt = SIMPLIFIED_RESEARCH_PROMPT_TEMPLATE.format(**product_details)

    # Instantiate Portia. We combine the open_source_tool_registry (which includes
    # tools like search and a calculator) with the PortiaToolRegistry for any
    # potential cloud-hosted tools. The llm_tool is available by default.
    my_config = Config.from_default(default_model=default_model, planning_model=planning_model, execution_model=execution_model, introspection_model=introspection_model, summarizer_model=summarizer_model)
    tool_registry = open_source_tool_registry + PortiaToolRegistry(my_config).replace_tool(
        LLMTool(model=tool_model)
    )
    portia = Portia(config=my_config, tools=tool_registry)

    plan = generate_and_display_plan(portia, prompt)

    while True:
        user_input = input("Are you happy with this plan? Please enter 'y' to accept, 'n' to regenerate, or 'q' to quit: ")
        if user_input.lower() == "y":
            break
        elif user_input.lower() == "n":
            print("Regenerating plan...")
            plan = generate_and_display_plan(portia, prompt)
        elif user_input.lower() == "q":
            print("Execution cancelled by user.")
            sys.exit(0)
        else:
            print("Please enter 'y' to accept the plan, 'n' to regenerate it, or 'q' to quit.")

    # Execute the plan
    print("\nExecuting the plan. This may take several minutes...")
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
    log_dir = "logs"
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
