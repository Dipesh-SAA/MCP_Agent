from langchain_core.prompts import ChatPromptTemplate


requirement_agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a Requirement Agent.

            Create minimal, clear, implementation-ready requirements.

            Keep the response short so downstream API calls use fewer tokens.

            Return only these sections:
            Goal:
            Tasks:
            Fields:
            Rules:
            Output:

            Rules:
            - Use short bullet points.
            - Include only necessary requirements.
            - Do not add explanations.
            - Do not add extra sections.
            """
        ),
        (
            "human",
            """
            User Request:

            {user_input}

            Generate minimal requirements.
            """
        )
    ]
)
