# Code Documentation

This document explains the Python application source under `app/`. It excludes generated files such as `venv/`, `.DS_Store`, and `__pycache__/`.

## Project Summary

This project is a FastAPI backend that exposes AI code-generation endpoints. The application takes a user request, converts it into requirements, decides whether the work belongs to a frontend HTML agent, a SQL agent, or both, generates output with an LLM, and then verifies the generated output.

There are two main usage styles:

- `/api/generate`: runs the full LangGraph workflow automatically.
- `/api/chat`, `/api/chat/action`, and `/api/chat/message`: run a step-by-step chat workflow with approval checkpoints.

## Main Flow

1. A user sends a build request.
2. The requirement agent rewrites the request into short implementation-ready requirements.
3. The planner agent routes the task to `html`, `sql`, or `html_sql`.
4. The selected generation agent creates the output.
5. The verification agent checks whether the generated output satisfies the requirements.
6. For chat mode, the state is stored in memory by session ID.

## Important Concepts

- `state`: A dictionary passed between agents. It carries `user_input`, `requirements`, `route`, outputs, and workflow progress.
- `route`: The planner decision. Valid values are `html`, `sql`, and `html_sql`.
- `session_id`: A UUID used by chat mode to resume a multi-step workflow.
- `llm`: A configured LangChain chat model created in `llm_factory.py`.

## File Tree

```text
app/
  main.py
  api/router/
    agent_routes.py
    chat_router.py
  graph/
    nodes/
      agent1_node.py
      agent2_node.py
      html_sql_node.py
      planner_agent_node.py
      requirement_agent_node.py
    routes/
      planner_routes.py
    workflow/
      workflow.py
  infrastrature/
    llm/
      llm_factory.py
    prompts/
      agent1_prompt.py
      agent2_prompt.py
      planner_agent_prompt.py
      requirement_agent_prompt.py
  schema/
    events.py
    request.py
    states.py
  services/
    conversation/
      approval_handler.py
      artifact_handler.py
      conversation_router.py
      greeting_handler.py
      requirement_handler.py
    session/
      session_store.py
    streaming/
      chat_stream.py
```

## `app/main.py`

Purpose: Creates the FastAPI app and registers API routers.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `FastAPI`, the framework class used to create the web application. |
| 3 | Imports the agent workflow router as `agent_router`. |
| 5 | Imports the chat workflow router as `chat_router`. |
| 6 | Creates the FastAPI application instance. |
| 8 | Registers agent routes under the `/api` prefix. This creates endpoints like `/api/generate`. |
| 9 | Registers chat routes under the `/api` prefix. This creates endpoints like `/api/chat`. |

## `app/api/router/agent_routes.py`

Purpose: Defines the automatic generation endpoint.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `APIRouter` to define a group of FastAPI routes. |
| 3 | Imports the compiled LangGraph workflow named `graph`. |
| 4 | Imports `UserRequest`, the request body schema for user input. |
| 6 | Creates the router object used by `main.py`. |
| 9 | Registers a POST endpoint at `/generate`. With the `/api` prefix, the full path is `/api/generate`. |
| 10-12 | Defines the async route handler. FastAPI validates the request body as `UserRequest`. |
| 14-18 | Calls `graph.ainvoke()` asynchronously with an initial state containing `user_input`. |
| 20 | Returns the final graph state/result to the client. |
| 23-30 | Commented-out streaming endpoint code. It shows an older or planned design for server-sent events. |

## `app/api/router/chat_router.py`

