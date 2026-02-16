#!/usr/bin/env python3
"""
Explore the database to see what data is available
"""
import sqlite3
import json
import sys
import os

def explore_database():
    db_path = "backend/data/musicology.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== DATABASE EXPLORATION ===\n")
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Available tables: {[table[0] for table in tables]}\n")
    
    # Check each table
    for table in tables:
        table_name = table[0]
        print(f"📊 TABLE: {table_name}")
        print("-" * 40)
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Columns: {[col[1] for col in columns]}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Row count: {count}")
        
        if count > 0:
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            samples = cursor.fetchall()
            print("Sample data:")
            for i, sample in enumerate(samples):
                print(f"  Row {i+1}: {sample}")
            
            # For text-heavy tables, show some content snippets
            if table_name == 'events':
                cursor.execute("SELECT title, description, sentence FROM events WHERE title IS NOT NULL OR description IS NOT NULL LIMIT 5")
                text_samples = cursor.fetchall()
                print("\nText content samples:")
                for i, (title, desc, sentence) in enumerate(text_samples):
                    print(f"  Event {i+1}:")
                    if title:
                        print(f"    Title: {title[:100]}...")
                    if desc:
                        print(f"    Description: {desc[:100]}...")
                    if sentence:
                        print(f"    Sentence: {sentence[:100]}...")
                    print()
            
            elif table_name == 'nlp_results':
                cursor.execute("SELECT summary, entities FROM nlp_results WHERE summary IS NOT NULL LIMIT 3")
                nlp_samples = cursor.fetchall()
                print("\nNLP content samples:")
                for i, (summary, entities) in enumerate(nlp_samples):
                    print(f"  NLP {i+1}:")
                    if summary:
                        print(f"    Summary: {summary[:150]}...")
                    if entities:
                        try:
                            ent_data = json.loads(entities) if isinstance(entities, str) else entities
                            if isinstance(ent_data, list) and len(ent_data) > 0:
                                print(f"    Sample entities: {ent_data[:3]}")
                        except:
                            print(f"    Entities: {str(entities)[:100]}...")
                    print()
            
            elif table_name == 'documents':
                cursor.execute("SELECT filename, decade, metadata_json FROM documents")
                doc_samples = cursor.fetchall()
                print("\nDocument samples:")
                for filename, decade, metadata in doc_samples:
                    print(f"  • {filename} (Decade: {decade})")
                    if metadata:
                        try:
                            meta_data = json.loads(metadata) if isinstance(metadata, str) else metadata
                            print(f"    Metadata keys: {list(meta_data.keys()) if isinstance(meta_data, dict) else 'Not a dict'}")
                        except:
                            print(f"    Metadata: {str(metadata)[:100]}...")
                print()
        
        print("=" * 50)
        print()
    
    # Now let's do a broader search for any musical terms
    print("🎵 SEARCHING FOR ANY MUSICAL TERMS...")
    print("-" * 50)
    
    musical_terms = [
        'music', 'raga', 'tala', 'carnatic', 'hindustani', 'classical',
        'melody', 'rhythm', 'composition', 'concert', 'performance',
        'singer', 'musician', 'instrument', 'vocal', 'veena', 'violin',
        'mridangam', 'tabla', 'flute', 'sitar'
    ]
    
    for term in musical_terms:
        # Quick search in events
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE LOWER(title) LIKE LOWER(?) 
               OR LOWER(description) LIKE LOWER(?) 
               OR LOWER(sentence) LIKE LOWER(?)
        """, (f'%{term}%', f'%{term}%', f'%{term}%'))
        
        event_count = cursor.fetchone()[0]
        
        # Quick search in nlp_results
        cursor.execute("""
            SELECT COUNT(*) FROM nlp_results 
            WHERE LOWER(summary) LIKE LOWER(?)
        """, (f'%{term}%',))
        
        nlp_count = cursor.fetchone()[0]
        
        total = event_count + nlp_count
        if total > 0:
            print(f"'{term}': {total} results (Events: {event_count}, NLP: {nlp_count})")
    
    conn.close()

if __name__ == "__main__":
    explore_database()