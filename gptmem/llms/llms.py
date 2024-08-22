import importlib
from typing import Any


class GenericLLMProvider:

    def __init__(self, llm):
        self.llm = llm

    @classmethod
    def from_provider(cls, provider: str, **kwargs: Any):
        if provider == "openai":
            cls._check_pkg("langchain_openai")
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(**kwargs)

        elif provider == "anthropic":
            cls._check_pkg("langchain_anthropic")
            from langchain_anthropic import ChatAnthropic

            # default anthropic
            if "model" not in kwargs:
                model = "claude-3-5-sonnet-20240620"
            else:
                model = kwargs["model_name"]
            llm = ChatAnthropic(**kwargs, model=model)

        elif provider == "mistralai":
            cls._check_pkg("langchain_mistralai")
            from langchain_mistralai import ChatMistralAI

            llm = ChatMistralAI(**kwargs)

        elif provider == "huggingface":
            cls._check_pkg("langchain_huggingface")
            from langchain_huggingface import ChatHuggingFace

            if "model" in kwargs or "model_name" in kwargs:
                model_id = kwargs.pop("model", None) or kwargs.pop("model_name", None)
                kwargs = {"model_id": model_id, **kwargs}
            llm = ChatHuggingFace(**kwargs)
        elif provider == "groq":
            cls._check_pkg("langchain_groq")
            from langchain_groq import ChatGroq

            llm = ChatGroq(**kwargs)
        elif provider == "bedrock":
            cls._check_pkg("langchain_aws")
            from langchain_aws import ChatBedrock

            if "model" in kwargs or "model_name" in kwargs:
                model_id = kwargs.pop("model", None) or kwargs.pop("model_name", None)
                kwargs = {"model_id": model_id, **kwargs}
            llm = ChatBedrock(**kwargs)
        else:
            _SUPPORTED_PROVIDERS = {
                "openai",
                "anthropic",
                "azure_openai",
                "cohere",
                "google_vertexai",
                "google_genai",
                "fireworks",
                "ollama",
                "together",
                "mistralai",
                "huggingface",
                "groq",
                "bedrock",
            }
            supported = ", ".join(_SUPPORTED_PROVIDERS)
            raise ValueError(
                f"Unsupported {provider=}.\n\nSupported model providers are: "
                f"{supported}"
            )

        return cls(llm)

    @staticmethod
    def _check_pkg(pkg: str) -> None:
        if not importlib.util.find_spec(pkg):
            pkg_kebab = pkg.replace("_", "-")
            raise ImportError(
                f"Unable to import {pkg_kebab}. Please install with "
                f"`pip install -U {pkg_kebab}`"
            )
