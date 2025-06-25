import os
import sys
from datetime import datetime
from src.agent_base import ResearchAgentBase
from src.prompts import SIMPLIFIED_RESEARCH_PROMPT_TEMPLATE
from src.utils import logging_context


class AutoPlanWithLearning(ResearchAgentBase):
    """
    Runs the market research agent using the simplified prompt template,
    leveraging user-led learning by fetching similar plans from storage.
    """

    def __init__(self):
        super().__init__()
        self.prompt = SIMPLIFIED_RESEARCH_PROMPT_TEMPLATE.format(**self.product_details)

    def _create_plan(self):
        """
        Generates a plan by first fetching similar 'liked' plans from
        Portia storage to use as examples for the planner.
        """
        print("Generating a plan for the research task. Please wait...")
        print("Attempting to fetch similar plans from Portia cloud storage...")

        example_plans = self.portia.storage.get_similar_plans(self.prompt)
        if not example_plans:
            print(
                "No example plans were found. The planner will proceed without examples."
            )
        else:
            print(f"{len(example_plans)} similar example plan(s) were found.")

        new_plan = self.portia.plan(
            self.prompt,
            example_plans=example_plans,
        )

        print("\n--- PLAN GENERATED ---")
        print(new_plan.pretty_print())
        print("----------------------\n")
        return new_plan


if __name__ == "__main__":
    with logging_context("logs/auto_with_learning"):
        agent = AutoPlanWithLearning()
        agent.run()
