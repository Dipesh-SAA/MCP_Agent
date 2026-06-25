import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router.chat_router import router as chat_router


load_dotenv()


def _csv_env(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


app = FastAPI(
    root_path="/MCP_Agents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_csv_env("CORS_ALLOW_ORIGINS", ["null"]),
    allow_origin_regex=os.getenv(
        "CORS_ALLOW_ORIGIN_REGEX",
        r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router, prefix="/api")
