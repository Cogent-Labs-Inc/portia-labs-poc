import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from portia import Config, Portia, open_source_tool_registry, PortiaToolRegistry, LLMTool
from prompts import RESEARCH_PROMPT_TEMPLATE

AI_MODEL = "openai/gpt-4.1-nano"


class Tee:
    """A helper class to redirect stdout to both the console and a file."""

    def __init__(self, console, file):
        self.console = console
        self.file = file

    def write(self, data):
        self.console.write(data)
        self.file.write(data)
        self.flush()

    def flush(self):
        self.console.flush()
        self.file.flush()


def get_product_details():
    """Gathers product details from the user via the command line."""
    product_details = {}
    print("---")
    print("Please enter the details for the product you want to research.")
    product_details["name"] = "Carbon Car Models"
    product_details["description"] = "Diecast model cars made of high quality carbon fiber"
    product_details["target_audience"] = "Adults who are into cars and/or driving"
    product_details["primary_competitors"] = "Tamiya, Maisto"
    product_details["differentiators"] = "Made of carbon fiber, high quality, lightweight"
    print("---\n")
    return product_details


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
    prompt = RESEARCH_PROMPT_TEMPLATE.format(**product_details)

    # Instantiate Portia. We combine the open_source_tool_registry (which includes
    # tools like search and a calculator) with the PortiaToolRegistry for any
    # potential cloud-hosted tools. The llm_tool is available by default.
    my_config = Config.from_default(default_model=AI_MODEL, planning_model=AI_MODEL, execution_model=AI_MODEL, introspection_model=AI_MODEL, summarizer_model=AI_MODEL)
    tool_registry = open_source_tool_registry + PortiaToolRegistry(my_config).replace_tool(
        LLMTool(model=AI_MODEL)
    )
    portia = Portia(config=my_config, tools=tool_registry)

    # Generate the plan from the detailed prompt
    print("Generating a plan for the research task. Please wait...")
    plan = portia.plan(prompt)

    print("\n--- PLAN GENERATED ---")
    print(plan.pretty_print())
    print("----------------------\n")

    # Get user confirmation before executing the plan
    user_input = input("Are you happy with this plan? (y/n): ")
    if user_input.lower() != "y":
        print("Execution cancelled by user.")
        sys.exit(0)

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
