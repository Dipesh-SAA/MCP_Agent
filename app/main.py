from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router.chat_router import router as chat_router


app = FastAPI(
    root_path="/MCP_Agents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router, prefix="/api")
