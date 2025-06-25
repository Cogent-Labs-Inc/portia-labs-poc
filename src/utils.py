import os
import sys
from datetime import datetime
from portia.plan import PlanBuilder
from contextlib import contextmanager


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


@contextmanager
def logging_context(log_dir):
    """A context manager to handle logging setup and teardown."""
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(
        log_dir, f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )

    original_stdout = sys.stdout
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        sys.stdout = Tee(original_stdout, log_file)
        print(f"--- Console output is being mirrored to {log_file_path} ---\n")

        try:
            yield
        finally:
            # This block will always run, even if an error occurs inside the 'with' statement.
            sys.stdout = original_stdout


def get_manual_plan(query, product_details):
    """Builds the manual plan for the market research agent."""
    return (
        PlanBuilder(query)
        # Step 0: Generate initial search queries
        .step(
            task=f"Generate a detailed research plan with up to 8 initial search queries for {product_details['name']}.",
            tool_id="llm_tool",
            output="$initial_search_queries",
        )
        # Step 1: Execute initial search
        .step(
            task="Execute search queries to gather preliminary data.",
            tool_id="search_tool",
            output="$raw_search_results_cycle1",
        )
        .input(name="$initial_search_queries", description="List of initial search queries for market research")
        # Step 2: Condense results from cycle 1
        .step(
            task="Condense and summarize the raw search results from the initial queries.",
            tool_id="llm_tool",
            output="$condensed_results_cycle1",
        )
        .input(name="$raw_search_results_cycle1", description="Raw results from initial market research search queries")
        # Step 3: Analyze for gaps and create follow-up
        .step(
            task="Analyze the condensed results to identify gaps and generate up to 8 follow-up questions.",
            tool_id="llm_tool",
            output="$followup_questions_cycle1",
        )
        .input(name="$condensed_results_cycle1", description="Condensed key findings from initial research")
        # Step 4: Conditional Search on follow-up 1
        .step(
            task="Perform targeted follow-up searches.",
            tool_id="search_tool",
            output="$raw_search_results_cycle2",
        )
        .input(name="$followup_questions_cycle1", description="Follow-up questions for more targeted research")
        .condition("len($followup_questions_cycle1) > 0")
        # Step 5: Condense results from cycle 2
        .step(
            task="Process the raw search results from Cycle 2.",
            tool_id="llm_tool",
            output="$condensed_results_cycle2",
        )
        .input(name="$raw_search_results_cycle2", description="Raw search results from Cycle 2.")
        .condition("$raw_search_results_cycle2 is not None")
        # Step 6: Final Summarization
        .step(
            task="Summarize and sort all collected research data into four key buckets: Financial Data, Behavioral Data, Competitor Data, and Demographic Data.",
            tool_id="llm_tool",
            output="$summarized_data",
        )
        .input(name="$condensed_results_cycle1", description="Condensed results from the first search cycle.")
        .input(name="$condensed_results_cycle2", description="Condensed results from the second search cycle (if it ran).")
        # Step 7: Competitive Summary
        .step(
            task=f"Create a narrative summary of the competitive landscape for {product_details['primary_competitors']}.",
            tool_id="llm_tool",
            output="$competitor_summary",
        )
        .input(name="$summarized_data", description="The final categorized summary of all research data.")
        # Step 8: TAM/SAM Calculation
        .step(
            task="Calculate the final TAM and SAM figures, listing assumptions and data points.",
            tool_id="llm_tool",
            output="$market_size_estimates",
        )
        .input(name="$summarized_data", description="All summarized research data.")
        # Step 9: Executive Summary
        .step(
            task="Generate a concise executive summary of findings and calculations.",
            tool_id="llm_tool",
            output="$executive_summary",
        )
        .input(name="$market_size_estimates", description="Final market size determinations and assumptions")
        # Step 10: Methodology Explanation
        .step(
            task="Describe the methodology, sources, and assumptions used for the analysis.",
            tool_id="llm_tool",
            output="$methodology_explanation",
        )
        .input(name="$market_size_estimates", description="Finalized market size and assumptions")
        # Step 11: Final Report Assembly
        .step(
            task="Assemble all sections into a comprehensive markdown report.",
            tool_id="llm_tool",
            output="$final_markdown_report",
        )
        .input(name="$executive_summary", description="The executive summary in markdown")
        .input(name="$market_size_estimates", description="Market size and data analysis")
        .input(name="$methodology_explanation", description="Methodology and assumptions")
        .input(name="$competitor_summary", description="Competitive landscape summary")
        .build()
    )
