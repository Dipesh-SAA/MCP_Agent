import json

from app.infrastrature.llm.llm_factory import llm
from app.infrastrature.prompts.orchestration_agent_prompt import (
    orchestration_agent_prompt
)


class OrchestrationAgent:

    @staticmethod
    def _is_conversation(
        message: str
    ):

        text = message.lower().strip()

        greeting_words = [
            "hello",
            "hi",
            "hii",
            "hey"
        ]

        return any(
            text == word
            or text.startswith(f"{word} ")
            for word in greeting_words
        ) or text in [
            "can you help me",
            "help me"
        ]

    @staticmethod
    def _is_approval(
        message: str
    ):

        return message.lower().strip() in [
            "approve",
            "continue",
            "next",
            "yes",
            "proceed"
        ]

    @staticmethod
    def _is_show(
        message: str
    ):

        text = message.lower().strip()

        return any(
            phrase in text
            for phrase in [
                "show requirement",
                "show plan",
                "show output"
            ]
        )

    @staticmethod
    def _is_verification(
        message: str
    ):

        text = message.lower()

        return any(
            word in text
            for word in [
                "verify",
                "validate",
                "check",
                "review"
            ]
        ) and any(
            word in text
            for word in [
                "requirement",
                "requirements",
                "req",
                "requir",
                "requrent",
                "requrents",
                "output",
                "result",
                "response",
                "code"
            ]
        )

    @staticmethod
    def _fallback_decide(
        state: dict,
        message: str
    ):

        current_step = state.get(
            "current_step"
        )

        if OrchestrationAgent._is_conversation(
            message
        ):
            return {
                "intent": "conversation"
            }

        if OrchestrationAgent._is_show(
            message
        ):
            return {
                "intent": "show"
            }

        if OrchestrationAgent._is_approval(
            message
        ):
            return {
                "intent": "approval"
            }

        if OrchestrationAgent._is_verification(
            message
        ):
            return {
                "intent": "verification"
            }

        if current_step in [
            "requirement_review",
            "plan_review"
        ]:
            return {
                "intent": "waiting_for_approval"
            }

        if current_step == "chat" and state.get("plan"):
            return {
                "intent": "agent_instruction"
            }

        return {
            "intent": "workflow"
        }
#############################################################. OrchestrationAgent code where llm is called #########################################################
    @staticmethod
    async def decide(
        state: dict,
        message: str
    ):

        formatted_messages = orchestration_agent_prompt.invoke(
            {
                "current_step": state.get("current_step"),
                "has_requirements": bool(state.get("requirements")),
                "has_plan": bool(state.get("plan")),
                "has_output": bool(state.get("output")),
                "message": message
            }
        )

        response = await llm.ainvoke(
            formatted_messages
        )

        content = response.content.strip()

        try:
            decision = json.loads(
                content
            )
        except json.JSONDecodeError:
            return OrchestrationAgent._fallback_decide(
                state,
                message
            )

        if decision.get("intent") not in [
            "conversation",
            "show",
            "approval",
            "waiting_for_approval",
            "verification",
            "agent_instruction",
            "workflow"
        ]:
            return OrchestrationAgent._fallback_decide(
                state,
                message
            )

        return decision
