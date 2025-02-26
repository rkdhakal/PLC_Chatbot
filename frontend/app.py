import streamlit as st
import requests

# FastAPI backend URL
FASTAPI_URL = "http://127.0.0.1:8000/chat"
# Streamlit UI
st.set_page_config(page_title="Siemens PLC Error Code Chatbot", layout="wide")

# Header
st.title("⚙️ Siemens PLC Error Code Chatbot")
st.write("Get troubleshooting help for Siemens PLC error codes.")

# User Input
query = st.text_area("🔍 Enter your error code or issue:", "")

if st.button("Get Solution 🚀"):
    if query.strip():
        with st.spinner("Retrieving response..."):
            try:
                response = requests.get(FASTAPI_URL, params={"query": query})
                if response.status_code == 200:
                    answer = response.json().get("response", "No response received.")
                    st.success("✅ Solution Found:")
                    st.write(answer)
                else:
                    st.error(f"❌ Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ API request failed: {e}")
    else:
        st.warning("⚠️ Please enter an error code or query.")

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Siemens-logo.svg", width=200)
st.sidebar.subheader("About")
st.sidebar.write(
    """
    This chatbot uses **FAISS** for similarity search and **LLama3-8B** via Groq API to provide troubleshooting solutions for Siemens PLC error codes.
    """
)
st.sidebar.info("💡 Developed using FastAPI & Streamlit.")

# Footer
st.markdown("---")
st.markdown("🚀 **Powered by FastAPI, FAISS & Streamlit** | Made with ❤️ for Siemens PLC users.")
