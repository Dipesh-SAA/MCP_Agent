from app.infrastrature.llm.llm_factory import llm
from app.infrastrature.prompts.agent1_prompt import agent1_agent_prompt

# from utils.file_utils import save_markdown


async def agent1(state: dict):

    formatted_messages = agent1_agent_prompt.invoke(
        {
             "requirements": state["requirements"]
            
        }
    )

    response = await llm.ainvoke(formatted_messages)



    return {
        "output": response.content
    }
