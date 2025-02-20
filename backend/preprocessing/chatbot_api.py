from fastapi import FastAPI
import uvicorn

app = FastAPI()

import requests
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd


GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class PLC_chatbot:
    def __init__(self):
        # Load a lightweight embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.df = pd.read_csv("final_preprocessed.csv")
        # Convert text content into embeddings
        self.embeddings = self.model.encode(self.df["content"].tolist(), convert_to_numpy=True)

        # Create a FAISS index
        self.dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(self.embeddings)

        # Save FAISS index
        faiss.write_index(self.index, "error_codes_faiss.index")


    def retrieve_similar(self, query, top_k=3):
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in range(top_k):
            if distances[0][i] < 0.5:  # Adjust similarity threshold
                results.append(self.df.iloc[indices[0][i]]["content"])
        
        return results

    def generate_response(self, query):
        retrieved_info = self.retrieve_similar(query)
        
        # if not retrieved_info:
        #     return "Sorry, I couldn't find relevant error codes. Please provide more details."

        context = "\n\n".join(retrieved_info)
        
        prompt = f"""You are a helpful Siemens PLC troubleshooting assistant. Based on the following Siemens error code details, provide guidance:\n\n{context}\n\nUser Query: {query}\n\nResponse:"""
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a Siemens PLC error code assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.json()}"

@app.get("/chat")
def chat(query: str):
    response = PLC_chatbot().generate_response(query)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
