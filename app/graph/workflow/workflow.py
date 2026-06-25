from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.checkpoint.memory import (
    MemorySaver
)

from app.schema.states import (
    AgentState
)

from app.graph.nodes.requirement_agent_node import (
    requrememt_agent
)

from app.graph.nodes.requirements_verification import (
    requirement_interrupt_node
)

from app.graph.nodes.planner_agent_node import (
    planner_json_agent_node,
    plan_interrupt_node
)

from app.graph.nodes.Execution_agent_node import create_project_node
# builder = StateGraph(
#     AgentState
# )

# builder.add_node(
#     "requirement",
#     requrememt_agent
# )

# builder.add_node(
#     "requirement_review",
#     requirement_interrupt_node
# )

# builder.add_node(
#     "planner",
#     planner_json_agent_node
# )

# builder.add_node(
#     "plan_review",
#     plan_interrupt_node
# )

# builder.add_edge(
#     START,
#     "requirement"
# )

# builder.add_edge(
#     "requirement",
#     "requirement_review"
# )

# builder.add_edge(
#     "requirement_review",
#     "planner"
# )

# builder.add_edge(
#     "planner",
#     "plan_review"
# )

# builder.add_edge(
#     "plan_review",
#     END
# )

# memory = MemorySaver()

# graph = builder.compile(
#     checkpointer=memory
# )


#########################################VERSION2#################################################
# builder = StateGraph(
#     AgentState
# )

# builder.add_node(
#     "requirement",
#     requrememt_agent
# )

# builder.add_node(
#     "requirement_review",
#     requirement_interrupt_node
# )

# builder.add_node(
#     "planner",
#     planner_json_agent_node
# )

# builder.add_node(
#     "plan_review",
#     plan_interrupt_node
# )

# builder.add_node(
#     "create_project",
#     create_project_node
# )

# builder.add_edge(
#     START,
#     "requirement"
# )

# builder.add_edge(
#     "requirement",
#     "requirement_review"
# )

# builder.add_edge(
#     "requirement_review",
#     "planner"
# )

# builder.add_edge(
#     "planner",
#     "plan_review"
# )

# builder.add_edge(
#     "plan_review",
#     "create_project"
# )

# builder.add_edge(
#     "create_project",
#     END
# )

# memory = MemorySaver()

# graph = builder.compile(
#     checkpointer=memory
# )
#########################################VERSION2#################################################



#########################################VERSION 3#################################################

builder = StateGraph(
    AgentState
)

builder.add_node(
    "requirement",
    requrememt_agent
)

builder.add_node(
    "requirement_review",
    requirement_interrupt_node
)

builder.add_node(
    "planner",
    planner_json_agent_node
)

builder.add_node(
    "plan_review",
    plan_interrupt_node
)

builder.add_node(
    "create_project",
    create_project_node
)

builder.add_edge(
    START,
    "requirement"
)

builder.add_edge(
    "requirement",
    "requirement_review"
)

# --- CHANGED: conditional edge instead of a straight edge ---
def route_after_requirement_review(state):
    if state.get("current_step") == "REQUIREMENT_MODIFY":
        return "requirement"   # loop back, regenerate requirements
    return "planner"           # approved, continue forward

builder.add_conditional_edges(
    "requirement_review",
    route_after_requirement_review,
    {
        "requirement": "requirement",
        "planner": "planner"
    }
)

builder.add_edge(
    "planner",
    "plan_review"
)

# --- CHANGED: conditional edge instead of a straight edge ---
def route_after_plan_review(state):
    if state.get("current_step") == "PLAN_MODIFY":
        return "planner"        # loop back, regenerate plan
    return "create_project"     # approved, continue forward

builder.add_conditional_edges(
    "plan_review",
    route_after_plan_review,
    {
        "planner": "planner",
        "create_project": "create_project"
    }
)

builder.add_edge(
    "create_project",
    END
)

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)

# graph.compile()