import questionary
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI
from langchain_ollama import ChatOllama


MODELS = {
    "Gemini 3.5 Flash": {
        "provider": "gemini",
        "model": "gemini-3.5-flash",
    },
    "Grok 4.7": {
        "provider": "xai",
        "model": "grok-4.7",
    },
    "Qwen 3 8B": {
        "provider": "ollama",
        "model": "qwen3:8b",
    },
}


def select_model():
    model_name = questionary.select(
        "Select a model:",
        choices=list(MODELS.keys()),
        instruction="Use ↑/↓ to navigate and Enter to select",
    ).ask()

    if model_name is None:
        raise KeyboardInterrupt

    return MODELS[model_name], model_name



def create_llm(model_config, gemini_api_key, xai_api_key):

    provider = model_config["provider"]
    model = model_config["model"]

    if provider == "gemini":
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=gemini_api_key,
        )

    elif provider == "xai":
        if not xai_api_key:
            raise ValueError("XAI_API_KEY is not set.")

        return ChatXAI(
            model=model,
            temperature=0,
            xai_api_key=xai_api_key,
        )

    elif provider == "ollama":
        return ChatOllama(
            model=model,
            temperature=0,
        )

    raise ValueError(f"Unsupported provider: {provider}")