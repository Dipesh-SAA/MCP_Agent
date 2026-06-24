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

builder.add_edge(
    START,
    "requirement"
)

builder.add_edge(
    "requirement",
    "requirement_review"
)

builder.add_edge(
    "requirement_review",
    "planner"
)

builder.add_edge(
    "planner",
    "plan_review"
)

builder.add_edge(
    "plan_review",
    END
)

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)
