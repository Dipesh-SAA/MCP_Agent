from app.infrastrature.llm.llm_factory import llm
from app.infrastrature.prompts.agent2_prompt import agent2_agent_prompt
from app.services.session.markdown_chat_logger import append_agent_chat

# from utils.file_utils import save_markdown


async def agent2(state: dict):

    formatted_messages = agent2_agent_prompt.invoke(
        {
             "requirements": state["requirements"]
            
        }
    )

    response = await llm.ainvoke(formatted_messages)

    append_agent_chat(
        state.get("session_id"),
        "SQL Agent",
        formatted_messages,
        response.content
    )



    return {
        "output": response.content
    }
