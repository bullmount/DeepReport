import os
from typing import Any, Dict, Iterator, List, Optional
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult, LLMResult
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompt_values import PromptValue
from pydantic import Field
import json
import requests
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class OpenRouterChatModel(BaseChatModel):
    api_key: str
    model_name: str = Field(alias='model')
    max_tokens: Optional[int] = 4 * 1024
    temperature: Optional[float] = 0.0
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stop: Optional[List[str]] = None

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "openrouter-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters.

        This information is used by the LangChain callback system, which
        is used for tracing purposes make it possible to monitor LLMs.
        """
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "api_key": self.api_key,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": self.stop,
        }

    async def agenerate(self, messages_list: List[List[BaseMessage]], stop: Optional[List[str]] = None,
                        **kwargs) -> LLMResult:
        """
        Metodo asincrono per generare risposte multiple.
        """
        results = []
        for messages in messages_list:
            chat_result = self._generate(messages, stop, **kwargs)
            results.append(chat_result.generations)

        return LLMResult(generations=results)

    async def agenerate_prompt(self, prompts: List[PromptValue], stop: Optional[List[str]] = None,
                               **kwargs) -> LLMResult:
        """
        Metodo legacy per compatibilità con versioni più vecchie di LangChain.
        """
        messages_list = [prompt.to_messages() for prompt in prompts]
        return await self.agenerate(messages_list, stop, **kwargs)

    def __convert_to_openai_messages(self, messages: list[BaseMessage]) -> list[dict]:
        """
        Converte una lista di messaggi LangChain in formato compatibile con OpenAI.
        """
        openai_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, SystemMessage):
                role = "system"
            else:
                raise ValueError(f"Messaggio non supportato: {type(message)}")

            openai_messages.append({"role": role, "content": message.content})
        return openai_messages

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        openai_messages = self.__convert_to_openai_messages(messages)
        completion = client.chat.completions.create(
            # extra_headers={
            #     "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
            #     "X-Title": "DeepReport",  # Optional. Site title for rankings on openrouter.ai.
            # },
            model=self.model_name,
            messages=openai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop)
        try:
            text = completion.choices[0].message.content
        except:
            logger.error(f"Errore in OpenRouterChatModel._generate: {completion}")
            raise
        llm_output = {
            "token_usage": completion.usage.to_dict(),
            "model_name": self.model_name,
        }
        generation = ChatGeneration(message=AIMessage(content=text))
        return ChatResult(generations=[generation], llm_output=llm_output)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        openai_messages = self.__convert_to_openai_messages(messages)
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": openai_messages,
            "stream": True,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": stop,
        }
        response = requests.post(url, headers=headers, json=payload, stream=True)
        if response.status_code != 200:
            raise Exception(f"Errore nella richiesta: {response.status_code}")

        buffer = ""
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            buffer += chunk
            while True:
                try:
                    # Find the next complete SSE line
                    line_end = buffer.find('\n')
                    if line_end == -1:
                        break
                    line = buffer[:line_end].strip()
                    buffer = buffer[line_end + 1:]
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            data_obj = json.loads(data)
                            content = data_obj["choices"][0]["delta"].get("content")
                            if content:
                                # Create AIMessageChunk with the content
                                message_chunk = AIMessageChunk(content=content)

                                # Create ChatGenerationChunk with the message chunk
                                generation_chunk = ChatGenerationChunk(message=message_chunk)

                                # Yield the generation chunk
                                if run_manager:
                                    run_manager.on_llm_new_token(content)
                                yield generation_chunk

                        except json.JSONDecodeError:
                            pass
                except Exception as e:
                    break

        return  # Terminazione del ciclo, risposte complete



def test_chat_model():
    """Test della classe ChatLMStudio."""
    from dotenv import load_dotenv
    load_dotenv()
    try:
        # Configura l'istanza del modello
        chat_model = OpenRouterChatModel(model="mistralai/mistral-small-24b-instruct-2501:free",
                                         api_key=os.getenv("OPENROUTER_API_KEY")
            # base_url="http://localhost:1234/v1",  # Assicurati che LMStudio sia in esecuzione su questa URL
            # model="model",  # Nome del modello da utilizzare
            # temperature=0.7,
            # format="json",  # Richiedi il formato JSON per il risultato
        )

        # Crea un messaggio di input (simulando una conversazione)
        messages = [HumanMessage(content="Qual è la capitale della Francia? (rispondi in formato json)")]
        result = chat_model.invoke(messages)
        print("Risultato generato:")
        print(result)

        for chunk in chat_model.stream("Spiegami come funziona un motore di ricerca."):
            print(chunk.content, end='', flush=True)



    except Exception as e:
        print(f"Errore durante il test: {str(e)}")


if __name__ == "__main__":
    test_chat_model()