Purpose: Defines the step-by-step chat API.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `uuid` to create unique session IDs. |
| 3 | Imports FastAPI `APIRouter`. |
| 5-8 | Imports node functions used directly by chat mode. |
| 9-12 | Imports requirement-related node functions. `requrememt_agent` has a typo in its name but is used consistently. |
| 13-17 | Imports Pydantic request schemas for chat endpoints. |
| 18 | Imports the approval workflow handler. |
| 19-24 | Imports handlers that return saved artifacts such as requirements, HTML, SQL, or combined output. |
| 25-28 | Imports intent detection and the `Intent` enum. |
| 29 | Imports greeting response handler. |
| 30 | Imports handler for starting a new requirement from a chat message. |
| 31-34 | Imports session store helpers. `get_state` is imported but not used in this file. |
| 37 | Creates the router object. |
| 40 | Registers POST `/chat`. Full path: `/api/chat`. |
| 41-43 | Defines the async function for starting a new chat workflow. |
| 45 | Creates a new UUID session ID. |
| 47-55 | Builds the initial session state. It starts at `current_step = "requirement"` and stores empty output fields. |
| 57-59 | Calls the requirement agent to turn raw user input into structured requirements. |
| 61-63 | Merges the requirement result into `state`. |
| 65 | Moves the workflow to the `requirement_review` checkpoint. |
| 67-70 | Saves the state in memory using the session ID. |
| 72-80 | Returns the session ID, generated requirements, and available actions to the client. |
| 83 | Registers POST `/chat/action`. Full path: `/api/chat/action`. |
| 84-86 | Defines the handler for explicit action requests. |
| 88-91 | Only supports `approve` at the moment. Other actions return a message. |
| 93-95 | Delegates approval handling to `handle_approval()`. |
| 98 | Registers POST `/chat/message`. Full path: `/api/chat/message`. |
| 99-101 | Defines a handler for free-text chat messages. |
| 103-105 | Detects the user's intent from the message text. |
| 107-108 | If the message is a greeting, returns a greeting response. |
| 110-113 | If the message is a new requirement, starts a new requirement workflow. |
| 115-118 | Requires `session_id` for commands that operate on an existing workflow. |
| 120-123 | If intent is approval, advances the workflow. |
| 125-128 | If intent asks for requirements, returns saved requirements. |
| 130-133 | If intent asks for HTML, returns saved HTML output. |
| 135-138 | If intent asks for SQL, returns saved SQL output. |
| 140-143 | If intent asks for output, returns the combined output. |
| 145-159 | If intent is help, returns available command examples. |
| 161-164 | Fallback for unrecognized requests. In practice, most non-command messages become `NEW_REQUIREMENT`. |

## `app/graph/nodes/agent1_node.py`

Purpose: Frontend generation agent.

| Lines | Explanation |
| --- | --- |
| 1 | Imports the configured LLM instance. |
| 2 | Imports the frontend prompt template. |
| 4 | Commented-out import for a file utility that is not currently used. |
| 7 | Defines async function `agent1`, receiving the shared workflow state. |
| 9-14 | Formats the frontend prompt by injecting `state["requirements"]`. |
| 16 | Sends the formatted messages to the LLM asynchronously. |
| 20-22 | Returns a dictionary containing the generated frontend code in `output`. |

## `app/graph/nodes/agent2_node.py`

Purpose: SQL generation agent.

| Lines | Explanation |
| --- | --- |
| 1 | Imports the configured LLM instance. |
| 2 | Imports the SQL prompt template. |
| 4 | Commented-out import for a file utility that is not currently used. |
| 7 | Defines async function `agent2`, receiving the shared workflow state. |
| 9-14 | Formats the SQL prompt by injecting `state["requirements"]`. |
| 16 | Sends the formatted messages to the LLM asynchronously. |
| 20-22 | Returns a dictionary containing generated SQL in `output`. |

## `app/graph/nodes/html_sql_node.py`

Purpose: Runs both HTML and SQL agents and combines their outputs.

| Lines | Explanation |
| --- | --- |
| 1 | Imports the frontend agent. |
| 2 | Imports the SQL agent. |
| 5 | Defines async `html_sql_agent`, receiving shared state. |
| 7-10 | Creates `html_state` by copying the current state and replacing `requirements` with `html_requirements`. |
| 11-14 | Creates `sql_state` by copying the current state and replacing `requirements` with `sql_requirements`. |
| 16 | Runs the frontend agent. |
| 17 | Runs the SQL agent after the frontend agent completes. |
| 19 | Extracts the frontend output. |
| 20 | Extracts the SQL output. |
| 22-26 | Returns separate `html_output`, separate `sql_output`, and a combined `output` string. |

Important note: This function expects `state["html_requirements"]` and `state["sql_requirements"]` to already exist. In graph mode, `requirement_split_agent` creates those fields first. In chat approval mode, this split step is currently missing before `html_sql_agent` is called.

