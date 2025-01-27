import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Define the API endpoints
PLC_CHAT_API_URL = os.environ.get("PLC_CHAT_API_URL")
PLC_DOCUMENTATION_API_URL = os.environ.get("PLC_DOCUMENTATION_API_URL")


class HelperFunction:

    def __init__(self):
        pass

    def plc_chat_section(self):
        """PLC Chat Functionality."""
        st.subheader("Ask a PLC-related Question")

        # Display previous chat history
        self.display_chat_history(st.session_state.chat_history)

        # Input for user question
        question = st.text_input("Enter your question:", key="plc_question_input")

        if st.button("Submit"):
            if question:
                with st.spinner("Fetching response..."):
                    response = requests.post(
                        PLC_CHAT_API_URL, json={"question": question}
                    )
                if response.status_code == 200:
                    answer = response.json().get("response")
                    st.session_state.chat_history.append(("User: " + question, "Bot: " + answer))
                    st.rerun()
                else:
                    st.error("Failed to fetch the response.")
            else:
                st.warning("Please enter a question.")

    def plc_documentation_section(self):
        """PLC Documentation Assistance."""
        st.subheader("Browse PLC Documentation")
        topic = st.text_input("Enter a PLC topic to search:", key="plc_topic_input")

        if st.button("Search Documentation"):
            if topic:
                with st.spinner("Searching documentation..."):
                    response = requests.get(PLC_DOCUMENTATION_API_URL, params={"topic": topic})
                if response.status_code == 200:
                    documentation = response.json().get("documentation")
                    st.markdown(f"### Results for '{topic}':\n{documentation}")
                else:
                    st.error("Failed to fetch documentation.")
            else:
                st.warning("Please enter a topic.")

    def display_chat_history(self, chat_history):
        """Display chat history."""
        for user_msg, bot_msg in chat_history:
            st.markdown(f"""
            <div style='margin: 10px;'>
                <p style='background-color: #f0f0f0; padding: 10px; border-radius: 10px;'>
                    <strong>{user_msg}</strong>
                </p>
                <p style='background-color: #e0f7fa; padding: 10px; border-radius: 10px;'>
                    <strong>{bot_msg}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
