#!/usr/bin/env python3
"""
Populate Missing Database Tables
===============================
Creates and populates missing tables for news, rulings, FTA rates, and conversations.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

def create_news_tables(conn):
    """Create news-related tables."""
    print("Creating news tables...")
    
    # News items table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            published_date DATETIME NOT NULL,
            url TEXT,
            tags TEXT NOT NULL,  -- JSON array
            priority TEXT NOT NULL DEFAULT 'medium',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # System alerts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS system_alerts (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            read BOOLEAN NOT NULL DEFAULT 0,
            action_url TEXT,
            expires_at DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Trade summaries table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trade_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            period_start DATETIME NOT NULL,
            period_end DATETIME NOT NULL,
            total_trade_value REAL NOT NULL,
            import_value REAL NOT NULL,
            export_value REAL NOT NULL,
            trade_balance REAL NOT NULL,
            top_trading_partners TEXT NOT NULL,  -- JSON array
            commodity_highlights TEXT NOT NULL,  -- JSON array
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # News analytics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME NOT NULL,
            total_articles INTEGER NOT NULL DEFAULT 0,
            categories_breakdown TEXT NOT NULL,  -- JSON object
            sources_breakdown TEXT NOT NULL,     -- JSON object
            trending_topics TEXT NOT NULL,       -- JSON array
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

def create_rulings_tables(conn):
    """Create rulings-related tables."""
    print("Creating rulings tables...")
    
    # Tariff rulings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tariff_rulings (
            ruling_number TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            hs_code TEXT NOT NULL,
            commodity_description TEXT NOT NULL,
            ruling_date DATETIME NOT NULL,
            effective_date DATETIME NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            tariff_classification TEXT NOT NULL,
            duty_rate TEXT NOT NULL,
            origin_country TEXT,
            applicant TEXT,
            ruling_text TEXT NOT NULL,
            reference_documents TEXT NOT NULL,      -- JSON array
            related_rulings TEXT NOT NULL, -- JSON array
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Anti-dumping decisions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS anti_dumping_decisions (
            id TEXT PRIMARY KEY,
            case_number TEXT NOT NULL,
            title TEXT NOT NULL,
            product_description TEXT NOT NULL,
            hs_codes TEXT NOT NULL,         -- JSON array
            countries_involved TEXT NOT NULL, -- JSON array
            decision_type TEXT NOT NULL,
            decision_date DATETIME NOT NULL,
            effective_date DATETIME NOT NULL,
            duty_rate TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            summary TEXT NOT NULL,
            document_url TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Regulatory updates table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS regulatory_updates (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            update_type TEXT NOT NULL,
            published_date DATETIME NOT NULL,
            effective_date DATETIME NOT NULL,
            affected_codes TEXT NOT NULL,   -- JSON array
            impact_level TEXT NOT NULL DEFAULT 'medium',
            summary TEXT NOT NULL,
            full_text TEXT,
            document_url TEXT,
            contact_info TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Ruling statistics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ruling_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            period_start DATETIME NOT NULL,
            period_end DATETIME NOT NULL,
            total_rulings INTEGER NOT NULL DEFAULT 0,
            active_rulings INTEGER NOT NULL DEFAULT 0,
            new_rulings INTEGER NOT NULL DEFAULT 0,
            superseded_rulings INTEGER NOT NULL DEFAULT 0,
            anti_dumping_cases INTEGER NOT NULL DEFAULT 0,
            regulatory_updates INTEGER NOT NULL DEFAULT 0,
            category_breakdown TEXT NOT NULL,     -- JSON object
            impact_level_breakdown TEXT NOT NULL, -- JSON object
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

def populate_news_data(conn):
    """Populate news tables with sample data."""
    print("Populating news data...")
    
    # Sample news items
    news_items = [
        {
            'id': 'news-001',
            'title': 'New Tariff Classifications for Electric Vehicles',
            'summary': 'Updated HS codes and duty rates for electric vehicles and components effective January 2024.',
            'content': 'The Australian Border Force has announced new tariff classifications for electric vehicles and their components. These changes reflect the growing importance of sustainable transport and align with international standards. Key changes include new subcategories for battery electric vehicles, hybrid vehicles, and charging infrastructure components.',
            'category': 'tariff',
            'source': 'Australian Border Force',
            'published_date': (datetime.now() - timedelta(days=2)).isoformat(),
            'url': 'https://abf.gov.au/news/electric-vehicles-tariff',
            'tags': json.dumps(['electric vehicles', 'tariff', 'HS codes', 'sustainability']),
            'priority': 'high'
        },
        {
            'id': 'news-002',
            'title': 'CPTPP Trade Agreement Updates',
            'summary': 'New preferential rates under the Comprehensive and Progressive Trans-Pacific Partnership.',
            'content': 'Significant updates to preferential tariff rates under the CPTPP agreement, affecting agricultural products, textiles, and manufactured goods. Importers should review their supply chains to take advantage of reduced duty rates.',
            'category': 'trade_agreement',
            'source': 'Department of Foreign Affairs and Trade',
            'published_date': (datetime.now() - timedelta(days=5)).isoformat(),
            'url': 'https://dfat.gov.au/news/cptpp-updates',
            'tags': json.dumps(['CPTPP', 'preferential rates', 'agriculture', 'textiles']),
            'priority': 'medium'
        },
        {
            'id': 'news-003',
            'title': 'Customs Modernization Initiative',
            'summary': 'Digital transformation of customs processes and new online services.',
            'content': 'The Australian Border Force is implementing a comprehensive digital transformation program to modernize customs processes. New online services include automated classification tools, digital duty payment systems, and enhanced cargo tracking capabilities.',
            'category': 'customs',
            'source': 'Australian Border Force',
            'published_date': (datetime.now() - timedelta(days=7)).isoformat(),
            'url': 'https://abf.gov.au/news/modernization',
            'tags': json.dumps(['digitalization', 'customs', 'automation', 'online services']),
            'priority': 'medium'
        },
        {
            'id': 'news-004',
            'title': 'Anti-Dumping Investigation: Steel Products',
            'summary': 'New anti-dumping investigation initiated for certain steel products from multiple countries.',
            'content': 'The Anti-Dumping Commission has initiated an investigation into alleged dumping of certain steel products. The investigation covers hot-rolled steel coils and plates from China, South Korea, and Taiwan. Provisional measures may be implemented pending the outcome.',
            'category': 'regulation',
            'source': 'Anti-Dumping Commission',
            'published_date': (datetime.now() - timedelta(days=10)).isoformat(),
            'url': 'https://adc.gov.au/news/steel-investigation',
            'tags': json.dumps(['anti-dumping', 'steel', 'investigation', 'provisional measures']),
            'priority': 'high'
        },
        {
            'id': 'news-005',
            'title': 'Supply Chain Resilience Program',
            'summary': 'Government announces new program to strengthen supply chain resilience.',
            'content': 'The Australian Government has announced a new Supply Chain Resilience Program aimed at reducing dependence on single-source suppliers and strengthening critical supply chains. The program includes incentives for diversification and domestic production capabilities.',
            'category': 'industry',
            'source': 'Department of Industry',
            'published_date': (datetime.now() - timedelta(days=14)).isoformat(),
            'url': 'https://industry.gov.au/news/supply-chain-resilience',
            'tags': json.dumps(['supply chain', 'resilience', 'diversification', 'domestic production']),
            'priority': 'medium'
        }
    ]
    
    for item in news_items:
        conn.execute("""
            INSERT OR IGNORE INTO news_items 
            (id, title, summary, content, category, source, published_date, url, tags, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['id'], item['title'], item['summary'], item['content'],
            item['category'], item['source'], item['published_date'], item['url'],
            item['tags'], item['priority']
        ))
    
    # Sample system alerts
    alerts = [
        {
            'id': 'alert-001',
            'type': 'warning',
            'title': 'System Maintenance Scheduled',
            'message': 'Customs portal will be unavailable for maintenance on Saturday 2-4 AM AEST.',
            'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
            'read': False,
            'expires_at': (datetime.now() + timedelta(days=2)).isoformat()
        },
        {
            'id': 'alert-002',
            'type': 'info',
            'title': 'New Classification Guidelines Available',
            'message': 'Updated classification guidelines for technology products are now available.',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
            'read': False,
            'action_url': '/guidelines/technology'
        },
        {
            'id': 'alert-003',
            'type': 'success',
            'title': 'Database Update Complete',
            'message': 'Tariff database has been successfully updated with latest rates.',
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'read': True
        }
    ]
    
    for alert in alerts:
        conn.execute("""
            INSERT OR IGNORE INTO system_alerts 
            (id, type, title, message, timestamp, read, action_url, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert['id'], alert['type'], alert['title'], alert['message'],
            alert['timestamp'], alert['read'], alert.get('action_url'),
            alert.get('expires_at')
        ))
    
    # Sample trade summary
    trade_partners = json.dumps([
        {'country': 'China', 'trade_value': 235000, 'change_percent': 5.2},
        {'country': 'United States', 'trade_value': 89000, 'change_percent': -2.1},
        {'country': 'Japan', 'trade_value': 67000, 'change_percent': 3.8},
        {'country': 'South Korea', 'trade_value': 45000, 'change_percent': 7.5},
        {'country': 'Singapore', 'trade_value': 34000, 'change_percent': 1.2}
    ])
    
    commodity_highlights = json.dumps([
        {'commodity': 'Iron Ore', 'hs_code': '2601', 'value': 89000, 'change_percent': 12.5},
        {'commodity': 'Coal', 'hs_code': '2701', 'value': 67000, 'change_percent': -5.2},
        {'commodity': 'Beef', 'hs_code': '0201', 'value': 23000, 'change_percent': 8.9},
        {'commodity': 'Wheat', 'hs_code': '1001', 'value': 18000, 'change_percent': 15.3}
    ])
    
    conn.execute("""
        INSERT OR IGNORE INTO trade_summaries 
        (period, period_start, period_end, total_trade_value, import_value, export_value, 
         trade_balance, top_trading_partners, commodity_highlights)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        '2024-Q1',
        '2024-01-01',
        '2024-03-31',
        567000.0,
        234000.0,
        333000.0,
        99000.0,
        trade_partners,
        commodity_highlights
    ))

