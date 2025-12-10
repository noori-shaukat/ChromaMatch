# src/rag/rag_pipeline.py

from src.models.chroma_model import analyze_image
from src.rag.retriever import RAGRetriever
from groq import Groq
import os
from dotenv import load_dotenv
from src.rag.guardrails import ChromaGuardrails

load_dotenv()

def get_client():
    from groq import Groq
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

client = get_client()

class ChromaRAGPipeline:
    def __init__(self):
        self.retriever = RAGRetriever()
        self.guardrails = ChromaGuardrails()

    def ml_to_query(self, ml_output: dict):
        return (
            f"My skin tone is {ml_output['skin_tone']}, "
            f"tone group {ml_output.get('tone_group')}, "
            f"descriptor {ml_output.get('descriptor')}, "
            f"undertone {ml_output['undertone']}, "
            f"my eye color is {ml_output['eye_color']} and "
            f"my hair color is {ml_output['hair_color']}. "
            f"What colors in fashion, makeup, and clothing suit this profile?"
        )

    def generate_answer(self, context_docs, user_query):
        context_str = "\n\n---DOCUMENT---\n\n".join(doc["text"] for doc in context_docs)

        prompt = f"""
You are a professional color analyst and stylist.

USER PROFILE:
{user_query}

RELEVANT DOCUMENTS:
{context_str}

Using only the information from these documents, give highly personalized and accurate style + color advice.
Focus on:
- clothing colors
- makeup colors
- jewelry (gold/silver)
- hair styling suggestions
- seasonal color palette match
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.3,
        )

        return response.choices[0].message.content

    # ----------- NEW FUNCTION -----------
    def recommend_from_predictions(self, query: str):
        docs = self.retriever.search(query, k=5)
        answer = self.generate_answer(docs, query)

        output_violations = self.guardrails.moderate_output(answer)
        if output_violations:
            print("Guardrail violation:", output_violations)
            answer = "I'm sorry, but I cannot provide a recommendation based on the provided information."

        return {
            "query_used": query,
            "rag_answer": answer,
            "retrieved_docs": docs,
            "guardrail_violations": output_violations,
        }

    def run(self, image_path: str):
        # Step 1: Model prediction
        ml_pred = analyze_image(image_path)

        # Step 2: Convert into query
        query = self.ml_to_query(ml_pred)

        # Step 3: Retrieve documents
        docs = self.retriever.search(query, k=4)

        # Step 4: Generate final answer
        answer = self.generate_answer(docs, query)

        return {
            "ml_prediction": ml_pred,
            "rag_answer": answer,
            "retrieved_docs": docs,
        }
