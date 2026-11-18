import logging
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai


MODEL = "gemini-4-hydrogen"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)


def create_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def main() -> None:
    st.set_page_config(page_title="Gemini Chatbot", page_icon="💬")
    st.title("💬 Gemini Chatbot")
    st.caption("Chat with Gemini. It remembers the context of this conversation.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "previous_interaction_id" not in st.session_state:
        st.session_state.previous_interaction_id = None

    with st.sidebar:
        st.header("Conversation")
        if st.button("New chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.previous_interaction_id = None
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            usage = message.get("usage")
            if usage:
                with st.expander("Token usage"):
                    st.write(f"Input tokens: {usage['input']}")
                    st.write(f"Output tokens: {usage['output']}")
                    st.write(f"Thought tokens: {usage['thought']}")
                    st.write(f"Tool tokens: {usage['tool']}")
                    st.write(f"Total tokens: {usage['total']}")

    user_message = st.chat_input("Type a message...")
    if not user_message or not user_message.strip():
        return

    with st.chat_message("user"):
        st.markdown(user_message)

    try:
        client = create_client()
        request = {"model": MODEL, "input": user_message.strip()}
        previous_interaction_id = st.session_state.previous_interaction_id
        if previous_interaction_id:
            request["previous_interaction_id"] = previous_interaction_id

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                interaction = client.interactions.create(**request)
            response = interaction.output_text or "No response generated."
            st.markdown(response)

            usage = interaction.usage
            usage_data = None
            if usage:
                usage_data = {
                    "input": usage.total_input_tokens or 0,
                    "output": usage.total_output_tokens or 0,
                    "thought": usage.total_thought_tokens or 0,
                    "tool": usage.total_tool_use_tokens or 0,
                    "total": usage.total_tokens or 0,
                }
                with st.expander("Token usage"):
                    st.write(f"Input tokens: {usage_data['input']}")
                    st.write(f"Output tokens: {usage_data['output']}")
                    st.write(f"Thought tokens: {usage_data['thought']}")
                    st.write(f"Tool tokens: {usage_data['tool']}")
                    st.write(f"Total tokens: {usage_data['total']}")

        st.session_state.messages.extend(
            [
                {"role": "user", "content": user_message.strip()},
                {"role": "assistant", "content": response, "usage": usage_data},
            ]
        )
        st.session_state.previous_interaction_id = interaction.id
    except Exception:
        logger.exception("Chat request failed.")
        st.error(
            "Could not get a response. Check your internet connection and make sure "
            "GOOGLE_API_KEY is set correctly in the project .env file."
        )


if __name__ == "__main__":
    main()
