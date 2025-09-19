# Shell FAQ Retrieval System

Efficient FAQ retrieval system using FAISS vector search and OpenAI's GPT models for natural language question answering.

## Features

- 🔍 **Vector Search**: FAISS-powered semantic search through Shell FAQ database
- 🤖 **AI Assistant**: GPT-powered natural language responses with source attribution  
- 💻 **CLI & Web Interface**: Command-line and Streamlit web interfaces
- 📚 **Source Attribution**: Shows which FAQs were used to generate each answer

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key_here

# Run automated setup (installs dependencies, builds index)
python setup.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY=your_openai_api_key_here

# Build FAQ index
python cli.py build
```

## Usage

**CLI:**
```bash
python cli.py ask "How can I download the Shell app?" --show-sources
python cli.py chat --show-sources
python cli.py search "shell app" --top-k 5
```

**Web Interface:**
```bash
streamlit run app.py
```

## Architecture

**Core Components:**
1. **FAQ Processor** (`faq_processor.py`): Extracts FAQ content, generates embeddings
2. **RAG Service** (`rag_service.py`): Orchestrates retrieval and generation pipeline  
3. **CLI Interface** (`cli.py`): Command-line interface with argparse
4. **Web Interface** (`app.py`): Streamlit web application

See `scripts/prd.txt` for detailed documentation.

## Requirements

- Python 3.8+, OpenAI API key, ~100MB RAM

## Project Structure

```
shell_faq_system/
├── extract_faq.py          # FAQ extraction from HTML files
├── faq_processor.py        # FAISS-based processing
├── rag_service.py         # RAG orchestration  
├── cli.py                 # Command-line interface
├── app.py                 # Streamlit web app
├── setup.py               # Automated setup
├── requirements.txt        # Dependencies
└── README.md   
```

## Testing

```bash
# Test after setup
python cli.py ask "How do I contact Shell support?"

# Verify installation  
python -c "from rag_service import RAGService; print('System ready!')"
```

## Troubleshooting

- **Module errors**: Run `pip install -r requirements.txt`
- **API key errors**: Set `export OPENAI_API_KEY=your_key_here`  
- **FAQ directory errors**: Run from project root with `shell-retail/faq/` present
- **Slow responses**: First query loads models; subsequent queries are faster
