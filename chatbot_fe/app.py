"""
app.py
Gradio frontend for DeepSeek RAG Chatbot - Simplified version
"""

import gradio as gr
import requests
import json

# Backend API configuration
BACKEND_BASE_URL = "http://localhost:8000"

class ChatbotClient:
    """Client to interact with the FastAPI backend"""
    
    def __init__(self, base_url: str = BACKEND_BASE_URL):
        self.base_url = base_url
    
    def ask_rag(self, question: str) -> dict:
        """Ask question using RAG endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/rag/ask",
                json={"question": question},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def ask_sql(self, question: str) -> dict:
        """Ask question using SQL agent endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/sql/ask",
                json={"question": question},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.base_url}/rag/health", timeout=5)
            return response.status_code == 200
        except:
            return False

# Initialize client
client = ChatbotClient()

def ask_question(question, mode):
    """Process user question and return response"""
    if not question.strip():
        return "Please enter a question."
    
    # Check backend health
    if not client.health_check():
        return "❌ Backend server is not running. Please start your FastAPI server first."
    
    # Get response based on mode
    if mode == "RAG (Context-based)":
        response = client.ask_rag(question)
        if "error" in response:
            return f"❌ Error: {response['error']}"
        
        answer = response.get("answer", "No answer received")
        context = response.get("context", [])
        context_count = response.get("context_count", 0)
        
        result = f"🤖 **Answer:** {answer}\n\n"
        if context:
            result += f"📚 **Context used ({context_count} documents):**\n"
            for i, ctx in enumerate(context[:3], 1):  # Show top 3
                result += f"{i}. {ctx}\n"
        return result
    
    elif mode == "SQL (Database queries)":
        response = client.ask_sql(question)
        if "error" in response:
            return f"❌ Error: {response['error']}"
        
        answer = response.get("answer", "No answer received")
        return f"🔍 **SQL Result:** {answer}"
    
    return "Invalid mode selected"

# Create simpler Gradio interface
with gr.Blocks(title="DeepSeek RAG Chatbot") as demo:
    gr.Markdown(
        """
        # 🤖 DeepSeek RAG Chatbot
        
        Choose between **RAG mode** (context-based answers) or **SQL mode** (direct database queries).
        
        **RAG Mode:** Uses vector search + LLM for context-aware answers  
        **SQL Mode:** Generates and executes SQL queries on your database
        """
    )
    
    with gr.Row():
        mode = gr.Dropdown(
            choices=["RAG (Context-based)", "SQL (Database queries)"],
            value="RAG (Context-based)",
            label="Mode"
        )
    
    with gr.Row():
        question_input = gr.Textbox(
            placeholder="Ask me about products, customers, orders...",
            label="Your Question",
            lines=2
        )
    
    with gr.Row():
        submit_btn = gr.Button("Ask Question", variant="primary")
    
    answer_output = gr.Textbox(
        label="Answer",
        lines=10,
        max_lines=20
    )
    
    gr.Markdown(
        """
        ### 💡 Example Questions
        
        **RAG Mode:**
        - "What products do you have?"
        - "Tell me about beverages"
        - "Which items are good for breakfast?"
        
        **SQL Mode:**
        - "How many products are there?"
        - "List all suppliers"
        - "How many orders have been placed?"
        """
    )
    
    # Event handlers
    submit_btn.click(
        ask_question,
        inputs=[question_input, mode],
        outputs=answer_output
    )
    
    question_input.submit(
        ask_question,
        inputs=[question_input, mode],
        outputs=answer_output
    )

if __name__ == "__main__":
    print("Starting Gradio interface...")
    print("Make sure your FastAPI backend is running on http://localhost:8000")
    demo.launch(
        server_name="127.0.0.1",  # Use localhost instead of 0.0.0.0
        server_port=7860,
        share=False,
        show_error=True
    )