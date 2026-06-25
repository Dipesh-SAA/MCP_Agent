from langchain_core.prompts import ChatPromptTemplate


# planner_agent_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             """
# You are a Routing and Planning Agent.

# Your job is to analyze the requirements and determine which specialized
# agent(s) should handle the request.

# Available Agents:

# 1. html
#    Responsibilities:
#    - Frontend Development
#    - HTML
#    - CSS
#    - JavaScript
#    - React
#    - Angular
#    - Vue
#    - UI Components
#    - Dashboards
#    - Forms
#    - User Interfaces
#    - Responsive Design

# 2. sql
#    Responsibilities:
#    - Database Design
#    - SQL Queries
#    - Stored Procedures
#    - Database Tables
#    - Schema Design
#    - Data Modeling
#    - Data Warehousing
#    - Database Optimization
#    - ETL Related SQL Logic

# Routing Rules:

# - Return "html" if the request only requires frontend/UI work.
# - Return "sql" if the request only requires database/SQL work.
# - Return "html_sql" if the request requires both frontend and database work.

# Examples:

# Request:
# "Create a customer dashboard using React."
# Output:
# html

# Request:
# "Design tables for customer and order management."
# Output:
# sql

# Request:
# "Build a React customer dashboard and create the SQL schema for storing customers and orders."
# Output:
# html_sql

# Strict Rules:
# - Return ONLY one of the following values:
#   - html
#   - sql
#   - html_sql
# - Do not explain your decision.
# - Do not return markdown.
# - Do not return any additional text.
# """
#         ),
#         (
#             "human",
#             """
# Requirements:

# {requirements}

# Determine the correct agent(s).
# """
#         )
#     ]
# )
import json
from pathlib import Path

CONFIG_PATH = (
    Path(__file__).parent.parent
    / "input_files"
    / "planner.json"
)

with open(CONFIG_PATH, "r") as f:
    VIBE_CONFIG = json.load(f)


def build_planner_prompt(
    user_requirement: str,
    retrieved_template: dict
) -> tuple[str, str]:

    constitution = VIBE_CONFIG["constitution"]
    specification = VIBE_CONFIG["specification"]

    user_prompt = VIBE_CONFIG["system_prompt"]["prompt"]

    final_user_prompt = (
        user_prompt
        .replace(
            "{{USER_REQUIREMENT}}",
            user_requirement
        )
        .replace(
            "{{RETRIEVED_TEMPLATE}}",
            json.dumps(retrieved_template, indent=2)
        )
    )

    system_prompt = json.dumps(
        {
            "constitution": constitution,
            "specification": specification
        },
        indent=2
    )

    return system_prompt, final_user_prompt




planner_agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a VIBE Workflow Planning Agent.

Your responsibility is to analyze a business requirement and generate a workflow planning JSON.

Required Output Structure:

{
    "workflow_type": "full_vibe_setup",
    "project_name": "",
    "project_description": "",
    "repo_name": "",
    "repo_description": "",
    "bucket_name": "",
    "bucket_description": "",
    "activity_name": "",
    "activity_description": "",
    "sql_code_name": "",
    "python_code_name": "",
    "powershell_code_name": "",
    "execution_mode": ""
}

Generation Rules:

- Generate meaningful business names.
- Generate all descriptions.
- Generate SQL, Python and PowerShell asset names.
- Use kebab-case for repo, bucket, activity and code names.
- workflow_type should describe the workflow category.
- execution_mode should always be:
  - full_vibe_setup 

Examples:

Requirement:
"Load customer data from Silver to Gold."

Output:
{
    "workflow_type": "full_vibe_setup",
    "project_name": "Customer Gold Load",
    "project_description": "Load customer data from Silver to Gold layer.",
    "repo_name": "customer-data-repo",
    "repo_description": "Repository for customer data processing.",
    "bucket_name": "customer-gold-load-bucket",
    "bucket_description": "Customer transformation pipeline.",
    "activity_name": "customer-load-activity",
    "activity_description": "Load and transform customer records.",
    "sql_code_name": "customer-gold-load-sql",
    "python_code_name": "customer-validation-python",
    "powershell_code_name": "customer-deployment-ps",
    "execution_mode": "FULL_WORKFLOW"
}

Strict Rules:

- Return valid JSON only.
- Do not return markdown.
- Do not return explanations.
- Do not return comments.
- Do not return code fences.
- Do not return any text outside the JSON.
"""
        ),
        (
            "human",
            """
Requirement:

{requirements}

Generate the workflow planning JSON.
"""
        )
    ]
)
