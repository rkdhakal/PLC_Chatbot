from fastapi import FastAPI
import uvicorn
import faiss
import numpy as np
import pandas as pd
from groq import Groq
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Set up the Groq API key properly
GROQ_API_KEY = "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"

class PLC_chatbot:
    def __init__(self):
        # Load a lightweight embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.df = pd.read_csv("final_preprocessed.csv")

        # Convert text content into embeddings and normalize
        self.embeddings = self.model.encode(self.df["content"].tolist(), convert_to_numpy=True)
        self.embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)  # Normalize

        # Create a FAISS index with Inner Product (cosine similarity)
        self.dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)  # Use Inner Product for cosine similarity
        self.index.add(self.embeddings)

        # Save FAISS index
        faiss.write_index(self.index, "error_codes_faiss.index")

        # Initialize Groq client
        self.llm = Groq(api_key=GROQ_API_KEY)

        # Define models
        self.LLAMA3_70B_INSTRUCT = "llama3-70b-8192"
        self.LLAMA3_8B_INSTRUCT = "llama3-8b-8192"
        self.DEFAULT_MODEL = self.LLAMA3_8B_INSTRUCT  # Choose appropriate model

    def retrieve_similar(self, query, top_k=5, threshold=0.2):
        # Encode and normalize the query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)  # Normalize

        # Perform similarity search
        distances, indices = self.index.search(query_embedding, top_k)
        print("distances",distances)
        results = []
        for i in range(top_k):
            if distances[0][i] > threshold:  # Since we use cosine similarity, higher is better
                print("content", self.df.iloc[indices[0][i]]["content"])
                results.append(self.df.iloc[indices[0][i]]["content"])

        return results

    def generate_response(self, query):
        retrieved_info = self.retrieve_similar(query)
        context = "\n\n".join(retrieved_info) if retrieved_info else "No relevant error codes found."
        print("context", context)
        
        prompt = f"""
        You are a Siemens PLC troubleshooting assistant.  
        Your task is to provide **only the retrieved Siemens error code data** without adding any extra information.  

        ### **Retrieved Error Code Details:**
        {context}

        ### **User Query:**
        {query}

        ### **Format Response Exactly Like This:**
        - **Error Code:** (Extract from retrieved data)
        - **Description:** (Extract from retrieved data)
        - **Remedy:** (Extract from retrieved data)

        If no exact match is found, respond with:
        "I'm sorry, but I couldn't find an exact match for this error code. Please check the details and try again."

        **Do not** generate any information beyond what is in the retrieved data.
        """
        
        try:
            response = self.llm.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.DEFAULT_MODEL,
                temperature=0.6,
                top_p=0.9,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

@app.get("/chat")
def chat(query: str):
    response = PLC_chatbot().generate_response(query)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