## `app/graph/nodes/planner_agent_node.py`

Purpose: Determines which generation route should handle the requirements.

| Lines | Explanation |
| --- | --- |
| 1 | Imports the configured LLM. |
| 2 | Imports the planner prompt template. |
| 4-22 | Commented-out older planner implementation. |
| 25 | Defines async `planner_agent_node`. |
| 27-31 | Formats the planner prompt with `state["requirements"]`. |
| 33 | Sends the prompt to the LLM. |
| 35 | Normalizes the model response by trimming whitespace, lowercasing it, and removing spaces. |
| 37-38 | Converts `html,sql` into `html_sql` in case the model returns a comma-separated route. |
| 40-42 | Returns the selected route in a dictionary. |

## `app/graph/nodes/requirement_agent_node.py`

Purpose: Creates requirements, splits combined requirements, and verifies final output.

| Lines | Explanation |
| --- | --- |
| 1 | Imports the configured LLM. |
| 2 | Imports the requirement prompt template. |
| 4 | Commented-out import for a file utility that is not used. |
| 7 | Defines async `requrememt_agent`. The name contains a spelling mistake. |
| 9-14 | Formats the requirement prompt with `state["user_input"]`. |
| 16 | Sends the prompt to the LLM asynchronously. |
| 20-22 | Returns generated requirements as `requirements`. |
| 25 | Defines async `requirement_split_agent`. |
| 27 | Reads combined requirements from state. |
| 29-32 | Creates two requirement strings: one for HTML and one for SQL. This is a simple prefix-based split, not a semantic split. |
| 35 | Defines async `requirement_verify_agent`. |
| 37-54 | Builds a verification prompt using the original request, requirements, and final output. |
| 56 | Sends the verification prompt to the LLM. |
| 58-60 | Returns the verification result as `verified_output`. |

## `app/graph/routes/planner_routes.py`

Purpose: Provides the conditional route function for LangGraph.

| Lines | Explanation |
| --- | --- |
| 1 | Defines `planner_router`, which receives the graph state. |
| 2 | Returns `state["route"]`. LangGraph uses this value to choose the next node. |

## `app/graph/workflow/workflow.py`

Purpose: Builds and compiles the LangGraph workflow used by `/api/generate`.

| Lines | Explanation |
| --- | --- |
| 1-5 | Imports LangGraph workflow primitives: `StateGraph`, `START`, and `END`. |
| 6 | Commented-out import of `AgentState`. The active import is on line 22. |
| 8-10 | Imports the planner node. |
| 12-16 | Imports requirement, split, and verification nodes. |
| 18 | Imports frontend generation node. |
| 19 | Imports SQL generation node. |
| 20 | Imports combined HTML/SQL generation node. |
| 22 | Imports the state type definition. |
| 23 | Imports the conditional router function. |
| 27-29 | Creates a `StateGraph` using `AgentState` as the state schema. |
| 31-34 | Adds the `planner` node. |
| 36-39 | Adds the `requirement` node. |
| 40-43 | Adds the `html` node. |
| 44-47 | Adds the `sql` node. |
| 48-51 | Adds the `split_requirement` node. |
| 52-55 | Adds the `html_sql` node. |
| 56-59 | Adds the `verify` node. |
| 60-63 | Connects the graph start to the requirement node. |
| 65-68 | Commented-out old edge from planner to requirement. |
| 70-73 | Connects requirement generation to planning. |
| 75-83 | Adds conditional edges from `planner`. If route is `html`, go to `html`; if `sql`, go to `sql`; if `html_sql`, go to `split_requirement`. |
| 84 | Connects split requirements to the combined HTML/SQL node. |
| 85 | Connects HTML generation to verification. |
| 86 | Connects SQL generation to verification. |
| 87 | Connects combined HTML/SQL generation to verification. |
| 88 | Connects verification to graph end. |
| 90 | Compiles the builder into an executable graph. |

## `app/infrastrature/llm/llm_factory.py`

