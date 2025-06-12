import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from portia import Config, Portia, open_source_tool_registry, PortiaToolRegistry, LLMTool
from portia.model import OpenAIGenerativeModel


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
    product_details["name"] = input("Product Name: ")
    product_details["description"] = input("Product Description: ")
    product_details["target_audience"] = input("Target Audience: ")
    product_details["primary_competitors"] = input("Primary Competitors (comma-separated): ")
    product_details["differentiators"] = input("Key Differentiators: ")
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

    # This is the detailed, multi-stage prompt for the Portia planner.
    # It instructs the agent on how to perform the entire research process.
    prompt = f"""
Your task is to conduct a comprehensive Total Addressable Market (TAM) and Serviceable Available Market (SAM) analysis for a new product idea. You will produce a detailed report in markdown format.

**Product Details:**
*   **Name:** {product_details["name"]}
*   **Description:** {product_details["description"]}
*   **Target Audience:** {product_details["target_audience"]}
*   **Primary Competitors:** {product_details["primary_competitors"]}
*   **Differentiators:** {product_details["differentiators"]}

**Execution Flow:**

**Stage 1: Initial Query Planning**
First, formulate a detailed research plan. Using the llm_tool, generate a set of initial search queries. Rule: The output of this step must be a clean list of strings, with no extra formatting or numbering.

**Stage 2: Iterative Research Loop**
You will now enter an iterative research cycle. This cycle should repeat up to a maximum of 2 times. For each cycle, the steps are:

1.  **Search:** Execute the current set of search queries using the search_tool. Let's call the output `$raw_search_results`.
2.  **Pre-process Results:** Using the llm_tool, process the `$raw_search_results`. For each result, extract only the 'title' and a brief summary of the 'content'. Your goal is to create a condensed text block of the key findings that is much smaller than the raw data. Let's call the output `$condensed_results`.
3.  **Analyze & Generate New Queries:** Using the llm_tool, analyze the `$condensed_results` to identify crucial missing information. Based on the gaps, generate a new, targeted set of follow-up questions.
    *   **CRITICAL RULE:** The sole purpose of this step is to produce a list of questions for the *next* search step. You MUST NOT answer the questions yourself. The output must be ONLY a clean list of strings for the search_tool.
    *   If you determine no new information is needed, you MUST output an empty list `[]`.

4.  **Conditional Search:** This is the next search step. It must have a condition to only run IF the list of follow-up questions from the previous step is NOT empty. It will use the new questions as input.

**Stage 3: Data Processing and Summarization**
Once all research cycles are complete (either by reaching the 2-cycle limit or by generating an empty list of questions), process all the raw data you have collected from all search steps.
1.  Using the llm_tool, summarize and sort the general research data into four key buckets: **Financial Data**, **Behavioral Data**, **Competitor Data**, and **Demographic Data**.
2.  Using the llm_tool, create a separate narrative summary of the competitive landscape based on the competitor-specific search results.

**Stage 4: Final Calculation and Content Generation**
With the clean, summarized data, perform the final analysis using the llm_tool.
1.  **Calculate TAM/SAM:** Produce the final TAM and SAM figures. Clearly list the key data points, assumptions, and any proxy data used in your calculations. Ensure your logic is sound and that the SAM is a logical subset of the TAM.
2.  **Write Executive Summary:** Generate a concise executive summary based on your final calculations and key findings.
3.  **Explain Methodology:** Generate a narrative explaining *how* you arrived at your conclusions, detailing the thought process behind the calculations and assumptions.

**Stage 5: Final Assembly**
Using the llm_tool, assemble all the generated components into a single, comprehensive markdown document. The report should be well-structured with clear headings for each section (e.g., Executive Summary, Market Size, Market Size Calculations, Key Assumptions, Methodology, Competitor Research Summary).

The final output of this entire plan must be the complete markdown report.
"""

    # Instantiate Portia. We combine the open_source_tool_registry (which includes
    # tools like search and a calculator) with the PortiaToolRegistry for any
    # potential cloud-hosted tools. The llm_tool is available by default.
    model = "openai/gpt-4.1-nano"
    my_config = Config.from_default(default_model=model, planning_model=model, execution_model=model, introspection_model=model, summarizer_model=model)
    tool_registry = open_source_tool_registry + PortiaToolRegistry(my_config).replace_tool(
        LLMTool(model=model)
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
