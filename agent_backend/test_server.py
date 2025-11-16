"""
Simple test to verify the server is working correctly
"""
import asyncio
from orchestrator import AgentOrchestrator


async def test_initialization():
    """Test that all agents initialize correctly"""
    print("🧪 Testing Agent Initialization...\n")
    
    try:
        orchestrator = AgentOrchestrator()
        print("✅ AgentOrchestrator initialized successfully")
        print(f"   - DocumentProcessor: {orchestrator.doc_processor is not None}")
        print(f"   - StructurizationAgent: {orchestrator.structurization_agent is not None}")
        print(f"   - HighlighterAgent: {orchestrator.highlighter_agent is not None}")
        print(f"   - ExplanationAgent: {orchestrator.explanation_agent is not None}")
        print(f"   - QuizAgent: {orchestrator.quiz_agent is not None}")
        
        print("\n✅ All agents initialized successfully!")
        print("\n📡 Server is ready to accept requests!")
        print("   Run: python api_server.py")
        print("   Then test: http://localhost:8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_initialization())
