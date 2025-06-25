import os
import sys
from datetime import datetime
from src.agent_base import ResearchAgentBase
from src.prompts import RESEARCH_PROMPT_TEMPLATE
from src.utils import logging_context


class AutoPlanWithoutLearning(ResearchAgentBase):
    """
    Runs the market research agent using the detailed prompt template
    without leveraging user-led learning.
    """

    def __init__(self):
        super().__init__()
        self.prompt = RESEARCH_PROMPT_TEMPLATE.format(**self.product_details)

    def _create_plan(self):
        """Generates and displays a plan using the standard planner."""
        print("Generating a plan for the research task. Please wait...")
        new_plan = self.portia.plan(self.prompt)

        print("\n--- PLAN GENERATED ---")
        print(new_plan.pretty_print())
        print("----------------------\n")
        return new_plan


if __name__ == "__main__":
    with logging_context("logs/auto_without_learning"):
        agent = AutoPlanWithoutLearning()
        agent.run()
