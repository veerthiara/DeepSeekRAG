"""
Enhanced Gradio Frontend for DeepSeek RAG Chatbot
Now with conversational AI, session management, and smart query routing!
"""

import gradio as gr
import requests
import json
from typing import List, Tuple, Optional

class ConversationalChatbotClient:
    """
    Enhanced client for interacting with the conversational AI backend.
    Supports session management, follow-up questions, and rich responses.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None  # Track current session
        
    def ask_question(self, question: str) -> dict:
        """
        Ask a question using the new conversational AI endpoint.
        Automatically maintains session continuity.
        """
        try:
            # Use the new conversational endpoint
            response = requests.post(
                f"{self.base_url}/chat/ask",
                json={
                    "question": question,
                    "session_id": self.session_id,  # Include session for continuity
                    "user_preferences": {
                        "response_detail": "moderate",
                        "include_sources": True
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Store session ID for continuity
                if not self.session_id:
                    self.session_id = result.get("session_id")
                
                return {
                    "success": True,
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def get_session_stats(self) -> dict:
        """Get statistics for the current session."""
        if not self.session_id:
            return {"error": "No active session"}
        
        try:
            response = requests.get(f"{self.base_url}/chat/session/{self.session_id}/stats")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_new_session(self):
        """Start a new conversation session."""
        self.session_id = None

# Initialize the enhanced client
client = ConversationalChatbotClient()

def format_response(response_data: dict) -> Tuple[str, str]:
    """
    Format the enhanced response data into user-friendly text.
    Returns (answer, metadata) tuple.
    """
    answer = response_data.get("answer", "No answer provided")
    
    # Build metadata information
    metadata_parts = []
    
    # Query type and confidence
    query_type = response_data.get("query_type_used", "Unknown")
    confidence = response_data.get("confidence", 0)
    metadata_parts.append(f"**Query Type**: {query_type} (Confidence: {confidence:.1%})")
    
    # Reasoning
    reasoning = response_data.get("reasoning", "")
    if reasoning:
        metadata_parts.append(f"**Reasoning**: {reasoning}")
    
    # Sources
    sources = response_data.get("sources", [])
    if sources:
        metadata_parts.append(f"**Sources**: {', '.join(sources)}")
    
    # SQL Query (if applicable)
    sql_query = response_data.get("sql_query")
    if sql_query and sql_query != "Query not available":
        metadata_parts.append(f"**SQL Query**: `{sql_query}`")
    
    # Session info
    session_id = response_data.get("session_id", "")
    if session_id:
        metadata_parts.append(f"**Session**: {session_id[:8]}...")
    
    # Follow-up suggestions
    followups = response_data.get("suggested_followups", [])
    if followups:
        metadata_parts.append(f"**Suggested Questions**:\n" + 
                            "\n".join([f"• {suggestion}" for suggestion in followups]))
    
    # Clarification needed
    clarification = response_data.get("clarification_needed")
    if clarification:
        metadata_parts.append(f"**Clarification Needed**: {clarification}")
    
    metadata = "\n\n".join(metadata_parts)
    return answer, metadata

def chat_with_ai(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """
    Enhanced chat function that maintains conversation history and provides rich responses.
    """
    if not message.strip():
        return history, ""
    
    # Show loading state
    thinking_message = "🤔 Analyzing your question and determining the best approach..."
    history.append((message, thinking_message))
    
    # Ask the question using enhanced client
    result = client.ask_question(message)
    
    if result["success"]:
        response_data = result["data"]
        answer, metadata = format_response(response_data)
        
        # Update the last response with actual answer
        history[-1] = (message, answer)
        
        # Return updated history and metadata
        return history, metadata
    else:
        error_message = f"❌ Error: {result['error']}"
        history[-1] = (message, error_message)
        return history, "Error occurred while processing your question."

def get_session_info() -> str:
    """Get information about the current session."""
    if not client.session_id:
        return "No active session. Start chatting to create a session!"
    
    stats_result = client.get_session_stats()
    if stats_result.get("success"):
        stats = stats_result["data"]
        return f"""
