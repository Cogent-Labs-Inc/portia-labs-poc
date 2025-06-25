RESEARCH_PROMPT_TEMPLATE = """
Your task is to conduct a comprehensive Total Addressable Market (TAM) and Serviceable Available Market (SAM) analysis for a new product idea. You will produce a detailed report in markdown format.

**Product Details:**
*   **Name:** {name}
*   **Description:** {description}
*   **Target Audience:** {target_audience}
*   **Primary Competitors:** {primary_competitors}
*   **Differentiators:** {differentiators}

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

SIMPLIFIED_RESEARCH_PROMPT_TEMPLATE = """
Please perform a comprehensive market analysis for a new product and generate a detailed report. I need to understand the Total Addressable Market (TAM) and Serviceable Available Market (SAM).

Your analysis should be thorough. Start by planning your research, then gather data iteratively until you have enough information. Once you have the data, I need you to calculate the market size, summarize your findings, and assemble everything into a well-structured markdown report.

**Product Details:**
*   **Name:** {name}
*   **Description:** {description}
*   **Target Audience:** {target_audience}
*   **Primary Competitors:** {primary_competitors}
*   **Differentiators:** {differentiators}

The final output should be the complete markdown report including your methodology, assumptions, and calculations.
"""
