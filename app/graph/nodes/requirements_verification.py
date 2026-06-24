from langgraph.types import interrupt


# async def requirement_review_node(state):

#     approval = interrupt(
#         {
#             "type": "requirement_review",
#             "requirements": state["requirements"],
#             "message": "Please review requirements."
#         }
#     )

#     return {
#         "approval_type": approval
#     }




# async def requirement_interrupt_node(state):

#     interrupt(
#         {
#             "type": "requirement_review",
#             "requirements": state["requirements"],
#             "message": "Please review and approve requirements."
#         }
#     )

#     return {
#         "current_step": "REQUIREMENT_APPROVED"
#     }

# requirements_verification.py


async def requirement_interrupt_node(state):
    resume = interrupt(
        {
            "type": "requirement_review",
            "requirements": state["requirements"],
            "message": "Please review and approve requirements."
        }
    )

    if isinstance(resume, dict) and resume.get("action") == "modify":
        return {"current_step": "REQUIREMENT_MODIFY", "modify_feedback": resume.get("feedback", "")}

    return {"current_step": "REQUIREMENT_APPROVED"}
