#!/usr/bin/env python3
"""
Script to search for specific musical terms in the musicology database
"""
import sqlite3
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def search_database():
    db_path = "backend/data/musicology.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    # Terms to search for
    terms = ['marga', 'desi', 'raagas', 'taala', 'prabandha', 'vaadyai']
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== SEARCHING FOR MUSICAL TERMS IN DATABASE ===\n")
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Available tables: {[table[0] for table in tables]}\n")
    
    results = {}
    
    for term in terms:
        print(f"🔍 Searching for: '{term}'")
        print("-" * 50)
        results[term] = {}
        
        # Search in Events table
        cursor.execute("""
            SELECT id, title, description, sentence, event_type, date_str 
            FROM events 
            WHERE title LIKE ? OR description LIKE ? OR sentence LIKE ?
        """, (f'%{term}%', f'%{term}%', f'%{term}%'))
        
        events = cursor.fetchall()
        if events:
            results[term]['events'] = []
            print(f"  📅 Found {len(events)} events:")
            for event in events:
                event_data = {
                    'id': event[0],
                    'title': event[1],
                    'description': event[2],
                    'sentence': event[3],
                    'type': event[4],
                    'date': event[5]
                }
                results[term]['events'].append(event_data)
                print(f"    • ID {event[0]}: {event[1] or 'No title'}")
                print(f"      Date: {event[5] or 'Unknown'}")
                print(f"      Description: {(event[2] or event[3] or 'No description')[:100]}...")
                print()
        
        # Search in NLP Results
        cursor.execute("""
            SELECT id, summary, entities, topics 
            FROM nlp_results 
            WHERE summary LIKE ? OR entities LIKE ? OR topics LIKE ?
        """, (f'%{term}%', f'%{term}%', f'%{term}%'))
        
        nlp_results = cursor.fetchall()
        if nlp_results:
            results[term]['nlp_results'] = []
            print(f"  🧠 Found {len(nlp_results)} NLP results:")
            for nlp in nlp_results:
                nlp_data = {
                    'id': nlp[0],
                    'summary': nlp[1],
                    'entities': nlp[2],
                    'topics': nlp[3]
                }
                results[term]['nlp_results'].append(nlp_data)
                print(f"    • NLP ID {nlp[0]}")
                print(f"      Summary: {(nlp[1] or 'No summary')[:100]}...")
                if nlp[2]:  # entities
                    try:
                        entities = json.loads(nlp[2]) if isinstance(nlp[2], str) else nlp[2]
                        print(f"      Entities: {entities}")
                    except:
                        print(f"      Entities: {nlp[2]}")
                print()
        
        # Search in Documents
        cursor.execute("""
            SELECT id, filename, metadata_json, decade 
            FROM documents 
            WHERE filename LIKE ? OR metadata_json LIKE ?
        """, (f'%{term}%', f'%{term}%'))
        
        docs = cursor.fetchall()
        if docs:
            results[term]['documents'] = []
            print(f"  📄 Found {len(docs)} documents:")
            for doc in docs:
                doc_data = {
                    'id': doc[0],
                    'filename': doc[1],
                    'metadata': doc[2],
                    'decade': doc[3]
                }
                results[term]['documents'].append(doc_data)
                print(f"    • Doc ID {doc[0]}: {doc[1]}")
                print(f"      Decade: {doc[3] or 'Unknown'}")
                print()
        
        if not events and not nlp_results and not docs:
            print(f"  ❌ No results found for '{term}'\n")
        
        print("=" * 60)
        print()
    
    conn.close()
    
    # Save results to JSON file
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Search results saved to 'search_results.json'")
    
    # Summary
    print("\n=== SUMMARY ===")
    for term in terms:
        total_results = 0
        if term in results:
            total_results += len(results[term].get('events', []))
            total_results += len(results[term].get('nlp_results', []))
            total_results += len(results[term].get('documents', []))
        print(f"{term}: {total_results} total results")

if __name__ == "__main__":
    search_database()