**Session Information**:
- Session ID: {stats['session_id'][:8]}...
- Created: {stats['created_at']}
- Interactions: {stats['total_interactions']}
- Current Context: {stats['current_context']}
        """
    else:
        return f"Error getting session info: {stats_result.get('error', 'Unknown error')}"

def start_new_conversation():
    """Start a new conversation session."""
    client.start_new_session()
    return [], "", "New session started! Ask me anything about the database."

def create_gradio_interface():
    """Create the enhanced Gradio interface with conversational features."""
    
    # Custom CSS for better styling
    css = """
    .metadata-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
        font-size: 0.9em;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
    }
    """
    
    with gr.Blocks(css=css, title="DeepSeek RAG Chatbot - Conversational AI") as interface:
        
        # Header
        gr.Markdown("""
        # 🤖 DeepSeek RAG Chatbot - Conversational AI
        
        Welcome to the enhanced conversational AI! This system:
        - **Maintains conversation context** across multiple questions
        - **Intelligently routes** your questions (RAG/SQL/Hybrid)
        - **Suggests follow-up questions** based on your interests
        - **Provides detailed explanations** of its reasoning
        
        Try asking about products, customers, orders, or any business data!
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                # Main chat interface
                chatbot = gr.Chatbot(
                    label="Conversation",
                    elem_classes=["chat-container"],
                    height=500,
                    show_label=True
                )
                
                with gr.Row():
                    message_input = gr.Textbox(
                        placeholder="Ask me anything about the database... (e.g., 'How many products do we have?' or 'Tell me about our customers')",
                        label="Your Question",
                        scale=4
                    )
                    send_button = gr.Button("Send", variant="primary", scale=1)
                
                # Response metadata display
                metadata_output = gr.Markdown(
                    label="Response Details",
                    elem_classes=["metadata-box"]
                )
                
            with gr.Column(scale=1):
                # Session management panel
                gr.Markdown("### 🔧 Session Management")
                
                session_info = gr.Markdown(
                    "No active session. Start chatting to create a session!"
                )
                
                with gr.Row():
                    refresh_session_btn = gr.Button("Refresh Info", size="sm")
                    new_session_btn = gr.Button("New Session", size="sm", variant="secondary")
                
                # Quick example questions
                gr.Markdown("### 💡 Try These Questions")
                
                example_questions = [
                    "How many products do we have?",
                    "Tell me about our customers",
                    "What are the top-selling categories?",
                    "Show me recent orders",
                    "Explain the database structure"
                ]
                
                for question in example_questions:
                    example_btn = gr.Button(question, size="sm", variant="outline")
                    example_btn.click(
                        lambda q=question: (q, ""),  # Return question and clear metadata
                        outputs=[message_input, metadata_output]
                    )
        
        # Event handlers
        def handle_message(message, history):
            """Handle user message and update interface."""
            new_history, metadata = chat_with_ai(message, history)
            return new_history, "", metadata  # Clear input, return new history and metadata
        
        # Send button click
        send_button.click(
            handle_message,
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, metadata_output]
        )
        
        # Enter key press
        message_input.submit(
            handle_message,
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, metadata_output]
        )
        
        # Session management
        refresh_session_btn.click(
            get_session_info,
            outputs=session_info
        )
        
        new_session_btn.click(
            start_new_conversation,
            outputs=[chatbot, message_input, session_info]
        )
        
        # Footer
        gr.Markdown("""
        ---
        **Features**: Session Management | Smart Query Routing | Context Awareness | Follow-up Suggestions
        
        **Tip**: The AI remembers your conversation context, so you can ask follow-up questions naturally!
        """)
    
    return interface

if __name__ == "__main__":
    # Create and launch the enhanced interface
    interface = create_gradio_interface()
    
    print("🚀 Starting Enhanced Conversational AI Frontend...")
    print("💬 Features: Session Management, Smart Routing, Context Awareness")
    print("🌐 Access the app at: http://127.0.0.1:7860")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )