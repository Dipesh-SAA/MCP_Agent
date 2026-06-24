from app.infrastrature.llm.llm_factory import llm
from app.infrastrature.prompts.agent2_prompt import agent2_agent_prompt

# from utils.file_utils import save_markdown


async def agent2(state: dict):

    formatted_messages = agent2_agent_prompt.invoke(
        {
             "requirements": state["requirements"]
            
        }
    )

    response = await llm.ainvoke(formatted_messages)



    return {
        "output": response.content
    }
