import os
from rag_system import RAGSystem
from gemini_service import GeminiService


BASE_DIR = os.path.dirname(__file__)
PDF_PATH = os.path.join(BASE_DIR, "3.1 Dynamic Arrays.pdf")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("Testing Sensei.i System\n")

# Test 1: RAG System
print("1. Testing RAG...")
rag = RAGSystem()
doc_id = rag.process_pdf(PDF_PATH)
print(f"✓ PDF processed: {doc_id}\n")

# Test 2: Query
print("2. Testing query...")
results = rag.query("What are dynamic arrays?", n_results=3)
print(f"✓ Found {len(results['results'])} results\n")
print("Context preview:")
print(results['context'][:300] + "...\n")

# Test 3: Gemini
print("3. Testing Gemini...")
gemini = GeminiService(api_key=GEMINI_API_KEY)
questions = gemini.generate_quiz(results['context'], num_questions=2)
print(f"✓ Generated {len(questions)} questions\n")

print("First question:")
print(questions[0]['question'])
print("\n✅ All tests passed!")
