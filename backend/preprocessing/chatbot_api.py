"""
PLC Chatbot API — FastAPI backend
RAG pipeline: FAISS semantic search + Google Gemini
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
import csv
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LOG_PATH       = "query_log.csv"
DATASET_PATH   = "final_preprocessed_v2.csv"
SIMILARITY_THRESHOLD = 0.35
TOP_K = 5

app = FastAPI(title="PLC Chatbot API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Query audit logger ────────────────────────────────────────────────────────
def log_query(query: str, response: str, confidence: float, matched: bool, match_type: str):
    file_exists = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "query", "response", "confidence", "matched", "match_type"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "query":      query,
            "response":   response[:300],
            "confidence": confidence,
            "matched":    matched,
            "match_type": match_type,
        })


# ── RAG Chatbot ───────────────────────────────────────────────────────────────
class PLCChatbot:
    def __init__(self):
        print("[INIT] Loading dataset...")
        self.df = pd.read_csv(DATASET_PATH)

        print("[INIT] Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("[INIT] Building FAISS index...")
        embeddings = self.model.encode(
            self.df["content"].tolist(), convert_to_numpy=True, show_progress_bar=False
        )
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings.astype("float32"))

        print("[INIT] Configuring Gemini...")
        genai.configure(api_key=GEMINI_API_KEY)
        self.llm = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite",
            generation_config=genai.GenerationConfig(
                temperature=0.0,
                max_output_tokens=512,
            )
        )
        print(f"[INIT] Ready — {len(self.df)} records indexed.")

    def retrieve(self, query: str):
        # Step 1: exact match on error code
        normalised = query.strip().upper()
        exact = self.df[self.df["error_code"].str.upper() == normalised]
        if not exact.empty:
            return [exact.iloc[0]["content"]], 1.0, "exact"

        # Step 2: partial code match (e.g. user types "8182" without "16#")
        partial = self.df[self.df["error_code"].str.upper().str.contains(normalised, regex=False)]
        if not partial.empty:
            return [partial.iloc[0]["content"]], 0.95, "partial"

        # Step 3: semantic search
        vec = self.model.encode([query], convert_to_numpy=True)
        vec = (vec / np.linalg.norm(vec)).astype("float32")
        scores, indices = self.index.search(vec, TOP_K)
        top_score = float(scores[0][0])

        results = [
            self.df.iloc[indices[0][i]]["content"]
            for i in range(TOP_K)
            if scores[0][i] > SIMILARITY_THRESHOLD
        ]
        return results, top_score, "semantic"

    def build_prompt(self, context: str, query: str) -> str:
        return f"""You are a Siemens PLC troubleshooting assistant.
Use ONLY the retrieved data below. Do NOT add, infer, or invent anything.

### Retrieved Data:
{context}

### User Query:
{query}

### Respond EXACTLY in this format (no extra text):
- **Error Code:** [extract from data]
- **Description:** [extract from data]
- **Remedy:** [extract from data]

If there is no clear match in the retrieved data, respond only with:
"No exact match found. Please verify the error code and try again."

Do NOT generate anything beyond what is in the retrieved data."""

    def answer(self, query: str) -> dict:
        results, confidence, match_type = self.retrieve(query)

        if not results:
            response_text = "No reliable match found. Please verify the error code and try again."
            log_query(query, response_text, round(confidence, 3), False, match_type)
            return {"response": response_text, "confidence": round(confidence, 3), "matched": False, "match_type": match_type}

        context = "\n\n".join(results)
        prompt  = self.build_prompt(context, query)

        try:
            resp = self.llm.generate_content(prompt)
            text = resp.text.strip()
            log_query(query, text, round(confidence, 3), True, match_type)
            return {"response": text, "confidence": round(confidence, 3), "matched": True, "match_type": match_type}
        except Exception as e:
            msg = f"LLM error: {str(e)}"
            log_query(query, msg, 0.0, False, match_type)
            return {"response": msg, "confidence": 0.0, "matched": False, "match_type": match_type}


# ── Startup ───────────────────────────────────────────────────────────────────
chatbot = PLCChatbot()


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/chat")
def chat(query: str = Query(..., description="PLC error code or fault description")):
    return chatbot.answer(query)


@app.get("/health")
def health():
    return {
        "status":    "ok",
        "records":   len(chatbot.df),
        "model":     "gemini-3.1-flash-lite",
        "embedding": "all-MiniLM-L6-v2",
        "threshold": SIMILARITY_THRESHOLD,
    }


@app.get("/stats")
def stats():
    df = chatbot.df
    log_df = pd.read_csv(LOG_PATH) if os.path.exists(LOG_PATH) else pd.DataFrame()

    total_queries  = len(log_df)
    matched        = int(log_df["matched"].sum()) if not log_df.empty else 0
    avg_conf       = round(float(log_df["confidence"].mean()), 3) if not log_df.empty else 0.0

    return {
        "dataset": {
            "total_records":   len(df),
            "unique_codes":    int(df["error_code"].nunique()),
            "error_types":     df["error_type"].dropna().unique().tolist(),
            "source_files":    df["source_file"].dropna().unique().tolist(),
            "categories":      int(df["category"].nunique()),
        },
        "queries": {
            "total":           total_queries,
            "matched":         matched,
            "unmatched":       total_queries - matched,
            "avg_confidence":  avg_conf,
            "match_types":     log_df["match_type"].value_counts().to_dict() if not log_df.empty else {},
        }
    }


@app.get("/query-log")
def query_log(limit: int = 50):
    if not os.path.exists(LOG_PATH):
        return []
    df = pd.read_csv(LOG_PATH).tail(limit)
    return df.to_dict(orient="records")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