Purpose: Centralizes LLM provider configuration.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `os` for reading environment variables. |
| 2 | Imports OpenAI chat model wrapper. |
| 3 | Imports Ollama chat model wrapper. |
| 4 | Imports Mistral chat model wrapper. |
| 5 | Imports Google Gemini chat model wrapper. |
| 6 | Imports `load_dotenv` for reading `.env` files. |
| 8 | Loads environment variables from `.env`. |
| 10 | Defines the `LLMFactory` class. |
| 12 | Declares `get_llm` as a static method, so it can be called without creating an instance. |
| 13-18 | Defines parameters: provider name, optional model, temperature, and extra keyword arguments. |
| 19 | Normalizes the provider name to lowercase. |
| 21-27 | If provider is `openai`, returns `ChatOpenAI` with model default `gpt-4o-mini` and `OPENAI_API_KEY`. |
| 29-34 | If provider is `ollama`, returns `ChatOllama` with model default `deepseek-r1:1.5b`. |
| 36-42 | If provider is `mistral`, returns `ChatMistralAI` with model default `mistral-large-latest` and `MISTRAL_API_KEY`. |
| 44-50 | If provider is `gemini`, returns `ChatGoogleGenerativeAI` with model default `gemini-2.5-flash` and `GOOGLE_API_KEY`. |
| 52 | Raises an error for unsupported providers. |
| 57-59 | Creates the global `llm` object using the Mistral provider. Every agent imports and uses this object. |

## `app/infrastrature/prompts/agent1_prompt.py`

Purpose: Defines the frontend code-generation prompt.

| Lines | Explanation |
| --- | --- |
| 1 | Imports LangChain `ChatPromptTemplate`. |
| 4 | Creates `agent1_agent_prompt` from chat messages. |
| 5 | Starts the list of prompt messages. |
| 6-21 | Defines the system message. It tells the model to act as a senior frontend developer and return only production-ready code. |
| 22-31 | Defines the human message. It injects `{requirements}` and asks for frontend implementation. |
| 32-33 | Closes the list and prompt construction. |

## `app/infrastrature/prompts/agent2_prompt.py`

Purpose: Defines the SQL generation prompt.

| Lines | Explanation |
| --- | --- |
| 1 | Imports LangChain `ChatPromptTemplate`. |
| 4 | Creates `agent2_agent_prompt` from chat messages. |
| 5 | Starts the list of prompt messages. |
| 6-21 | Defines the system message. It tells the model to act as a senior database engineer and return only SQL code. |
| 22-31 | Defines the human message. It injects `{requirements}` and asks for SQL implementation. |
| 32-33 | Closes the list and prompt construction. |

## `app/infrastrature/prompts/planner_agent_prompt.py`

Purpose: Defines the routing prompt used by the planner agent.

| Lines | Explanation |
| --- | --- |
| 1 | Imports LangChain `ChatPromptTemplate`. |
| 4 | Creates `planner_agent_prompt` from chat messages. |
| 5 | Starts the list of prompt messages. |
| 6-75 | Defines the system message. It explains available agents and strict routing rules. |
| 16-30 | Describes the `html` route responsibilities. |
| 31-42 | Describes the `sql` route responsibilities. |
| 43-48 | Defines when to return `html`, `sql`, or `html_sql`. |
| 49-64 | Provides routing examples. |
| 66-73 | Requires the model to return only one route value with no markdown or explanation. |
| 76-85 | Defines the human message. It injects `{requirements}` and asks for the correct route. |
| 86-87 | Closes the list and prompt construction. |

## `app/infrastrature/prompts/requirement_agent_prompt.py`

Purpose: Defines the prompt that rewrites raw user requests into concise requirements.

| Lines | Explanation |
| --- | --- |
| 1 | Imports LangChain `ChatPromptTemplate`. |
| 4 | Creates `requirement_agent_prompt` from chat messages. |
| 5 | Starts the list of prompt messages. |
| 6-28 | Defines the system message. It instructs the model to produce short implementation-ready requirements. |
| 15-20 | Defines the exact output sections: `Goal`, `Tasks`, `Fields`, `Rules`, and `Output`. |
| 22-26 | Adds constraints: short bullets, only necessary requirements, no explanations, and no extra sections. |
| 29-38 | Defines the human message. It injects `{user_input}` and asks for minimal requirements. |
| 39-40 | Closes the list and prompt construction. |

## `app/schema/events.py`

