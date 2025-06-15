#!/usr/bin/env python3
"""Check conversations table structure."""

import sqlite3
from pathlib import Path

def check_conversations_structure():
    db_path = Path('customs_portal.db')
    if not db_path.exists():
        print('❌ Database not found.')
        return
    
    conn = sqlite3.connect(db_path)
    try:
        # Check conversations table structure
        cursor = conn.execute("PRAGMA table_info(conversations)")
        columns = cursor.fetchall()
        
        print("Conversations table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check conversation_messages table structure
        cursor = conn.execute("PRAGMA table_info(conversation_messages)")
        columns = cursor.fetchall()
        
        print("\nConversation Messages table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_conversations_structure()
