"""
Test the API endpoints to ensure they're working correctly
Run this while the server is running in another terminal
"""
import requests
import sys


def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        print("   Start it with: python start_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_api_docs():
    """Test if API documentation is available"""
    print("\nTesting API documentation...")
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API documentation is available at http://localhost:8000/docs")
            return True
        else:
            print(f"❌ API docs returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing API docs: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("🧪 Testing Sensei Agent Backend API")
    print("=" * 60)
    print()
    
    tests = [
        test_health_check,
        test_api_docs
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if all(results):
        print("✅ All tests passed! Server is working correctly.")
        print("\n📝 Available Endpoints:")
        print("   POST /api/process-document - Process full document")
        print("   POST /api/structure - Get document structure")
        print("   POST /api/highlights - Get text highlights")
        print("   POST /api/explanations - Get explanations")
        print("   POST /api/quiz - Generate quiz questions")
    else:
        print("❌ Some tests failed. Please check the server.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
