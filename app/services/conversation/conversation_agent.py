from app.infrastrature.llm.llm_factory import llm
from app.infrastrature.prompts.conversation_agent_prompt import (
    conversation_agent_prompt
)
from app.services.session.markdown_chat_logger import append_agent_chat


class ConversationAgent:

    @staticmethod
    async def respond(
        state: dict,
        message: str
    ):

        # text = message.lower().strip()

        # if any(
        #     text == word
        #     or text.startswith(f"{word} ")
        #     for word in [
        #         "hello",
        #         "hi",
        #         "hii",
        #         "hey"
        #     ]
        # ):
        #     response = "Hi, how can I help you?"

        # elif text in [
        #     "can you help me",
        #     "help me"
        # ]:
        #     response = "Yes, tell me what you want to build or generate."

        # else:
        #     response = "Tell me your requirement and I will help you with the next step."

        formatted_messages = conversation_agent_prompt.invoke(
            {
                "message": message
            }
        )

        response = await llm.ainvoke(
            formatted_messages
        )

        append_agent_chat(
            state.get("session_id"),
            "Conversation Agent",
            formatted_messages,
            response.content
        )

        return {
            "session_id": state["session_id"],
            "type": "conversation",
            "message": response.content
        }
