import streamlit as st
import requests

# FastAPI backend URL
FASTAPI_URL = "http://127.0.0.1:8000/chat"

# Streamlit UI Configuration
st.set_page_config(page_title="Siemens PLC Error Code Chatbot", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
        /* Background & general text styles */
        body {background-color: #f8f9fa;}
        .stTextArea textarea {font-size: 18px; height: 120px !important;}
        .stButton>button {
            border-radius: 8px; 
            padding: 10px 20px; 
            font-size: 18px; 
            font-weight: bold; 
            background-color: #007bff; 
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        /* Response Box */
        .response-box {
            border-radius: 10px;
            background-color: #eef2f7;
            padding: 15px;
            margin-top: 10px;
            color: #212529;
            font-weight: 500;
            font-size: 16px;
        }
        /* Code Styling */
        code {
            color: #d63384 !important; /* Dark pink color for error codes */
            background-color: #f8f9fa !important;
            padding: 2px 6px;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("⚙️ Siemens PLC Error Code Chatbot")
st.write("Get **troubleshooting help** for Siemens PLC error codes.")

# User Input
query = st.text_area("🔍 **Enter your error code or issue:**", "")

# Button to fetch response
if st.button("Get Solution 🚀"):
    if query.strip():
        with st.spinner("⏳ Retrieving response..."):
            try:
                response = requests.get(FASTAPI_URL, params={"query": query})
                if response.status_code == 200:
                    answer = response.json().get("response", "No response received.")
                    
                    # Display response inside a styled box
                    st.markdown(f'<div class="response-box">{answer}</div>', unsafe_allow_html=True)
                
                else:
                    st.error(f"❌ Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ API request failed: {e}")
    else:
        st.warning("⚠️ Please enter an error code or query.")

# Sidebar with Branding
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Siemens-logo.svg", width=200)
st.sidebar.subheader("About")
st.sidebar.write(
    """
    This chatbot uses **FAISS** for similarity search and **LLama3-8B** via Groq API 
    to provide troubleshooting solutions for Siemens PLC error codes.
    """
)
st.sidebar.info("💡 Developed using **FastAPI & Streamlit**.")

# Footer
st.markdown("---")
st.markdown("🚀 **Powered by FastAPI, FAISS & Streamlit** | Made with ❤️ for Siemens PLC users.")
