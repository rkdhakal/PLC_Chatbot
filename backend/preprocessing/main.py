from fastapi import FastAPI
import pandas as pd
import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# Constants for the Groq API
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_API_URL = "https://api.groq.com/v1/chat/completions"

app = FastAPI()

class PLC_chatbot:
    def __init__(self):
        print("Initializing PLC Chatbot...")
        
        # Load the CSV file
        try:
            self.df = pd.read_csv("final_preprocessed.csv")
            print("CSV file loaded successfully. Shape:", self.df.shape)
        except Exception as e:
            print("Error loading CSV file:", e)
            return
        
        # Check if the content column exists
        if "content" not in self.df.columns:
            print("Error: 'content' column not found in CSV file.")
            return

        # Load sentence transformer model
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            print("SentenceTransformer model loaded.")
        except Exception as e:
            print("Error loading SentenceTransformer:", e)
            return

        # Convert text into embeddings
        try:
            self.embeddings = self.model.encode(self.df["content"].tolist(), convert_to_numpy=True)
            print("Embeddings generated. Shape:", self.embeddings.shape)
        except Exception as e:
            print("Error generating embeddings:", e)
            return

        # Create a FAISS index
        try:
            self.dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(self.embeddings)
            print("FAISS index created and data added.")

            # Save FAISS index
            faiss.write_index(self.index, "error_codes_faiss.index")
            print("FAISS index saved successfully.")
        except Exception as e:
            print("Error creating FAISS index:", e)
            return

    def retrieve_similar(self, query, top_k=1):
        try:
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            print("Query embedding generated successfully.")

            distances, indices = self.index.search(query_embedding, top_k)
            print(f"FAISS search completed. Distances: {distances}, Indices: {indices}")

            results = []
            for i in range(top_k):
                if distances[0][i] < 0.5:  # Adjust similarity threshold
                    results.append(self.df.iloc[indices[0][i]]["content"])
            
            print("Retrieved results:", results)
            return results
        except Exception as e:
            print("Error in retrieve_similar():", e)
            return []

    def generate_response(self, query):
        retrieved_info = self.retrieve_similar(query)

        # if not retrieved_info:
        #     print("No similar error codes found.")
        #     return "I'm sorry, but I couldn't find an exact match for this error code."

        context = "\n\n".join(retrieved_info)
        
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
        """

        print("Sending request to Groq API...")

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a Siemens PLC error code assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                print("Groq API Response:", result)
                return result
            else:
                print("Error from Groq API:", response.json())
                return f"Error: {response.json()}"
        except Exception as e:
            print("Error in generate_response():", e)
            return "Error: Unable to process request."

@app.get("/chat")
def chat(query: str):
    print("Received query:", query)
    response = PLC_chatbot().generate_response(query)
    print("Final chatbot response:", response)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
