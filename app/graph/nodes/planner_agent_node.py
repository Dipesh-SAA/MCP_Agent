from app.infrastrature.llm.llm_factory import llm
from app.infrastrature.prompts.planner_agent_prompt import planner_agent_prompt
from langgraph.types import interrupt
# from utils.file_utils import save_markdown
from app.infrastrature.llm.llm_factory import llm

from app.infrastrature.prompts.vibe_project_json_generator_prompt import (
    vibe_project_json_generator_prompt
)

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


async def planner_agent_node(state):

    formatted_messages = planner_agent_prompt.invoke(
        {
            "requirements": state["requirements"]
        }
    )

    response = await llm.ainvoke(formatted_messages)

    route = response.content.strip().lower().replace(" ", "")

    if route == "html,sql":
        route = "html_sql"

    return {
        "route": route
    }

#################################### Vibe Planner #########################################



async def planner_json_agent_node(state):

    formatted_messages = (
        vibe_project_json_generator_prompt.invoke(
            {
                "requirements": state["requirements"]
            }
        )
    )

    response = await llm.ainvoke(
        formatted_messages
    )

    return {
        "plan": response.content
    }





#############################################################################################
async def plan_interrupt_node(state):

    interrupt(
        {
            "type": "plan_review",
            "plan": state["plan"],
            "message": "Please review and approve plan."
        }
    )

    return {
        "current_step": "PLAN_APPROVED"
    }