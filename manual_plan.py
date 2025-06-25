import sys

from src.utils import logging_context, get_manual_plan
from src.agent_base import ResearchAgentBase

AI_MODEL = "openai/gpt-4.1-nano"


class ManualPlanAgent(ResearchAgentBase):
    """
    Runs the market research agent using a manually constructed plan
    defined in the get_manual_plan() utility function.
    """

    def __init__(self):
        super().__init__()
        self.query = (
            f"Run a TAM/SAM analysis for the following product: {self.product_details['name']}"
        )

    def _create_plan(self):
        """Builds the plan manually using the PlanBuilder."""
        print("Constructing manual plan. Please wait...")
        plan = get_manual_plan(self.query, self.product_details)

        print("\n--- MANUAL PLAN CONSTRUCTED ---")
        print(plan.pretty_print())
        print("-----------------------------\n")
        return plan

    def run(self):
        """
        Overrides the base run method to execute the manual plan directly
        without the regeneration loop.
        """
        plan = self._create_plan()

        user_input = input("Are you happy with this manual plan? (y/n): ")
        if user_input.lower() != "y":
            print("Execution cancelled by user.")
            sys.exit(0)

        print("\nExecuting the manual plan. This may take several minutes...")
        plan_run = self.portia.run_plan(plan)

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
    with logging_context("logs/manual"):
        agent = ManualPlanAgent()
        agent.run()