def populate_rulings_data(conn):
    """Populate rulings tables with sample data."""
    print("Populating rulings data...")
    
    # Sample tariff rulings
    rulings = [
        {
            'ruling_number': 'TR-2024-001',
            'title': 'Classification of Smart Home Devices',
            'description': 'Tariff classification ruling for internet-connected home automation devices.',
            'hs_code': '8517.62.00',
            'commodity_description': 'Smart home hubs and connected devices for home automation',
            'ruling_date': (datetime.now() - timedelta(days=30)).isoformat(),
            'effective_date': (datetime.now() - timedelta(days=15)).isoformat(),
            'status': 'active',
            'tariff_classification': '8517.62.00',
            'duty_rate': '5%',
            'origin_country': 'China',
            'applicant': 'Tech Imports Pty Ltd',
            'ruling_text': 'The subject goods are classified under HS code 8517.62.00 as machines for the reception, conversion and transmission or regeneration of voice, images or other data.',
            'reference_documents': json.dumps(['WCO Classification Opinion 8517.62/1', 'Australian Customs Notice 2024-01']),
            'related_rulings': json.dumps(['TR-2023-089', 'TR-2023-156'])
        },
        {
            'ruling_number': 'TR-2024-002',
            'title': 'Electric Vehicle Battery Classification',
            'description': 'Classification of lithium-ion batteries for electric vehicles.',
            'hs_code': '8507.60.00',
            'commodity_description': 'Lithium-ion batteries designed for electric vehicles',
            'ruling_date': (datetime.now() - timedelta(days=45)).isoformat(),
            'effective_date': (datetime.now() - timedelta(days=30)).isoformat(),
            'status': 'active',
            'tariff_classification': '8507.60.00',
            'duty_rate': 'Free',
            'origin_country': 'South Korea',
            'applicant': 'Green Energy Solutions',
            'ruling_text': 'Lithium-ion batteries specifically designed for electric vehicles are classified under HS code 8507.60.00.',
            'reference_documents': json.dumps(['WCO Classification Opinion 8507.60/2', 'Environmental Goods Agreement']),
            'related_rulings': json.dumps(['TR-2023-234'])
        }
    ]
    
    for ruling in rulings:
        conn.execute("""
            INSERT OR IGNORE INTO tariff_rulings 
            (ruling_number, title, description, hs_code, commodity_description, ruling_date,
             effective_date, status, tariff_classification, duty_rate, origin_country, applicant,
             ruling_text, reference_documents, related_rulings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ruling['ruling_number'], ruling['title'], ruling['description'], ruling['hs_code'],
            ruling['commodity_description'], ruling['ruling_date'], ruling['effective_date'],
            ruling['status'], ruling['tariff_classification'], ruling['duty_rate'],
            ruling['origin_country'], ruling['applicant'], ruling['ruling_text'],
            ruling['reference_documents'], ruling['related_rulings']
        ))
    
    # Sample anti-dumping decisions
    ad_decisions = [
        {
            'id': 'AD-2024-001',
            'case_number': 'ADC-2024-001',
            'title': 'Steel Wire Rod from China and Taiwan',
            'product_description': 'Hot-rolled steel wire rod in coils',
            'hs_codes': json.dumps(['7213.91.00', '7213.99.00']),
            'countries_involved': json.dumps(['China', 'Taiwan']),
            'decision_type': 'preliminary',
            'decision_date': (datetime.now() - timedelta(days=60)).isoformat(),
            'effective_date': (datetime.now() - timedelta(days=45)).isoformat(),
            'duty_rate': '15.2% - 23.7%',
            'status': 'active',
            'summary': 'Preliminary determination of dumping for steel wire rod imports. Provisional measures implemented.',
            'document_url': 'https://adc.gov.au/cases/2024/steel-wire-rod'
        }
    ]
    
    for decision in ad_decisions:
        conn.execute("""
            INSERT OR IGNORE INTO anti_dumping_decisions 
            (id, case_number, title, product_description, hs_codes, countries_involved,
             decision_type, decision_date, effective_date, duty_rate, status, summary, document_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision['id'], decision['case_number'], decision['title'], decision['product_description'],
            decision['hs_codes'], decision['countries_involved'], decision['decision_type'],
            decision['decision_date'], decision['effective_date'], decision['duty_rate'],
            decision['status'], decision['summary'], decision['document_url']
        ))

