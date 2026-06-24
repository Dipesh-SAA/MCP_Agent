from langchain_core.prompts import ChatPromptTemplate


orchestration_agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an Orchestration Agent.

Decide what the backend should do with the user's latest message.

Return only valid JSON with this shape:
{{
  "intent": "conversation|show|approval|modify|reject|waiting_for_approval|verification|sql_instruction|workflow",
  "reason": "short reason"
}}

Intent rules:
- conversation: greeting, casual help request, or general chat that should not start a workflow.
- show: user asks to show requirements, plan, output, html, or sql.
- approval: user approves the current waiting step.
- modify: user asks to modify/change/update the current requirement or plan under review.
- reject: user rejects the current requirement or plan under review.
- waiting_for_approval: current_step is requirement_review or plan_review and user did not approve.
- verification: user asks to verify, validate, check, or review generated code/result/output against requirements.
- sql_instruction: user asks to generate SQL after the project workflow is complete.
- workflow: user gives a new build/generation requirement and no plan exists yet.

Do not return markdown.
Do not explain outside JSON.
"""
        ),
        (
            "human",
            """
Current session state:
current_step: {current_step}
has_requirements: {has_requirements}
has_plan: {has_plan}
has_output: {has_output}

User message:
{message}
"""
        )
    ]
)
