# from app.infrastrature.llm.llm_factory import llm
# from app.infrastrature.prompts.Execution_node_agent_prompt import Execution_node_agent_prompt

# from utils.file_utils import save_markdown


# async def Execution_node(state: dict):

#     formatted_messages = Execution_node_agent_prompt.invoke(
#         {
#              "requirements": state["requirements"]
            
#         }
#     )

#     response = await llm.ainvoke(formatted_messages)



#     return {
#         "output": response.content
#     }



from app.services.a2_client import call_a2_with_plan

async def create_project_node(state):
    api_response = await call_a2_with_plan(state)

    return {
        "api_response": api_response,
        "output": api_response.get("final_response")
    }