Purpose: Defines the shape of streaming events.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `TypedDict` for dictionary type definitions. |
| 4 | Defines `StreamEvent`, a typed dictionary. |
| 5 | Declares a `type` string field, such as `status`, `output`, or `error`. |
| 6 | Declares a `message` string field. |

## `app/schema/request.py`

Purpose: Defines FastAPI request body schemas.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `Optional` for fields that may be omitted. |
| 3 | Imports Pydantic `BaseModel`. |
| 6-7 | Defines `UserRequest` with required `user_input`. Used by `/api/generate`. |
| 12-13 | Defines `ChatRequest` with required `user_input`. Used by `/api/chat`. |
| 17-19 | Defines `ChatActionRequest` with required `session_id` and `action`. Used by `/api/chat/action`. |
| 21-25 | Defines `ChatMessageRequest`. `session_id` is optional, and `message` is required. Used by `/api/chat/message`. |

## `app/schema/states.py`

Purpose: Defines the workflow state structure.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `Optional` and `TypedDict`. |
| 5-23 | Commented-out older `AgentState` definition. |
| 31 | Defines active `AgentState`. |
| 32 | `session_id`: chat session identifier. |
| 34 | `current_step`: current checkpoint in chat workflow. |
| 36 | `user_input`: original user request. |
| 38 | `requirements`: generated implementation requirements. |
| 40 | `route`: planner decision. |
| 42 | `html_requirements`: requirements passed specifically to the HTML agent. |
| 44 | `sql_requirements`: requirements passed specifically to the SQL agent. |
| 46 | `output`: generated output for single-agent flow or combined output for dual-agent flow. |
| 48 | `html_output`: separate frontend output for dual-agent flow. |
| 50 | `sql_output`: separate SQL output for dual-agent flow. |
| 52 | `verified_output`: final verification result. |

Important note: `session_id` and `current_step` are required in this type, but `/api/generate` starts the graph with only `user_input`. Depending on LangGraph's runtime type handling, this may be acceptable at runtime or may need optional fields.

## `app/services/conversation/approval_handler.py`

Purpose: Advances the chat workflow when the user approves each step.

| Lines | Explanation |
| --- | --- |
| 1-5 | Imports generation, planning, combined generation, and verification node functions. |
| 6-9 | Imports session state helpers. |
| 12-14 | Defines async `handle_approval` with a session ID. |
| 16-18 | Loads the saved state for the session. |
| 20-23 | Returns an error if the session does not exist. |
| 25 | Reads the current workflow step. |
| 27 | Checks whether the user is approving generated requirements. |
| 29-31 | Runs the planner node. |
| 33-35 | Merges planner result into state. |
| 37 | Moves workflow to `planner_review`. |
| 39-42 | Saves updated state. |
| 44-52 | Returns planner decision and approval actions. |
| 54 | Checks whether the user is approving the planner route. |
| 56 | Reads the selected route. |
| 58-62 | If route is `html`, runs frontend generation. |
| 64-68 | If route is `sql`, runs SQL generation. |
| 70-74 | Otherwise, runs combined HTML/SQL generation. |
| 76-78 | Merges generated output into state. |
| 80 | Moves workflow to `generation_review`. |
| 82-85 | Saves updated state. |
| 87-95 | Returns generated output and approval actions. |
| 97 | Checks whether the user is approving generated output. |
| 99-101 | Runs verification agent. |
| 103-105 | Merges verification result into state. |
| 107 | Moves workflow to `verification_review`. |
| 109-112 | Saves updated state. |
| 114-122 | Returns verification output and approval actions. |
| 124 | Checks whether final verification is approved. |
| 126 | Marks workflow as completed. |
| 128-131 | Saves completed state. |
| 133-137 | Returns a completion response. |
| 139-141 | Fallback for invalid workflow step values. |

Important note: If route is `html_sql`, this handler calls `html_sql_agent(state)` without first calling `requirement_split_agent(state)`. That means `html_sql_agent` may fail because it expects `html_requirements` and `sql_requirements`.

## `app/services/conversation/artifact_handler.py`

Purpose: Returns saved workflow artifacts from the session store.

