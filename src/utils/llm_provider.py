import os
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from custom_llm.my_chat_model import MyChatModel
from custom_llm.openrouter_chat_model import OpenRouterChatModel


def llm_provide(model_name: str, model_provider: str,
                is_json_format: bool = False, max_tokens: int = 12000) -> BaseChatModel:
    if model_provider == "openrouter":
        openai_api_key = os.getenv("OPENROUTER_API_KEY")
        llm = ChatOpenAI(api_key=openai_api_key,
                         base_url="https://openrouter.ai/api/v1",
                         max_tokens=max_tokens,
                         model=model_name, temperature=0.0)
    elif model_provider == "openrouter-custom":
        openai_api_key = os.getenv("OPENROUTER_API_KEY")
        llm = OpenRouterChatModel(api_key= openai_api_key, model=model_name, temperature=0,max_tokens=max_tokens)
    elif model_provider == "my_provider":   # ad uso privato con server interno
        llm = MyChatModel(
            model=model_name, temperature=0, max_tokens=max_tokens,
            format="json" if is_json_format else None
        )
    # todo: aggiungere altri LLM
    else:
        raise ValueError(f"Unknown model provider: {model_provider}")

    return llm
