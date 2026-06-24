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



import httpx

async def create_project_node(state):

    payload = state["plan"]
    headers = {}

    token = state.get("token")

    if token:
        headers["Authorization"] = token

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/project/create",
            json=payload,
            headers=headers
        )

    return {
        "api_response": {
            "status_code": response.status_code,
            "body": response.json()
        }
    }
