from app.infrastrature.llm.llm_factory import llm
from langgraph.types import interrupt
# from utils.file_utils import save_markdown
from app.infrastrature.prompts.planner_agent_prompt import (
    build_planner_prompt,
    planner_agent_prompt
)
import json

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)
from app.services.session.markdown_chat_logger import append_agent_chat

# from app.infrastrature.prompts.vibe_project_json_generator_prompt import (
#     vibe_project_json_generator_prompt
# )

# async def planner_agent(state: dict):

#     formatted_messages = planner_agent_prompt.invoke(
#         {
#             "user_input": state["user_input"],
            
#         }
#     )

#     response = await llm.ainvoke(formatted_messages)



#     return {
#         "response": response.content
#     }


# async def planner_agent_node(state):

#     formatted_messages = planner_agent_prompt.invoke(
#         {
#             "requirements": state["requirements"]
#         }
#     )

#     response = await llm.ainvoke(formatted_messages)

#     append_agent_chat(
#         state.get("session_id"),
#         "Planner Routing Agent",
#         formatted_messages,
#         response.content
#     )

#     route = response.content.strip().lower().replace(" ", "")

#     if route == "html,sql":
#         route = "html_sql"

#     return {
#         "route": route
#     }
# planner_agent_node.py

async def planner_json_agent_node(state):

    requirement_text = state["requirements"]

    if state.get("modify_feedback"):
        requirement_text = f"""
Requirements:
{state["requirements"]}

Previously generated plan:
{state.get("plan")}

User feedback / requested changes:
{state["modify_feedback"]}

Regenerate the plan incorporating this feedback.
"""

    system_prompt, user_prompt = build_planner_prompt(
        user_requirement=requirement_text,
        retrieved_template=state.get("retrieved_template", {})
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = await llm.ainvoke(messages)

    append_agent_chat(
        state.get("session_id"),
        "Planner Agent",
        messages,
        response.content
    )

    content = response.content.strip()

    if content.startswith("```"):
        content = content.strip("`")
        content = content.removeprefix("json").strip()

    return {
        "plan": json.loads(content),
        "modify_feedback": None
    }
#################################### Vibe Planner #########################################


async def planner_json_agent_node(state):

    requirement_text = state["requirements"]

    if state.get("modify_feedback"):
        requirement_text = f"""
Requirements:
{state["requirements"]}

Previously generated plan:
{state.get("plan")}

User feedback / requested changes:
{state["modify_feedback"]}

Regenerate the plan incorporating this feedback.
"""

    system_prompt, user_prompt = build_planner_prompt(
        user_requirement=requirement_text,
        retrieved_template=state.get(
            "retrieved_template",
            {}
        )
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = await llm.ainvoke(
        messages
    )

    append_agent_chat(
        state.get("session_id"),
        "Planner Agent",
        messages,
        response.content
    )

    content = response.content.strip()

    if content.startswith("```"):
        content = content.strip("`")
        content = content.removeprefix("json").strip()

    return {
        "plan": json.loads(content),
        "modify_feedback": None
    }


#############################################################################################
# planner_agent_node.py (replace plan_interrupt_node)

async def plan_interrupt_node(state):

    resume = interrupt(
        {
            "type": "plan_review",
            "plan": state["plan"],
            "message": "Please review and approve plan."
        }
    )

    if isinstance(resume, dict) and resume.get("action") == "modify":
        return {
            "current_step": "PLAN_MODIFY",
            "modify_feedback": resume.get("feedback", "")
        }

    return {
        "current_step": "PLAN_APPROVED"
    }
