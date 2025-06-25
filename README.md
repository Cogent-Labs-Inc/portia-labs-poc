# Portia Labs POC - Market Research Agent

This project contains an AI agent built with Portia Labs that performs a comprehensive Total Addressable Market (TAM) and Serviceable Available Market (SAM) analysis for a given product idea.

The core application logic (base classes, prompts, utilities) is located in the `src/` directory, while runnable scripts are in the project root.

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
    Create a file named `.env` in the project root directory (`portia-labs-poc/`) and add your API keys. You will need keys for Portia, your LLM provider, and Tavily.

    ```
    PORTIA_API_KEY="your_portia_key_here"
    OPENAI_API_KEY="your_openai_key_here"
    TAVILY_API_KEY="your_tavily_key_here"
    GOOGLE_API_KEY="your_google_key_here"
    ```

## Usage

This agent can be run in three modes. The product details are currently hardcoded in `src/utils.py` for faster testing but can be replaced with `input()` prompts.

### 1. Auto-Planner (Without Learning)
This is the standard method. It uses the Portia AI Planner and a detailed prompt to dynamically generate a plan.

**To run:**
```bash
python auto_plan_without_learning.py
```
Logs for each run will be saved in the `logs/auto_without_learning/` directory.

### 2. Auto-Planner (With User-Led Learning)
This method uses a simplified prompt, relying on Portia's ability to learn from previously "liked" plans stored in the cloud. This tests the agent's ability to infer complex workflows from simple instructions.

**To run:**
```bash
python auto_plan_with_learning.py
```
Logs for each run will be saved in the `logs/auto_with_learning/` directory.

### 3. Manual Plan
This method uses a handcrafted, static plan built with Portia's `PlanBuilder`. This provides a predictable, deterministic execution path, useful for debugging.

**To run:**
```bash
python manual_plan.py
```
Logs for each run will be saved in the `logs/manual/` directory.
