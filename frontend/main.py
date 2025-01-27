import streamlit as st
from utils import HelperFunction


class PLCUI(HelperFunction):

    def __init__(self):
        # Set the page title and layout
        st.set_page_config(page_title="PLC Chat", layout="wide")
        super().__init__()

        # Initialize session state for chat history and PLC model selection
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'selected_tab' not in st.session_state:
            st.session_state.selected_tab = 'Chat'
        if 'processed' not in st.session_state:
            st.session_state.processed = False

    def clear_session(self):
        st.session_state.chat_history = []

    def driver(self):
        # Main tabs for Chat functionality
        chat_tab, doc_tab = st.tabs(["PLC Chat", "Documentation"])

        with chat_tab:
            self.plc_chat_section()
        with doc_tab:
            self.plc_documentation_section()

    def main(self):
        st.title("PLC Chat Assistant")
        self.driver()


PLCUI().main()