| Lines | Explanation |
| --- | --- |
| 1-3 | Imports `get_state`. |
| 6-8 | Defines `handle_show_requirements`. |
| 10 | Loads state by session ID. |
| 12-15 | Returns saved `requirements`. |
| 18-20 | Defines `handle_show_html`. |
| 22 | Loads state by session ID. |
| 24-27 | Returns saved `html_output`. |
| 30-32 | Defines `handle_show_sql`. |
| 34 | Loads state by session ID. |
| 36-39 | Returns saved `sql_output`. |
| 42-44 | Defines `handle_show_output`. |
| 46 | Loads state by session ID. |
| 48-51 | Returns saved combined/single `output`. |

Important note: These functions assume the session exists. If `get_state()` returns `None`, `state.get(...)` will raise an exception.

## `app/services/conversation/conversation_router.py`

Purpose: Converts free-text chat messages into known intents.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `Enum`. |
| 4 | Defines `Intent` enum as strings. |
| 5 | `GREETING`: greeting messages. |
| 6 | `APPROVE`: approval/continue messages. |
| 7 | `SHOW_REQUIREMENTS`: request to display requirements. |
| 8 | `SHOW_HTML`: request to display HTML. |
| 9 | `SHOW_SQL`: request to display SQL. |
| 10 | `SHOW_OUTPUT`: request to display output. |
| 11 | `HELP`: help command. |
| 12 | `NEW_REQUIREMENT`: any new build request. |
| 15 | Defines `detect_intent`. |
| 17 | Normalizes message text to lowercase and trims spaces. |
| 19-26 | Maps approval words like `approve`, `continue`, `next`, `yes`, and `proceed` to `APPROVE`. |
| 28-33 | Maps `hello`, `hi`, and `hey` to `GREETING`. |
| 35-36 | Detects messages containing `show requirement`. |
| 38-39 | Detects messages containing `show html`. |
| 41-42 | Detects messages containing `show sql`. |
| 44-45 | Detects messages containing `show output`. |
| 47-48 | Detects exact `help`. |
| 50 | Defaults everything else to `NEW_REQUIREMENT`. |
| 53-117 | Commented-out older intent detection implementation with additional variants. |

## `app/services/conversation/greeting_handler.py`

Purpose: Returns a greeting response.

| Lines | Explanation |
| --- | --- |
| 1 | Defines `handle_greeting`. |
| 3-8 | Returns a dictionary with type `message` and a greeting prompt. |
| 11-26 | Commented placeholders for future handlers. |

## `app/services/conversation/requirement_handler.py`

Purpose: Starts a new chat workflow from a user message.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `uuid` for session ID creation. |
| 3-5 | Imports `save_state`. |
| 7-9 | Imports the requirement agent. |
| 12-14 | Defines async `handle_new_requirement`. |
| 16 | Creates a new UUID session ID. |
| 18-29 | Builds the initial session state with user input and empty result fields. |
| 31-33 | Calls the requirement agent. |
| 35-37 | Merges generated requirements into state. |
| 39 | Moves workflow to `requirement_review`. |
| 41-44 | Saves state by session ID. |
| 46-57 | Returns session ID, requirement review data, and actions. |

## `app/services/session/session_store.py`

Purpose: Provides a simple in-memory session database.

| Lines | Explanation |
| --- | --- |
| 1 | Imports `Dict` for type annotation. |
| 4 | Creates global `SESSIONS`, a dictionary keyed by session ID. |
| 7-10 | Defines `save_state`. |
| 11 | Stores the whole state under the session ID. |
| 14-17 | Defines `get_state` and returns a saved state or `None`. |
| 20-23 | Defines `update_state`. |
| 24-25 | Returns `None` if the session does not exist. |
| 27 | Merges updates into the saved state. |
| 29 | Returns the updated state. |
| 32-36 | Defines `delete_state` and removes a session if present. |
| 39-42 | Defines `session_exists` and returns whether the session ID is present. |

Important note: This store is in memory only. All sessions are lost when the server restarts, and it is not safe for multi-process deployment.

## `app/services/streaming/chat_stream.py`

Purpose: Implements a server-sent-events style streaming workflow. The route that uses it is currently commented out in `agent_routes.py`.

