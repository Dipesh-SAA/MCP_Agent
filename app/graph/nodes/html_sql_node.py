from app.graph.nodes.agent1_node import agent1
from app.graph.nodes.agent2_node import agent2


async def html_sql_agent(state: dict):

    html_state = {
        **state,
        "requirements": state["html_requirements"]
    }
    sql_state = {
        **state,
        "requirements": state["sql_requirements"]
    }

    html_result = await agent1(html_state)
    sql_result = await agent2(sql_state)

    html_output = html_result["output"]
    sql_output = sql_result["output"]

    return {
        "html_output": html_output,
        "sql_output": sql_output,
        "output": f"HTML OUTPUT:\n{html_output}\n\nSQL OUTPUT:\n{sql_output}"
    }
