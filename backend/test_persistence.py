"""
Test script to verify SQLite database persistence across sessions.
This script will:
1. Connect to the database
2. Check existing data
3. Add a test conversation
4. Verify the data persists
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import create_database_engine
from models.conversation import Conversation, ConversationMessage
from sqlalchemy import text

async def test_database_persistence():
    """Test that data persists across database connections."""
    
    print("=== Testing SQLite Database Persistence ===")
    
    # Create engine and connect
    engine = await create_database_engine()
    
    # Test 1: Check existing data
    async with engine.begin() as conn:
        # Check tariff codes (should have 98 from migration)
        result = await conn.execute(text("SELECT COUNT(*) FROM tariff_codes"))
        tariff_count = result.scalar()
        print(f"Existing tariff codes: {tariff_count}")
        
        # Check conversations (should be empty initially)
        result = await conn.execute(text("SELECT COUNT(*) FROM conversations"))
        conversation_count = result.scalar()
        print(f"Existing conversations: {conversation_count}")
        
        # Check conversation messages
        result = await conn.execute(text("SELECT COUNT(*) FROM conversation_messages"))
        message_count = result.scalar()
        print(f"Existing conversation messages: {message_count}")
    
    # Test 2: Add a test conversation to verify persistence
    async with engine.begin() as conn:
        # Insert a test conversation
        await conn.execute(text("""
            INSERT INTO conversations (id, session_id, created_at, last_updated, context)
            VALUES (999, 'test-session-999', :created_at, :last_updated, '{}')
        """), {"created_at": datetime.now(), "last_updated": datetime.now()})
        
        # Insert a test message
        await conn.execute(text("""
            INSERT INTO conversation_messages (id, conversation_id, role, content, timestamp, message_metadata)
            VALUES (999, 999, 'user', 'This is a persistence test message', :timestamp, '{}')
        """), {"timestamp": datetime.now()})
        
        print("Added test conversation and message")
    
    # Test 3: Verify data was inserted
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM conversations WHERE session_id = 'test-session-999'"))
        test_conversations = result.scalar()
        
        result = await conn.execute(text("SELECT COUNT(*) FROM conversation_messages WHERE conversation_id = 999"))
        test_messages = result.scalar()
        
        print(f"Test conversations found: {test_conversations}")
        print(f"Test messages found: {test_messages}")
    
    # Test 4: Simulate session restart by creating new engine
    print("\n--- Simulating session restart ---")
    await engine.dispose()  # Close current connection
    
    # Create new engine (simulates backend restart)
    new_engine = await create_database_engine()
    
    # Test 5: Verify data still exists after "restart"
    async with new_engine.begin() as conn:
        # Check all data is still there
        result = await conn.execute(text("SELECT COUNT(*) FROM tariff_codes"))
        tariff_count_after = result.scalar()
        
        result = await conn.execute(text("SELECT COUNT(*) FROM conversations"))
        conversation_count_after = result.scalar()
        
        result = await conn.execute(text("SELECT COUNT(*) FROM conversation_messages"))
        message_count_after = result.scalar()
        
        # Check our test data specifically
        result = await conn.execute(text("SELECT session_id FROM conversations WHERE session_id = 'test-session-999'"))
        test_conversation = result.fetchone()
        
        result = await conn.execute(text("SELECT content FROM conversation_messages WHERE conversation_id = 999"))
        test_message = result.fetchone()
        
        print(f"Tariff codes after restart: {tariff_count_after}")
        print(f"Conversations after restart: {conversation_count_after}")
        print(f"Messages after restart: {message_count_after}")
        print(f"Test conversation session_id: {test_conversation[0] if test_conversation else 'NOT FOUND'}")
        print(f"Test message content: {test_message[0] if test_message else 'NOT FOUND'}")
    
    # Clean up test data
    async with new_engine.begin() as conn:
        await conn.execute(text("DELETE FROM conversation_messages WHERE conversation_id = 999"))
        await conn.execute(text("DELETE FROM conversations WHERE session_id = 'test-session-999'"))
        print("\nCleaned up test data")
    
    await new_engine.dispose()
    
    # Final verification
    print("\n=== Persistence Test Results ===")
    if tariff_count == tariff_count_after and tariff_count == 98:
        print("Tariff data persisted correctly")
    else:
        print("Tariff data persistence failed")
    
    if test_conversation and test_message:
        print("Conversation data persisted correctly")
    else:
        print("Conversation data persistence failed")
    
    print("SQLite database persistence verified!")

if __name__ == "__main__":
    asyncio.run(test_database_persistence())
