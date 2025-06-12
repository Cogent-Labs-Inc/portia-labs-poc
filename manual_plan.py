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
    product_details["name"] = input("Product Name: ")
    product_details["description"] = input("Product Description: ")
    product_details["target_audience"] = input("Target Audience: ")
    product_details["primary_competitors"] = input("Primary Competitors (comma-separated): ")
    product_details["differentiators"] = input("Key Differentiators: ")
    print("---\n")
    return product_details


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
    plan = (
        PlanBuilder(query)
        # Step 0: Generate initial search queries
        .step(
            task="Generate a detailed research plan with initial search queries in the form of a list of strings, covering aspects like total addressable market, target demographics, competitor landscape, trends in diecast models, and market demand for high-quality carbon fiber models.",
            tool_id="llm_tool",
            output="$initial_search_queries",
        )
        # Step 1: Execute initial search
        .step(
            task="Execute search queries to gather preliminary data about the TAM and SAM for high-quality diecast model cars, focusing on market size, target consumers, and competitive landscape.",
            tool_id="search_tool",
            output="$raw_search_results_cycle1",
        )
        .input(name="$initial_search_queries", description="List of initial search queries for market research")
        # Step 2: Condense results from cycle 1
        .step(
            task="Condense and summarize the raw search results from the initial queries, extracting key findings on market trends, size, and competitive landscape, creating a concise overview.",
            tool_id="llm_tool",
            output="$condensed_results_cycle1",
        )
        .input(name="$raw_search_results_cycle1", description="Raw results from initial market research search queries")
        # Step 3: Analyze for gaps and create follow-up
        .step(
            task="Analyze the condensed results to identify any missing information or gaps, and generate a targeted list of follow-up search questions to refine the research.",
            tool_id="llm_tool",
            output="$followup_questions_cycle1",
        )
        .input(name="$condensed_results_cycle1", description="Condensed key findings from initial research")
        # Step 4: Conditional Search on follow-up 1
        .step(
            task="Perform targeted follow-up searches with the questions generated to gather more specific data on market segmentation, competitive differentiation, and consumer preferences.",
            tool_id="search_tool",
            output="$raw_search_results_cycle2",
        )
        .input(name="$followup_questions_cycle1", description="Follow-up questions for more targeted research")
        .condition("len($followup_questions_cycle1) > 0")
        # Step 5: Condense results from cycle 2
        .step(
            task="Process the raw search results from Cycle 2 by extracting for each result only the title and a brief summary of the content. The result should be a condensed text block reflecting key findings.",
            tool_id="llm_tool",
            output="$condensed_results_cycle2",
        )
        .input(name="$raw_search_results_cycle2", description="Raw search results from Cycle 2.")
        .condition("$raw_search_results_cycle2 is not None")
        # Step 6: Final Summarization
        .step(
            task="Summarize and sort all collected research data from all search steps into four key buckets: Financial Data, Behavioral Data, Competitor Data, and Demographic Data.",
            tool_id="llm_tool",
            output="$summarized_data",
        )
        .input(name="$condensed_results_cycle1", description="Condensed results from the first search cycle.")
        .input(name="$condensed_results_cycle2", description="Condensed results from the second search cycle (if it ran).")
        # Step 7: Competitive Summary
        .step(
            task="Create a narrative summary of the competitive landscape specifically based on the competitor-related search results from the collected data. The summary should highlight competitor insights for Tamiya and Maisto.",
            tool_id="llm_tool",
            output="$competitor_summary",
        )
        .input(name="$summarized_data", description="The final categorized summary of all research data.")
        # Step 8: TAM/SAM Calculation
        .step(
            task="Calculate the final TAM and SAM figures using all the gathered summaries and key data points. Ensure that the calculation clearly lists the key data points, assumptions, and any proxy data used.",
            tool_id="llm_tool",
            output="$market_size_estimates",
        )
        .input(name="$summarized_data", description="All summarized research data.")
        # Step 9: Executive Summary
        .step(
            task="Generate a concise executive summary based on the final TAM and SAM calculations and the key findings from the research.",
            tool_id="llm_tool",
            output="$executive_summary",
        )
        .input(name="$market_size_estimates", description="Final market size determinations and assumptions")
        # Step 10: Methodology Explanation
        .step(
            task="Describe the methodology used for research, analysis, and calculations, including sources, assumptions, and logical flow.",
            tool_id="llm_tool",
            output="$methodology_explanation",
        )
        .input(name="$market_size_estimates", description="Finalized market size and assumptions")
        # Step 11: Final Report Assembly
        .step(
            task="Assemble all sections: Executive Summary, Market Size, Market Size Calculations, Key Assumptions, Methodology, and Competitor Research Summary into a comprehensive markdown document.",
            tool_id="llm_tool",
            output="$final_markdown_report",
        )
        .input(name="$executive_summary", description="The executive summary in markdown")
        .input(name="$market_size_estimates", description="Market size and data analysis")
        .input(name="$methodology_explanation", description="Methodology and assumptions")
        .input(name="$competitor_summary", description="Competitive landscape summary")
        .build()
    )

    # --- Execute the Manually Built Plan ---
    my_config = Config.from_default(default_model=AI_MODEL)
    tool_registry = open_source_tool_registry + PortiaToolRegistry(my_config).replace_tool(
        LLMTool(model=AI_MODEL)
    )
    portia = Portia(config=my_config, tools=tool_registry)

    print("\n--- MANUAL PLAN CONSTRUCTED ---")
    print(plan.pretty_print())
    print("-----------------------------\n")

    user_input = input("Are you happy with this manual plan? (y/n): ")
    if user_input.lower() != "y":
        print("Execution cancelled by user.")
        sys.exit(0)

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
