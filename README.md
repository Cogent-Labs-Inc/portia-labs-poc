# Portia Labs POC

## Market Research Agent

This project contains an AI agent built with Portia Labs that performs a comprehensive Total Addressable Market (TAM) and Serviceable Available Market (SAM) analysis for a given product idea.

## Setup

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    *(On Windows, use `venv\Scripts\activate`)*

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up API Keys:**
    Create a file named `.env` in the `market-research-agent` directory and add your API keys. You will need keys for Portia, your LLM provider (like OpenAI), and Tavily for the search tool.

    ```
    PORTIA_API_KEY="your_portia_key_here"
    OPENAI_API_KEY="your_openai_key_here"
    TAVILY_API_KEY="your_tavily_key_here"
    ```

## Usage

This agent can be run in two modes, each using a different approach to generating the research plan. The product details are currently hardcoded in both files for faster testing but can be replaced with `input()` prompts.

### 1. AI-Powered Planner (`auto_plan.py`)

This is the primary method. It uses the Portia AI Planner to dynamically generate a multi-step plan based on a high-level prompt. This approach is flexible and can adapt to changes in the prompt.

**To run:**
```bash
python auto_plan.py
```
Logs for each run will be saved in the `logs/` directory.

### 2. Manual Plan (`manual_plan.py`)

This method uses a handcrafted, static plan built with Portia's `PlanBuilder`. This provides a more predictable and deterministic execution path but is less flexible than the AI planner. It is primarily used for debugging and ensuring a consistent workflow.

**To run:**
```bash
python manual_plan.py
```
Logs for each run will be saved in the `logs_manual/` directory.
