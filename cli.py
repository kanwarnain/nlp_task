import argparse
import os
from rag_service import RAGService
from faq_processor import FAQProcessor

def build_command(args):
    """Build the FAQ index"""
    processor = FAQProcessor()
    processor.load_faqs(args.faq_dir)
    processor.build_index()
    processor.save_index(args.output)
    print("✅ FAQ index built and saved!")

def ask_command(args):
    """Ask a single question"""
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable or use --api-key")
        return
    
    try:
        rag = RAGService(api_key)
        result = rag.answer_question(args.question)
        
        print(f"\n🤖 Answer: {result['answer']}\n")
        
        if result['sources'] and args.show_sources:
            print("📚 Sources:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['question']} (Score: {source['score']:.3f})")
                if args.verbose:
                    print(f"   {source['answer'][:200]}...\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def chat_command(args):
    """Interactive chat"""
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable or use --api-key")
        return
    
    try:
        rag = RAGService(api_key)
        print("🛢️  Shell FAQ Assistant - Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("Your question: ")
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not question.strip():
                    continue
                
                result = rag.answer_question(question)
                print(f"\n🤖 {result['answer']}\n")
                
                if result['sources'] and args.show_sources:
                    print("📚 Sources used:")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"{i}. {source['question']} (Score: {source['score']:.3f})")
                    print()
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error initializing service: {e}")

def search_command(args):
    """Search FAQs directly"""
    try:
        processor = FAQProcessor()
        processor.load_index(args.index_file)
        results = processor.search(args.query, top_k=args.top_k)
        
        print(f"\n🔍 Search results for: {args.query}\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['question']} (Score: {result['score']:.3f})")
            if args.verbose:
                print(f"   {result['answer'][:150]}...")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Shell FAQ Assistant - Simple CLI with RAG capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py build                                    # Build FAQ index
  python cli.py ask "How do I download the Shell app?"  # Ask a question
  python cli.py chat --show-sources                     # Interactive chat with sources
  python cli.py search "shell app" --top-k 5           # Search FAQs directly
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build the FAQ index')
    build_parser.add_argument('--faq-dir', default='shell-retail/faq/', 
                             help='Directory containing FAQ HTML files (default: shell-retail/faq/)')
    build_parser.add_argument('--output', default='faq_index.pkl',
                             help='Output file for the index (default: faq_index.pkl)')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a single question')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--api-key', help='OpenAI API key (overrides OPENAI_API_KEY env var)')
    ask_parser.add_argument('--show-sources', action='store_true', 
                           help='Show sources used for the answer')
    ask_parser.add_argument('--verbose', action='store_true',
                           help='Show detailed source information')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Interactive chat')
    chat_parser.add_argument('--api-key', help='OpenAI API key (overrides OPENAI_API_KEY env var)')
    chat_parser.add_argument('--show-sources', action='store_true',
                            help='Show sources used for each answer')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search FAQs directly')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--top-k', type=int, default=5,
                              help='Number of results to return (default: 5)')
    search_parser.add_argument('--index-file', default='faq_index.pkl',
                              help='Index file to use (default: faq_index.pkl)')
    search_parser.add_argument('--verbose', action='store_true',
                              help='Show detailed results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'build':
        build_command(args)
    elif args.command == 'ask':
        ask_command(args)
    elif args.command == 'chat':
        chat_command(args)
    elif args.command == 'search':
        search_command(args)

if __name__ == "__main__":
    main()
