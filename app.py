import streamlit as st
import os
from rag_service import RAGService

st.set_page_config(page_title="Shell FAQ Assistant", page_icon="🛢️", layout="wide")

st.title("🛢️ Shell FAQ Assistant")
st.markdown("Ask me anything about Shell services!")

# Initialize session state
if 'rag_service' not in st.session_state:
    st.session_state.rag_service = None

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key", 
        type="password", 
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key to use the assistant"
    )
    
    # Initialize service
    if st.button("🚀 Initialize Service", type="primary"):
        if api_key:
            try:
                with st.spinner("Loading FAQ database and initializing service..."):
                    st.session_state.rag_service = RAGService(api_key)
                st.success("✅ Service initialized successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Failed to initialize service: {e}")
        else:
            st.error("Please enter your OpenAI API key")
    
    st.divider()
    
    # Service status
    st.subheader("📊 Status")
    if st.session_state.rag_service:
        st.success("🟢 Service: Ready")
        try:
            # Show some stats if possible
            if hasattr(st.session_state.rag_service.faq_processor, 'faqs'):
                faq_count = len(st.session_state.rag_service.faq_processor.faqs)
                st.info(f"📚 {faq_count} FAQs loaded")
        except:
            pass
    else:
        st.warning("🟡 Service: Not initialized")
    
    st.divider()
    
    # Clear conversation
    if st.button("🗑️ Clear Conversation"):
        if "messages" in st.session_state:
            st.session_state.messages = []
        st.rerun()
    
    # Example questions
    st.subheader("💡 Try These Questions")
    example_questions = [
        "How can I download the Shell app?",
        "What is Pay at Pump?",
        "Where can I find Shell charging stations?",
        "How do I contact Shell support?",
        "What payment methods are accepted?"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{hash(question)}", use_container_width=True):
            if st.session_state.rag_service:
                # Add to chat
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()

# Main chat interface
if not st.session_state.rag_service:
    st.warning("⚠️ Please initialize the service using the sidebar to start asking questions.")
    
    st.info("💡 You'll need an OpenAI API key to use this assistant. Get one from https://platform.openai.com/")
    
    # Show system overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🗂️ FAQ Database**
        
        Comprehensive collection of Shell service information extracted from HTML files.
        """)
    
    with col2:
        st.markdown("""
        **🔍 Vector Search**
        
        FAISS-powered semantic search for finding relevant FAQs quickly.
        """)
    
    with col3:
        st.markdown("""
        **🤖 AI Assistant**
        
        GPT-powered responses using retrieved FAQ context for accurate answers.
        """)

else:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander(f"📚 Sources ({len(message['sources'])})"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}. {source['question']}** (Relevance: {source['score']:.3f})")
                        
                        # Show first part of the answer
                        answer_preview = source['answer'][:300] + "..." if len(source['answer']) > 300 else source['answer']
                        st.write(answer_preview)
                        
                        if i < len(message['sources']):
                            st.divider()
    
    # Chat input
    if prompt := st.chat_input("What would you like to know about Shell?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.rag_service.answer_question(prompt)
                    
                    # Display the answer
                    st.markdown(result['answer'])
                    
                    # Show sources in expandable section
                    if result['sources']:
                        with st.expander(f"📚 Sources ({len(result['sources'])})"):
                            for i, source in enumerate(result['sources'], 1):
                                st.write(f"**{i}. {source['question']}** (Relevance: {source['score']:.3f})")
                                
                                # Show first part of the answer
                                answer_preview = source['answer'][:300] + "..." if len(source['answer']) > 300 else source['answer']
                                st.write(answer_preview)
                                
                                if i < len(result['sources']):
                                    st.divider()
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result['answer'],
                        "sources": result['sources']
                    })
                    
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg,
                        "sources": []
                    })

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Shell FAQ Assistant | Powered by FAISS, LangChain & OpenAI<br>
        For official support, visit <a href="https://support.shell.com" target="_blank">support.shell.com</a>
    </div>
    """, unsafe_allow_html=True)
