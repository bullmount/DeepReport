from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    HumanMessage,
    BaseMessage,
)
from langchain_core.outputs import ChatResult

from custom_llm import MyChatModel

from dotenv import load_dotenv
load_dotenv()

def test_chat_wk_model():
    # Configura l'istanza del modello
    chat_model = MyChatModel(model="gpt-4o", format="json"
                             # base_url="http://localhost:1234/v1",  # Assicurati che LMStudio sia in esecuzione su questa URL
                             # model="model",  # Nome del modello da utilizzare
                             # temperature=0.7,
                             # format="json",  # Richiedi il formato JSON per il risultato
                             )

    # Crea un messaggio di input (simulando una conversazione)
    messages = [HumanMessage(content="Qual è la capitale della Francia? (rispondi in formato json)")]

    # Genera una risposta usando il modello
    result: ChatResult = chat_model._generate(messages)

    assert "parigi" in result.generations[0].text.lower()