def populate_fta_rates(conn):
    """Populate FTA rates table with sample data."""
    print("Populating FTA rates...")
    
    fta_rates = [
        ('0101.21.00', 'AUSFTA', 'US', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('0201.10.00', 'AUSFTA', 'US', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('8703.21.00', 'KAFTA', 'KR', 5.00, 'ad_valorem', 'B', '2024-01-01', '2030-01-01', None, None, False, 'Regional value content 45%'),
        ('8703.22.00', 'KAFTA', 'KR', 5.00, 'ad_valorem', 'B', '2024-01-01', '2030-01-01', None, None, False, 'Regional value content 45%'),
        ('1001.11.00', 'CPTPP', 'CA', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('1001.19.00', 'CPTPP', 'CA', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('0406.10.00', 'CPTPP', 'NZ', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('8517.12.00', 'JAEPA', 'JP', 3.00, 'ad_valorem', 'C', '2024-01-01', '2035-01-01', None, None, False, 'Regional value content 40%'),
        ('8517.18.00', 'JAEPA', 'JP', 3.00, 'ad_valorem', 'C', '2024-01-01', '2035-01-01', None, None, False, 'Regional value content 40%'),
        ('2601.11.00', 'ChAFTA', 'CN', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('2601.12.00', 'ChAFTA', 'CN', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('0902.10.00', 'AIFTA', 'IN', 7.50, 'ad_valorem', 'D', '2024-01-01', '2040-01-01', None, None, True, 'Regional value content 35%'),
        ('0902.20.00', 'AIFTA', 'IN', 7.50, 'ad_valorem', 'D', '2024-01-01', '2040-01-01', None, None, True, 'Regional value content 35%'),
        ('5201.00.00', 'TAFTA', 'TH', 0.00, 'ad_valorem', 'A', '2024-01-01', None, None, None, False, 'Wholly obtained or produced'),
        ('2710.19.00', 'SAFTA', 'SG', 2.00, 'ad_valorem', 'B', '2024-01-01', '2028-01-01', None, None, False, 'Regional value content 40%')
    ]
    
    for (hs_code, fta_code, country_code, preferential_rate, rate_type, staging_category, 
         effective_date, elimination_date, quota_quantity, quota_unit, safeguard_applicable, rule_of_origin) in fta_rates:
        conn.execute("""
            INSERT OR IGNORE INTO fta_rates 
            (hs_code, fta_code, country_code, preferential_rate, rate_type, staging_category,
             effective_date, elimination_date, quota_quantity, quota_unit, safeguard_applicable, rule_of_origin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (hs_code, fta_code, country_code, preferential_rate, rate_type, staging_category,
              effective_date, elimination_date, quota_quantity, quota_unit, safeguard_applicable, rule_of_origin))

def populate_conversations(conn):
    """Populate conversation tables with sample data."""
    print("Populating conversations...")
    
    # Sample conversations
    conversations = [
        {
            'session_id': 'session-001',
            'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
            'last_updated': (datetime.now() - timedelta(days=3)).isoformat(),
            'context': json.dumps({'topic': 'classification', 'category': 'electronics'})
        },
        {
            'session_id': 'session-002',
            'created_at': (datetime.now() - timedelta(days=7)).isoformat(),
            'last_updated': (datetime.now() - timedelta(days=6)).isoformat(),
            'context': json.dumps({'topic': 'duty_calculation', 'category': 'automotive'})
        }
    ]
    
    conversation_ids = []
    for conv in conversations:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO conversations 
            (session_id, created_at, last_updated, context)
            VALUES (?, ?, ?, ?)
        """, (conv['session_id'], conv['created_at'], conv['last_updated'], conv['context']))
        
        # Get the conversation ID for messages
        cursor = conn.execute("SELECT id FROM conversations WHERE session_id = ?", (conv['session_id'],))
        result = cursor.fetchone()
        if result:
            conversation_ids.append((result[0], conv['session_id']))
    
    # Sample conversation messages
    if conversation_ids:
        messages = [
            {
                'conversation_id': conversation_ids[0][0],
                'role': 'user',
                'content': 'I need help classifying wireless earbuds with noise cancellation features.',
                'timestamp': (datetime.now() - timedelta(days=3)).isoformat(),
                'message_metadata': json.dumps({'type': 'text', 'source': 'web'})
            },
            {
                'conversation_id': conversation_ids[0][0],
                'role': 'assistant',
                'content': 'Wireless earbuds with noise cancellation are typically classified under HS code 8518.30.00 as headphones and earphones. The noise cancellation feature is considered an integral part of the audio equipment.',
                'timestamp': (datetime.now() - timedelta(days=3, minutes=2)).isoformat(),
                'message_metadata': json.dumps({'type': 'response', 'confidence': 0.95})
            }
        ]
        
        if len(conversation_ids) > 1:
            messages.extend([
                {
                    'conversation_id': conversation_ids[1][0],
                    'role': 'user',
                    'content': 'What is the duty rate for brake pads imported from Germany?',
                    'timestamp': (datetime.now() - timedelta(days=7)).isoformat(),
                    'message_metadata': json.dumps({'type': 'text', 'source': 'web'})
                },
                {
                    'conversation_id': conversation_ids[1][0],
                    'role': 'assistant',
                    'content': 'Brake pads are classified under HS code 8708.30.00. The general duty rate is 5%, but under the EU-Australia FTA, goods from Germany may qualify for preferential treatment with a reduced rate of 2.5%.',
                    'timestamp': (datetime.now() - timedelta(days=7, minutes=1)).isoformat(),
                    'message_metadata': json.dumps({'type': 'response', 'confidence': 0.92})
                }
            ])
        
        for msg in messages:
            conn.execute("""
                INSERT OR IGNORE INTO conversation_messages 
                (conversation_id, role, content, timestamp, message_metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (msg['conversation_id'], msg['role'], msg['content'], msg['timestamp'], msg['message_metadata']))

def main():
    """Main function to create and populate all missing tables."""
    db_path = Path('customs_portal.db')
    if not db_path.exists():
        print('❌ Database not found. Please run migration first.')
        return
    
    conn = sqlite3.connect(db_path)
    try:
        print("=== POPULATING MISSING DATABASE TABLES ===\n")
        
        # Create tables
        create_news_tables(conn)
        create_rulings_tables(conn)
        
        # Populate data
        populate_news_data(conn)
        populate_rulings_data(conn)
        populate_fta_rates(conn)
        populate_conversations(conn)
        
        # Commit all changes
        conn.commit()
        
        print("\n✅ All missing tables created and populated successfully!")
        
        # Verify results
        print("\n📊 VERIFICATION:")
        tables_to_check = [
            'news_items', 'system_alerts', 'trade_summaries', 'news_analytics',
            'tariff_rulings', 'anti_dumping_decisions', 'regulatory_updates', 'ruling_statistics',
            'fta_rates', 'conversations', 'conversation_messages'
        ]
        
        for table in tables_to_check:
            try:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                status = "✅" if count > 0 else "❌"
                print(f"  {table}: {count} records {status}")
            except sqlite3.OperationalError:
                print(f"  {table}: Table not found ❌")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
