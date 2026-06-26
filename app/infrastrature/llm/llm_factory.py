import os
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class LLMFactory:

    @staticmethod
    def get_llm(
        provider: str,
        model: str = None,
        temperature: float = 0.0,
        **kwargs
    ):
        provider = provider.lower()

        if provider == "openai":
            return ChatOpenAI(
                model=model or "gpt-4o-mini",
                temperature=temperature,
                api_key=os.getenv("OPENAI_API_KEY"),
                **kwargs
            )

        elif provider == "ollama":
            return ChatOllama(
                model=model or "deepseek-r1:1.5b",
                temperature=temperature,
                **kwargs
            )

        elif provider == "mistral":
            return ChatMistralAI(
                model=model or "mistral-large-latest",
                temperature=temperature,
                api_key=os.getenv("MISTRAL_API_KEY"),
                **kwargs
            )

        elif provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model or "gemini-2.5-flash",
                temperature=temperature,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                **kwargs
            )

        raise ValueError(f"Unsupported provider: {provider}")
    



llm = LLMFactory.get_llm(
    provider=os.getenv("LLM_PROVIDER", "openai"),
)
