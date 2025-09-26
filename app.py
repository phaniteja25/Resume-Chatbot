import streamlit as st
import os
import sys
import torch 
#adding src to the directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'data'))

from rag_system import ResumeRAG

torch.classes.__path__ = []

#setting the oconfig
st.set_page_config(
    page_title="Chat with Teja's Resume",
    page_icon='💼',
    layout='wide',
    initial_sidebar_state="expanded"
)

# Custom CSS for better chat appearance
st.markdown("""
<style>
    .chat-container {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        text-align: left;
    }
    
    .stChatInput > div {
        background-color: white;
    }
    
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    
    init_session_state()
    
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💼 Chat with Teja Upadhyayula's Resume</h1>
        <p style="color: #666; font-size: 1.1em;">Ask me anything about Teja Upadhyayula's professional background!</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    if not check_api_key__present():
        return
    
    
    #setting up side bar
    
    setup_sidebar()
    
    
    if st.session_state.rag_system:
        display_chat_interface()
    else:
        display_welcome_screen()
    


def init_session_state():
    
    #system states
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = False
        
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False

    #chat states
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    if 'chat_started' not in st.session_state:
        st.session_state.chat_started = False
        
    if 'show_typing' not in st.session_state:
        st.session_state.show_typing = False
        
    if 'last_question' not in st.session_state:
        st.session_state.last_question = ""
        


def check_api_key__present():
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("🔑 Gemini API key not found!")
        st.markdown("""
        **To get started:**
        1. Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Add it to your `.env` file: `GEMINI_API_KEY=your-key-here`
        3. Restart the app
        
        **For Streamlit Cloud deployment:**
        Add `GEMINI_API_KEY` to your app secrets.
        """)
        
        return False
    else:
        return True

def rag_system():
    
    status_text = st.empty()
    
    try:
        
        status_text.text("Initializing Resume Bot")
        rag = ResumeRAG()
        st.session_state.system_initialized = True
        st.session_state.rag_system = rag
        status_text.text("Successfully Initialized Resume Bot")
        return True
        
    except Exception as e:
        st.error(f"❌ Error initializing system: {str(e)}")
        return False

def setup_sidebar():
    
    
    with st.sidebar:
        st.header("AI Resume Chat Bot")
    
    #initization section 
    
        if not st.session_state.system_initialized or not st.session_state.rag_system:
            st.markdown("Ready to Start?")
            if st.button("🚀 Initialize Resume Chatbot", type="primary", use_container_width=True):
                result = rag_system()
            
                if result:
                    st.rerun()
                else:
                    st.error("Error occured while initliazing the app :(")
            
        
        st.divider()
    
    
        sample_questions = [
                "What's his background?",
                "What programming languages does he know?",
                "Tell me about his Paycom internship",
                "What projects has he worked on?",
                "What's his educational background?",
                "Does he have cloud experience?",
                "What technologies does he use?",
                "Tell me about his Android development experience"
            ]
    
    
        for i, question in enumerate(sample_questions):
            if st.button(question, key=f"sample_{i}", use_container_width=True):
                if not st.session_state.rag_system:
                    st.info("System is not Initialized yet. Please initlialize it first")
                else:                
                    # Add question to chat
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": question,
                        "timestamp": st.session_state.get('message_counter', 0)
                    })
                    st.session_state.chat_started = True
                
                    with st.chat_message(name="AI",avatar="💼"):
                        with st.spinner("Thinking..."):
                            try:
                                response = st.session_state.rag_system.chat(question)
                            except Exception as e:
                                response = f"Sorry!! I encountered an error : {e}"
            
                            st.markdown(response)
        
                            assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": st.session_state.get('message_counter', 0) + 1
                    }       
        
        
                        st.session_state.messages.append(assistant_message)           
                    if 'message_counter' not in st.session_state:
                        st.session_state.message_counter = 0
                    st.session_state.message_counter += 2         
                    st.divider()
    
        st.markdown('''
                This AI Chatbot is powered by
                    - 🧠 **Google Gemini 2.5 Flash Lite**
                    - 🔍 **ChromaDB Vector Search** 
                    - 🤖 **Sentence Transformers**
                    - ⚡ **Streamlit Interface**
                    
                    Ask any question about Teja's Resume
                ''')
    

def display_welcome_screen():
    """Display welcome screen when system isn't ready."""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>👋 Welcome!</h2>
            <p style="font-size: 1.2em; color: #666;">
                Get ready to chat with Saimanikanta's AI resume assistant
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("👈 Click 'Initialize Resume Chatbot' in the sidebar to get started!")
        
        # Show what users can ask about
        st.markdown("### 📋 What you can ask about:")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            **💼 Professional Experience:**
            - Work history and internships
            - Technologies and frameworks used
            - Key achievements and projects
            - Specific company experiences
            
            **🎓 Education & Skills:**
            - Academic background
            - Technical skills and programming languages
            - Certifications and relevant coursework
            """)
        
        with col_b:
            st.markdown("""
            **🚀 Projects & Development:**
            - Personal and academic projects
            - Mobile app development
            - Web development experience
            - Cloud and database technologies
            
            **🎯 Career & Goals:**
            - Career objectives and interests
            - Industry preferences
            - Professional strengths
            """)
            
            
            
def display_chat_interface():
    
    if not st.session_state.chat_started or not st.session_state.messages:
        display_welcome_message()
        
    #chat container
    chat_container = st.container()
    
    with chat_container:
        
        for i,message in enumerate(st.session_state.messages):
            display_message(message)
    
    handle_chat_input()
    
    

def display_welcome_message():
    """Display initial welcome message in chat."""
    
    with st.chat_message(name="assistant", avatar="💼"):
        st.markdown("""
        👋 **Hi! I'm Saimanikanta's AI resume assistant.**
        
        I can answer questions about:
        - 💻 My technical skills and programming experience
        - 🏢 My work experience and internships  
        - 🎓 My educational background
        - 🚀 My projects and achievements
        - 🎯 My career goals and interests
        
        **What would you like to know about my background?**
        """)

def display_message(message):
    """Display a single chat message."""
    
    role = message["role"]
    content = message["content"]
    
    # Choose avatar based on role
    avatar = "🧑‍💼" if role == "user" else "💼"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)
        
def handle_chat_input():
    
    if prompt := st.chat_input("Ask me anything about Teja's Resume"):
        
        st.session_state.chat_started = True
        
        user_message = {
            "role":"user",
            "content":prompt,
            "timestamp":st.session_state.get('message_counter',0)
        }
        
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(prompt)
            
        
        with st.chat_message(name="AI",avatar="💼"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.rag_system.chat(prompt)
                except Exception as e:
                    response = f"Sorry!! I encountered an error : {e}"
            
            st.markdown(response)
        
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": st.session_state.get('message_counter', 0) + 1
        }       
        
        
        st.session_state.messages.append(assistant_message)
        
        # Update message counter
        if 'message_counter' not in st.session_state:
            st.session_state.message_counter = 0
        st.session_state.message_counter += 2  # User + assistant
        

if __name__ == "__main__":
    main()


    
    
    
    
    
    
    


