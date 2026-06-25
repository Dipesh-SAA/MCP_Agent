import uuid

from langgraph.types import Command

from app.graph.nodes.agent2_node import agent2
# from app.graph.nodes.html_sql_node import html_sql_agent
from app.graph.nodes.requirement_agent_node import (
    requirement_verify_agent
)
from app.graph.workflow.workflow import (
    graph
)
from app.services.conversation.conversation_agent import (
    ConversationAgent
)
from app.services.orchestration.orchestration_agent import (
    OrchestrationAgent
)
from app.services.session.session_store import (
    get_state,
    save_state
)

class Orchestrator:

    @staticmethod
    def _new_session_state(session_id: str, token: str = None) -> dict:
        return {
            "session_id": session_id,
            "token": token,
            "current_step": "chat",
            "user_input": None,
            "requirements": None,
            "plan": None,
            "route": None,
            "output": None,
            "history": []
        }

    @staticmethod
    def _is_greeting(message: str) -> bool:
        text = message.lower().strip()
        greeting_words = ["hello", "hi", "hii", "hey"]

        # return message.lower().strip() in [
        #     "hello",
        #     "hi",
        #     "hii",
        #     "hey"
        # ]
        return any(
            text == word or text.startswith(f"{word} ")
            for word in greeting_words
        ) or text in ["can you help me", "help me"]

    @staticmethod
    def _is_approval(message: str) -> bool:
        return message.lower().strip() in [
            "approve",
            "continue",
            "next",
            "yes",
            "proceed"
        ]

    @staticmethod
    def _is_verification(message: str) -> bool:
        text = message.lower()
        actions = ["verify", "validate", "check", "review"]
        targets = [
            "requirement", "requirements", "req", "requir", 
            "requrent", "requrents", "output", "result", 
            "response", "code"
        ]

        return (
            any(word in text for word in actions) and 
            any(word in text for word in targets)
        )

    @staticmethod
    def _show_saved_state(state: dict, message: str) -> dict | None:
        text = message.lower().strip()

        if "show requirement" in text:
            return {
                "session_id": state["session_id"],
                "type": "requirements",
                "requirements": state.get("requirements")
            }

        if "show plan" in text:
            return {
                "session_id": state["session_id"],
                "type": "plan",
                "plan": state.get("plan")
            }

        if "show output" in text:
            return {
                "session_id": state["session_id"],
                "type": "output",
                "output": state.get("output")
            }

        return None

    @staticmethod
    async def _graph_values(config: dict) -> dict:
        graph_state = await graph.aget_state(config)
        return dict(graph_state.values)

    @staticmethod
    def _route_instruction(message: str) -> str:
        text = message.lower()

        wants_html = any(word in text for word in ["html", "ui", "frontend", "front end", "react", "css"])
        wants_sql = any(word in text for word in ["sql", "database", "table", "schema", "query"])

        if wants_html and wants_sql:
            return "html_sql"
        if wants_sql:
            return "sql"
        return "html"

    @staticmethod
    async def modify(session_id: str, message: str) -> dict:
        config = {"configurable": {"thread_id": session_id}}
        state = get_state(session_id)

        if not state:
            return {"error": "Session not found"}

        current_step = state.get("modify_target_step") or state.get("current_step")
        before_step = state.get("current_step")

        if current_step not in ["requirement_review", "plan_review"]:
            return {
                "session_id": session_id,
                "type": current_step,
                "message": "Nothing is waiting for modification."
            }

        # Resume the interrupted node with the user's feedback instead of "approve".
        # The requirement/planner node should branch on this resume value:
        # if resume == "approve" -> proceed forward
        # if it's a dict like {"action": "modify", "feedback": ...} -> regenerate and re-interrupt
        await graph.ainvoke(
            Command(resume={"action": "modify", "feedback": message}),
            config=config
        )

        state.update(await Orchestrator._graph_values(config))

        # Stay on the same step so the user reviews the refined version again
        state["current_step"] = current_step
        state.pop("modify_target_step", None)
        save_state(session_id, state)

        if current_step == "requirement_review":
            return {
                "session_id": session_id,
                "type": "requirement_review",
                "requirements": state.get("requirements"),
                "actions": ["approve", "modify"],
                "debug": {
                    "intent": "modify_feedback",
                    "before_step": before_step,
                    "after_step": current_step
                }
            }

        return {
            "session_id": session_id,
            "type": "plan_review",
            "plan": state.get("plan"),
            "actions": ["approve", "modify"],
            "debug": {
                "intent": "modify_feedback",
                "before_step": before_step,
                "after_step": current_step
            }
        }

    @staticmethod
    async def request_modify(session_id: str, message: str) -> dict:
        state = get_state(session_id)

        if not state:
            return {"error": "Session not found"}

        current_step = state.get("current_step")

        if current_step not in ["requirement_review", "plan_review"]:
            return {
                "session_id": session_id,
                "type": current_step,
                "message": "Nothing is waiting for modification."
            }

        state["modify_target_step"] = current_step
        state["current_step"] = f"{current_step}_modify_pending"
        save_state(session_id, state)

        if current_step == "requirement_review":
            return {
                "session_id": session_id,
                "type": "requirement_modify",
                "message": "Tell me what changes you want in the requirements.",
                "requirements": state.get("requirements"),
                "debug": {
                    "intent": "modify",
                    "before_step": current_step,
                    "after_step": state["current_step"]
                }
            }

        return {
            "session_id": session_id,
            "type": "plan_modify",
            "message": "Tell me what changes you want in the plan.",
            "plan": state.get("plan"),
            "debug": {
                "intent": "modify",
                "before_step": current_step,
                "after_step": state["current_step"]
            }
        }
    @staticmethod
    async def start_workflow(
        user_input: str,
        session_id: str = None,
        token: str = None
    ):

        if not session_id:
            session_id = str(
                uuid.uuid4()
            )

        config = {
            "configurable": {
                "thread_id": session_id
            }
        }

        # result = await graph.ainvoke(
        await graph.ainvoke(
            {
                "session_id": session_id,
                "token": token,
                "user_input": user_input
            },
            config=config
        )

        state = await Orchestrator._graph_values(
            config
        )

        state["session_id"] = session_id
        state["token"] = token
        state["current_step"] = "requirement_review"

        save_state(
            session_id,
            state
        )

        return {
            "session_id": session_id,
            # "result": result
            "type": "requirement_review",
            "requirements": state.get("requirements"),
            "actions": [
                "approve",
                "modify"
            ]
        }
    @staticmethod
    def _is_modify(message: str):
        text = message.lower().strip()
        return text == "modify" or text.startswith("modify")