| Lines | Explanation |
| --- | --- |
| 3 | Imports `json` to serialize events. |
| 5-9 | Imports requirement, split, and verification agents. |
| 11-13 | Imports planner agent. |
| 15-17 | Imports frontend agent. |
| 19-21 | Imports SQL agent. |
| 23-25 | Imports combined HTML/SQL agent. |
| 28-29 | Defines `event`, which formats a Python dictionary as a server-sent event string. |
| 32 | Defines async generator `stream_chat`. |
| 34-36 | Creates initial state with `user_input`. |
| 38 | Starts a `try` block so failures can be streamed as error events. |
| 40-47 | Emits a status event saying requirements are being generated. |
| 49 | Calls the requirement agent. |
| 51 | Merges requirements into state. |
| 53-56 | Emits a `requirements` event. |
| 58-65 | Emits a status event saying planning is running. |
| 67 | Calls planner agent. |
| 69 | Merges planner result into state. |
| 71 | Reads route. |
| 73-76 | Emits a `route` event. |
| 78-80 | Begins routing section. |
| 82-90 | If route is `html`, emits frontend status and runs frontend agent. |
| 91-99 | If route is `sql`, emits SQL status and runs SQL agent. |
| 100-115 | If route is `html_sql`, emits split status, splits requirements, emits generation status, and runs combined agent. |
| 117-124 | If route is unknown, emits an error event and stops. |
| 126 | Merges generated output into state. |
| 128-135 | Emits generated output. |
| 137-144 | Emits verification status. |
| 146 | Calls verification agent. |
| 148 | Merges verification result into state. |
| 150-153 | Emits verification result. |
| 155-162 | Emits completed event. |
| 164-169 | Catches exceptions and emits an error event with the exception message. |

## API Reference

### `POST /api/generate`

Runs the full graph workflow automatically.

Request:

```json
{
  "user_input": "Build a customer dashboard and SQL schema"
}
```

High-level response fields may include:

```json
{
  "user_input": "...",
  "requirements": "...",
  "route": "html_sql",
  "html_requirements": "...",
  "sql_requirements": "...",
  "html_output": "...",
  "sql_output": "...",
  "output": "...",
  "verified_output": "..."
}
```

### `POST /api/chat`

Starts a chat workflow and returns requirements for approval.

Request:

```json
{
  "user_input": "Create a customer dashboard"
}
```

Response:

```json
{
  "session_id": "uuid",
  "type": "requirement_review",
  "requirements": "...",
  "actions": ["approve", "modify"]
}
```

### `POST /api/chat/action`

Advances an existing chat workflow. Only `approve` is currently supported.

Request:

```json
{
  "session_id": "uuid",
  "action": "approve"
}
```

### `POST /api/chat/message`

Accepts free-text messages and detects intent.

Examples:

```json
{
  "message": "hello"
}
```

```json
{
  "session_id": "uuid",
  "message": "approve"
}
```

```json
{
  "session_id": "uuid",
  "message": "show output"
}
```

## Known Issues And Risks

- `requrememt_agent` is misspelled. The code works because imports use the same spelling, but it is confusing.
- The folder name `infrastrature` is misspelled. It works as long as imports match, but it should probably be `infrastructure`.
- Chat approval mode does not split requirements before calling `html_sql_agent`, so the `html_sql` route can fail with missing `html_requirements` or `sql_requirements`.
- Artifact handlers do not handle missing sessions and can crash when `get_state()` returns `None`.
- The session store is in memory only, so sessions disappear on restart.
- `modify` is returned as an available action, but `/chat/action` does not support it.
- The global LLM provider is hardcoded to Mistral.
- The streaming implementation exists, but the route that exposes it is commented out.
- `AgentState` marks `session_id` and `current_step` as required, but graph mode starts without those fields.

## How To Explain This Code To ChatGPT

You can paste this summary:

```text
This is a FastAPI app that uses LangGraph and LangChain LLM wrappers to generate code. A user request first goes to a requirement agent, which creates concise requirements. Then a planner agent chooses one route: html, sql, or html_sql. The html route calls a frontend-generation prompt, the sql route calls a SQL-generation prompt, and the html_sql route splits requirements and calls both. Finally, a verification agent checks the output. The app supports an automatic endpoint `/api/generate` and a chat workflow with sessions and approval steps through `/api/chat`, `/api/chat/action`, and `/api/chat/message`.
```

