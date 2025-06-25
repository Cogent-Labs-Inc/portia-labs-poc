import os
import sys

from dotenv import load_dotenv
from portia import (
    Config,
    LLMTool,
    Portia,
    PortiaToolRegistry,
    open_source_tool_registry,
    ToolRetryError,
)

from .utils import get_product_details
from .constants import (
    default_model,
    execution_model,
    introspection_model,
    planning_model,
    summarizer_model,
    tool_model,
)


class ResearchAgentBase:
    """A generic base class for the market research agent."""

    def __init__(self):
        """Initializes the base agent runner."""
        self._setup()

    def _setup(self):
        """Handles initial setup like loading env vars and checking keys."""
        load_dotenv()
        self._check_api_keys()
        self.product_details = get_product_details()

        my_config = Config.from_default(
            default_model=default_model,
            planning_model=planning_model,
            execution_model=execution_model,
            introspection_model=introspection_model,
            summarizer_model=summarizer_model,
        )
        tool_registry = open_source_tool_registry + PortiaToolRegistry(
            my_config
        ).replace_tool(LLMTool(model=tool_model))
        self.portia = Portia(config=my_config, tools=tool_registry)

    def _check_api_keys(self):
        """Checks for the presence of required API keys."""
        if not all(
            [
                os.getenv("PORTIA_API_KEY"),
                os.getenv("OPENAI_API_KEY"),
                os.getenv("TAVILY_API_KEY"),
            ]
        ):
            print("---")
            print("ERROR: Missing one or more required API keys in your .env file.")
            print("---")
            sys.exit(1)

    def _create_plan(self):
        """
        Abstract method for plan creation. Must be overridden by subclasses.
        This method should generate and return a plan.
        """
        raise NotImplementedError(
            "Subclasses must implement the '_create_plan' method."
        )

    def run(self):
        """Runs the main agent loop: plan, get confirmation, and execute."""
        plan = self._create_plan()

        while True:
            user_input = input(
                "Are you happy with this plan? Please enter 'y' to accept, 'n' to regenerate, or 'q' to quit: "
            )
            if user_input.lower() == "y":
                break
            elif user_input.lower() == "n":
                print("Regenerating plan...")
                plan = self._create_plan()
            elif user_input.lower() == "q":
                print("Execution cancelled by user.")
                sys.exit(0)
            else:
                print(
                    "Please enter 'y' to accept the plan, 'n' to regenerate it, or 'q' to quit."
                )

        print("\nExecuting the plan. This may take several minutes...")
        try:
            plan_run = self.portia.run_plan(plan)
            if plan_run.outputs and plan_run.outputs.final_output:
                print("\n--- FINAL REPORT ---")
                print(plan_run.outputs.final_output.value)
                print("--------------------")
            else:
                print("\n--- EXECUTION FINISHED ---")
                print("The plan run completed, but no final output was generated.")
                print("Final state for debugging:")
                print(plan_run.model_dump_json(indent=2))

        except ToolRetryError as e:
            print(f"\n--- EXECUTION FAILED: {e} ---")
            print("This is often a temporary network issue. Please try again.")

        except Exception as e:
            print(f"\n--- AN UNEXPECTED ERROR OCCURRED: {e} ---")
            if "plan_run" in locals():
                print(plan_run.model_dump_json(indent=2))
