from app.infrastrature.llm.llm_factory import llm
from app.infrastrature.prompts.requirement_agent_prompt import requirement_agent_prompt

# from utils.file_utils import save_markdown


async def requrememt_agent(state: dict):

    formatted_messages = requirement_agent_prompt.invoke(
        {
            "user_input": state["user_input"],
            
        }
    )

    response = await llm.ainvoke(formatted_messages)



    return {
        "requirements": response.content
    }


async def requirement_split_agent(state: dict):

    requirements = state["requirements"]

    return {
        "html_requirements": f"HTML task only:\n{requirements}",
        "sql_requirements": f"SQL task only:\n{requirements}"
    }


async def requirement_verify_agent(state: dict):

    formatted_messages = requirement_agent_prompt.invoke(
        {
            "user_input": f"""
            Original User Request:
            {state["user_input"]}

            Requirements:
            {state["requirements"]}

            Final Output:
            {state["output"]}

            Verify if the final output satisfies the requirements.
            Return missing points if anything is missing.
            Return the verified final output if it is correct.
            """
        }
    )

    response = await llm.ainvoke(formatted_messages)

    return {
        "verified_output": response.content
    }