############################################################## main chat function with Orchestrator agent ##############################################################
    @staticmethod
    async def handle_chat(
        message: str,
        session_id: str = None,
        token: str = None
    ):

        if not session_id:
            session_id = str(
                uuid.uuid4()
            )

            state = Orchestrator._new_session_state(
                session_id,
                token
            )

            save_state(
                session_id,
                state
            )

        else:
            state = get_state(
                session_id
            )

            if not state:
                return {
                    "error": "Session not found"
                }

            if token:
                state["token"] = token

        state.setdefault(
            "history",
            []
        )
        state["history"].append(
            {
                "role": "user",
                "message": message
            }
        )

        if state.get("current_step") in [
            "requirement_review_modify_pending",
            "plan_review_modify_pending"
        ]:
            return await Orchestrator.modify(
                session_id,
                message
            )

        decision = await OrchestrationAgent.decide(
            state,
            message
        )

        if decision["intent"] == "conversation":
            response = await ConversationAgent.respond(
                state,
                message
            )

            state["history"].append(
                {
                    "role": "assistant",
                    "message": response["message"]
                }
            )

            save_state(
                session_id,
                state
            )

            return response
        if decision["intent"] == "modify":
            return await Orchestrator.request_modify(
                session_id,
                message
            )

        if decision["intent"] == "reject":
            return await Orchestrator.request_modify(
                session_id,
                message
            )

        if decision["intent"] == "show":
            return Orchestrator._show_saved_state(
                state,
                message
            )

        if decision["intent"] == "approval":
            return await Orchestrator.approve(
                session_id
            )

        if decision["intent"] == "waiting_for_approval":
            return {
                "session_id": session_id,
                "type": state.get("current_step"),
                "message": "Please approve the current step before sending the next instruction."
            }

        if decision["intent"] == "verification":
            return await Orchestrator.verify_output(
                session_id,
                message
            )

        if decision["intent"] == "agent_instruction":
            return await Orchestrator.handle_message(
                session_id,
                message
            )

        if decision["intent"] == "sql_instruction":
            return await Orchestrator.handle_message(
                session_id,
                message
            )

        if decision["intent"] == "workflow":
            return await Orchestrator.start_workflow(
                message,
                session_id=session_id,
                token=state.get("token")
            )

        # Old direct orchestration logic kept below for reference.
        # Active routing now goes through OrchestrationAgent and ConversationAgent.
        if Orchestrator._is_greeting(
            message
        ):
            response = {
                "session_id": session_id,
                "type": "conversation",
                "message": "Hi, how can I help you?"
            }

            state["history"].append(
                {
                    "role": "assistant",
                    "message": response["message"]
                }
            )

            save_state(
                session_id,
                state
            )

            return response

        saved_response = Orchestrator._show_saved_state(
            state,
            message
        )

        if saved_response:
            return saved_response

        if Orchestrator._is_approval(
            message
        ):
            return await Orchestrator.approve(
                session_id
            )

        current_step = state.get(
            "current_step"
        )

        if current_step in [
            "requirement_review",
            "plan_review"
        ]:
            return {
                "session_id": session_id,
                "type": current_step,
                "message": "Please approve the current step before sending the next instruction."
            }

        if current_step == "chat" and state.get("plan"):
            return await Orchestrator.handle_message(
                session_id,
                message
            )

        return await Orchestrator.start_workflow(
            message,
            session_id=session_id
        )

    @staticmethod
    async def approve(
        session_id: str
    ):

        config = {
            "configurable": {
                "thread_id": session_id
            }
        }

        state = get_state(
            session_id
        )

        if not state:
            return {
                "error": "Session not found"
            }

        current_step = state.get(
            "current_step"
        )

        if current_step not in [
            "requirement_review",
            "plan_review"
        ]:
            return {
                "session_id": session_id,
                "type": current_step,
                "message": "Nothing is waiting for approval."
            }

        # result = await graph.ainvoke(
        await graph.ainvoke(
            Command(
                resume="approve"
            ),
            config=config
        )

        state.update(
            await Orchestrator._graph_values(
                config
            )
        )

        if current_step == "requirement_review":
            state["current_step"] = "plan_review"

            save_state(
                session_id,
                state
            )

            return {
                "session_id": session_id,
                "type": "plan_review",
                "plan": state.get("plan"),
                "actions": [
                    "approve",
                    "modify"
                ]
            }

        state["current_step"] = "completed"

        save_state(
            session_id,
            state
        )

        return {
            "session_id": session_id,
            "type": "execution_result",
            "plan": state.get("plan"),
            "api_response": state.get("api_response"),
            "a2_response": (state.get("api_response") or {}).get("final_response"),
            "a2_ok": (state.get("api_response") or {}).get("ok"),
            "message": "Plan approved and sent to A2 for Vibe execution."
        }

    @staticmethod
    async def verify_output(
        session_id: str,
        message: str
    ):

        state = get_state(
            session_id
        )

        if not state:
            return {
                "error": "Session not found"
            }

        if not state.get("output"):
            return {
                "session_id": session_id,
                "type": "verification_error",
                "message": "No generated output found to verify."
            }

        verify_state = {
            **state,
            "user_input": state.get("user_input") or state.get("last_instruction") or message,
            "requirements": state.get("requirements"),
            "output": state.get("output")
        }

        result = await requirement_verify_agent(
            verify_state
        )

        state.update(
            result
        )
        state["last_instruction"] = message
        state["current_step"] = "chat"

        save_state(
            session_id,
            state
        )

        return {
            "session_id": session_id,
            "type": "verification_result",
            "verified_output": state.get("verified_output"),
            "actions": [
                "send next instruction",
                "show output"
            ]
        }

    @staticmethod
    async def handle_message(
        session_id: str,
        message: str
    ):

        state = get_state(
            session_id
        )

        if not state:
            return {
                "error": "Session not found"
            }

        text = message.lower().strip()

        if text in [
            "approve",
            "continue",
            "next",
            "yes",
            "proceed"
        ]:
            return await Orchestrator.approve(
                session_id
            )

        if state.get("current_step") != "chat":
            return {
                "session_id": session_id,
                "type": state.get("current_step"),
                "message": "Please approve the current step before sending generation instructions."
            }

        if Orchestrator._is_verification(
            message
        ):

            return await Orchestrator.verify_output(
                session_id,
                message
            )

        # route = Orchestrator._route_instruction(
        #     message
        # )
        route = Orchestrator._route_instruction(
            message
        )

        generation_requirements = f"""
Approved Requirements:
{state.get("requirements")}

Approved Plan:
{state.get("plan")}

User Instruction:
{message}
"""

        agent_state = {
            **state,
            "route": route,
            "requirements": generation_requirements,
            "html_requirements": generation_requirements,
            "sql_requirements": generation_requirements
        }

        if route == "sql":
            result = await agent2(
                agent_state
            )

        # elif route == "html_sql":
        #     result = await html_sql_agent(
        #         agent_state
        #     )

        else:
            result = {
                "output": "Only SQL generation is available in the current workflow."
            }

        state.update(
            result
        )
        state["route"] = route
        state["last_instruction"] = message
        state["current_step"] = "chat"

        save_state(
            session_id,
            state
        )

        return {
            "session_id": session_id,
            "type": "generation_result",
            "route": route,
            "output": state.get("output"),
            "actions": [
                "send next instruction",
                "show output"
            ]
        }
