"""
Example usage of the Agent Backend system.

This script demonstrates how to use the agent orchestrator to process
PDF documents and generate all features.
"""

import asyncio
import json
from orchestrator import AgentOrchestrator


async def process_full_document():
    """Example: Process a complete document through all agents"""
    
    orchestrator = AgentOrchestrator()
    
    # Replace with your PDF path
    pdf_path = "path/to/your/document.pdf"
    
    try:
        # Process the entire document
        results = await orchestrator.process_document(
            pdf_path=pdf_path,
            num_quiz_questions=15
        )
        
        # Save results to file
        with open("output_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n📊 Results Summary:")
        print(f"  - Total Pages: {results['metadata']['total_pages']}")
        print(f"  - Topics Found: {results['metadata']['total_topics']}")
        print(f"  - Highlights: {results['metadata']['total_highlights']}")
        print(f"  - Quiz Questions: {results['metadata']['total_questions']}")
        
        print("\n✅ Results saved to 'output_results.json'")
        
        return results
        
    except Exception as e:
        print(f"❌ Error processing document: {str(e)}")
        raise


async def process_single_feature_example():
    """Example: Process only the structure feature"""
    
    orchestrator = AgentOrchestrator()
    pdf_path = "path/to/your/document.pdf"
    
    try:
        # Get only the structure
        structure_result = await orchestrator.process_single_feature(
            pdf_path=pdf_path,
            feature="structure"
        )
        
        print("\n📋 Document Structure:")
        for topic in structure_result['structure']['topics']:
            print(f"\n{topic['title']} (Pages {topic['page_range']})")
            for subtopic in topic['subtopics']:
                print(f"  └─ {subtopic['title']} (Page {subtopic['page_reference']})")
        
        return structure_result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise


async def main():
    """Main entry point"""
    
    print("=" * 60)
    print("Agent Backend - Document Processing System")
    print("=" * 60)
    
    # Choose which example to run
    choice = input("\nSelect option:\n1. Process full document\n2. Process structure only\n\nChoice (1 or 2): ")
    
    if choice == "1":
        await process_full_document()
    elif choice == "2":
        await process_single_feature_example()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
