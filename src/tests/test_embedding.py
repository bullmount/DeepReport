from sentence_transformers import SentenceTransformer, util
import numpy as np

import torch

if torch.cuda.is_available():
    print("CUDA è disponibile!")
    print("Nome GPU:", torch.cuda.get_device_name(0))
else:
    print("CUDA NON è disponibile.")

def calculate_embedding_similarity_score(query: str, texts: list[str], model_name: str = 'paraphrase-multilingual-mpnet-base-v2') -> list[float]:
    print("************************")
    print(model_name)
    try:
        model = SentenceTransformer(model_name, trust_remote_code=True)
    except ValueError:
        print(f"Errore: Il modello '{model_name}' non è stato trovato. Assicurati che il nome sia corretto.")
        return [0.0] * len(texts)

    query_embedding = model.encode(query,normalize_embeddings=True)
    text_embeddings = model.encode(texts,normalize_embeddings=True)

    similarity_scores = [util.pytorch_cos_sim(query_embedding, text_embedding).item()
                         for text_embedding in text_embeddings]

    return similarity_scores

if __name__ == '__main__':
    query = "Quali sono le ultime scoperte scientifiche sull'intelligenza artificiale?"
    texts = [
        "Un nuovo algoritmo di deep learning supera le prestazioni umane nel riconoscimento di immagini complesse.",
        "Ricercatori sviluppano un sistema di intelligenza artificiale in grado di generare testi creativi in modo autonomo.",
        "L'applicazione dell'IA nel settore medico porta a diagnosi più precise e trattamenti personalizzati.",
        "Le implicazioni etiche dell'intelligenza artificiale generativa sono oggetto di un acceso dibattito pubblico.",
        "Un gatto dorme pigramente sul divano mentre il sole splende attraverso la finestra."
    ]

    # Utilizzo del modello multilingua di default
    scores_default = calculate_embedding_similarity_score(query, texts)
    print("Scores con modello multilingua:")
    for i, score in enumerate(scores_default):
        print(f"Testo {i+1}: '{texts[i][:80]}...' - Score: {score:.4f}")

    print("\n")

    # Utilizzo di un modello specifico per l'italiano
    # italian_model_name = 'nickprock/sentence-bert-base-italian-uncased'
    italian_model_name ="Alibaba-NLP/gte-multilingual-base"
    scores_italian = calculate_embedding_similarity_score(query, texts, italian_model_name)
    for i, score in enumerate(scores_italian):
        print(f"Testo {i+1}: '{texts[i][:80]}...' - Score: {score:.4f}")

    # Utilizzo di un modello specifico per l'italiano
    italian_model_name = 'nickprock/sentence-bert-base-italian-uncased'
    scores_italian = calculate_embedding_similarity_score(query, texts, italian_model_name)
    for i, score in enumerate(scores_italian):
        print(f"Testo {i+1}: '{texts[i][:80]}...' - Score: {score:.4f}")