import os
from typing import Dict

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

from faq_processor import FAQProcessor


class RAGService:
  """Simple RAG service for Shell FAQ answering"""

  def __init__(self, openai_api_key: str = None):
    self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if not self.api_key:
      raise ValueError("OpenAI API key required")

    self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0, openai_api_key=self.api_key)

    self.faq_processor = FAQProcessor()

    # Load or build index
    try:
      self.faq_processor.load_index()
      print("✅ Loaded existing FAQ index")
    except FileNotFoundError:
      print("Building new FAQ index...")
      self.faq_processor.load_faqs()
      self.faq_processor.build_index()
      self.faq_processor.save_index()
      print("✅ Built and saved FAQ index")

  def answer_question(self, question: str) -> Dict:
    """Answer a question using RAG"""
    # Retrieve relevant FAQs
    relevant_faqs = self.faq_processor.search(question, top_k=3)

    if not relevant_faqs:
      return {
        "answer": "I couldn't find relevant information to answer your question. Please contact Shell customer support directly.",
        "sources": [],
      }

    # Format context
    context = "\n\n".join(
      [f"FAQ {i + 1}:\nQ: {faq['question']}\nA: {faq['answer']}" for i, faq in enumerate(relevant_faqs)]
    )

    # Create prompt
    prompt = f"""You are a helpful Shell customer service assistant. Use the following FAQ information to answer the customer's question accurately and helpfully.

Context from Shell FAQs:
{context}

Customer Question: {question}

Please provide a clear, helpful answer based on the FAQ information. If the FAQs don't contain enough information, politely say so and suggest contacting Shell support directly.

Answer:"""

    # Generate response
    try:
      response = self.llm.invoke([HumanMessage(content=prompt)])
      answer = response.content
    except Exception as e:
      answer = f"I apologize, but I'm having trouble processing your question right now. Error: {str(e)}"

    return {"answer": answer, "sources": relevant_faqs, "question": question}


if __name__ == "__main__":
  # Test the service
  rag = RAGService()

  test_questions = [
    "How can I download the Shell app?",
    "What is Pay at Pump?",
    "Where can I find Shell electric vehicle charging?",
  ]

  for question in test_questions:
    print(f"\nQ: {question}")
    result = rag.answer_question(question)
    print(f"A: {result['answer']}")
    print(f"Sources used: {len(result['sources'])}")
