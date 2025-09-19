"""
Simple Streamlit Chat Interface for DeepSeek RAG Chatbot
Clean, reliable interface that avoids complex type issues.
"""

import streamlit as st
import requests
from typing import Optional
import time

class ChatClient:
    """Simple client for the conversational AI backend."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        
    def ask(self, message: str, session_id: Optional[str] = None) -> dict:
        """Send message and get AI response."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/chat",
                json={
                    "question": message,
                    "session_id": session_id,
                    "user_preferences": {"response_detail": "balanced"}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "answer": f"❌ Server error: {response.status_code}",
                    "query_type_used": "ERROR",
                    "session_id": session_id
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "answer": "❌ Cannot connect to backend. Make sure the server is running on http://127.0.0.1:8000",
                "query_type_used": "ERROR",
                "session_id": session_id
            }
        except requests.exceptions.Timeout:
            return {
                "answer": "⏳ Request timed out. The AI might be processing a complex query.",
                "query_type_used": "ERROR", 
                "session_id": session_id
            }
        except Exception as e:
            return {
                "answer": f"❌ Error: {str(e)}",
                "query_type_used": "ERROR",
                "session_id": session_id
            }

def main():
    """Main Streamlit app."""
    
    # Page config
    st.set_page_config(
        page_title="DeepSeek RAG Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize client
    client = ChatClient()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    
    # Header
    st.title("🤖 DeepSeek RAG Chatbot")
    st.markdown("**Your intelligent database assistant**")
    st.markdown("Ask me anything about your data in natural language! I automatically choose the best approach to help you.")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "query_type" in message and message["query_type"]:
                    st.caption(f"*[{message['query_type']} approach used]*")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your database..."):
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.ask(prompt, st.session_state.session_id)
                
                # Update session ID
                if response.get("session_id"):
                    st.session_state.session_id = response["session_id"]
                
                # Display response
                answer = response.get("answer", "No answer provided")
                query_type = response.get("query_type_used", "")
                
                st.markdown(answer)
                if query_type and query_type != "ERROR":
                    st.caption(f"*[{query_type} approach used]*")
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer,
            "query_type": query_type if query_type != "ERROR" else None
        })
    
    # Sidebar with controls
    with st.sidebar:
        st.markdown("### 💡 Example Questions")
        
        examples = [
            "How many products do we have?",
            "Tell me about our customers", 
            "What are our product categories?",
            "Show me recent orders",
            "What's the total revenue?"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                # Add example to chat input (this will trigger the chat)
                st.session_state.messages.append({"role": "user", "content": example})
                
                # Get AI response for example
                with st.spinner("Processing example..."):
                    response = client.ask(example, st.session_state.session_id)
                    
                    if response.get("session_id"):
                        st.session_state.session_id = response["session_id"]
                    
                    answer = response.get("answer", "No answer provided") 
                    query_type = response.get("query_type_used", "")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "query_type": query_type if query_type != "ERROR" else None
                    })
                
                # Rerun to show the new messages
                st.rerun()
        
        st.markdown("---")
        
        # Reset conversation
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()
        
        # Connection status
        st.markdown("### 🔗 Connection Status")
        try:
            test_response = requests.get("http://127.0.0.1:8000/api/v1/health", timeout=5)
            if test_response.status_code == 200:
                st.success("✅ Backend Connected")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Offline")

if __name__ == "__main__":
    main()