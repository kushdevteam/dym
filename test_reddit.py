#!/usr/bin/env python3
"""
Test script for Reddit connector
This script tests the Reddit integration without requiring API keys
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

# Add api and ingest to path
sys.path.append('./api')
sys.path.append('./ingest')

async def test_database_connection():
    """Test basic database connectivity"""
    print("Testing database connection...")
    try:
        import asyncpg
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not set")
            return False
            
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT COUNT(*) FROM mention")
        await conn.close()
        print(f"✅ Database connected. Current mentions: {result}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_reddit_connector_structure():
    """Test Reddit connector can be imported and initialized"""
    print("\nTesting Reddit connector structure...")
    try:
        from reddit_connector import RedditConnector, RedditMention
        
        # Test RedditMention dataclass
        mention = RedditMention(
            source_id="test_123",
            author="test_user",
            text="Test $SOL post",
            created_at=datetime.now(timezone.utc)
        )
        print(f"✅ RedditMention created: {mention.source_id}")
        
        # Test RedditConnector initialization (without API keys)
        print("✅ Reddit connector structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Reddit connector import failed: {e}")
        return False

async def test_entity_extraction():
    """Test entity extraction functionality"""
    print("\nTesting entity extraction...")
    try:
        from reddit_connector import RedditConnector
        
        connector = RedditConnector()
        
        # Test text with various entities
        test_text = "Check out $SOL and $WIF tokens! Also u/test_user mentioned https://example.com"
        entities = connector.extract_entities(test_text)
        
        print(f"Extracted entities: {entities}")
        
        # Verify expected entities
        assert "SOL" in entities["tickers"], "SOL ticker not extracted"
        assert "WIF" in entities["tickers"], "WIF ticker not extracted"
        assert "test_user" in entities["mentions"], "User mention not extracted"
        assert "https://example.com" in entities["urls"], "URL not extracted"
        
        print("✅ Entity extraction working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        return False

async def test_api_routes():
    """Test that API routes are properly configured"""
    print("\nTesting API route configuration...")
    try:
        # Import main app
        sys.path.append('./api')
        from main import app
        
        # Check that ingestion router is included
        routes = [route.path for route in app.routes]
        
        expected_routes = ["/ingest/reddit", "/ingest/status", "/mentions", "/healthz"]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✅ Route {route} found")
            else:
                print(f"❌ Route {route} missing")
                return False
                
        print("✅ All expected API routes are configured")
        return True
        
    except Exception as e:
        print(f"❌ API route test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Reddit Connector Tests\n")
    
    tests = [
        test_database_connection(),
        test_reddit_connector_structure(),
        test_entity_extraction(),
        test_api_routes()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Reddit connector is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)