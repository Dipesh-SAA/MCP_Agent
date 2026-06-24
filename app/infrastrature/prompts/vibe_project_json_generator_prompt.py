from langchain_core.prompts import ChatPromptTemplate


vibe_project_json_generator_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a project planning agent.

Create a concise JSON implementation plan from the approved requirements.
Return only valid JSON.
""",
        ),
        (
            "human",
            """
Requirements:

{requirements}
""",
        ),
    ]
)
