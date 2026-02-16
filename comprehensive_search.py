#!/usr/bin/env python3
"""
Comprehensive search for musical terms with variations and diacritical marks
"""
import sqlite3
import json
import sys
import os
import re

def search_database():
    db_path = "backend/data/musicology.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    # Terms with variations including Sanskrit diacritical marks
    term_variations = {
        'marga': ['marga', 'mārga', 'margam', 'mārgam'],
        'desi': ['desi', 'deśi', 'deshi', 'deśī'],
        'raagas': ['raaga', 'rāga', 'raga', 'raagas', 'rāgas', 'ragas'],
        'taala': ['taala', 'tāla', 'tala', 'taal', 'tāl'],
        'prabandha': ['prabandha', 'prabandham', 'prabandhā'],
        'vaadyai': ['vaadya', 'vādya', 'vadya', 'vaadyai', 'vādyai']
    }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== COMPREHENSIVE SEARCH FOR MUSICAL TERMS ===\n")
    
    results = {}
    
    for main_term, variations in term_variations.items():
        print(f"🔍 Searching for: '{main_term}' and variations: {variations}")
        print("-" * 70)
        results[main_term] = {}
        found_any = False
        
        for variation in variations:
            # Search in Events table
            cursor.execute("""
                SELECT id, title, description, sentence, event_type, date_str, document_id
                FROM events 
                WHERE LOWER(title) LIKE LOWER(?) 
                   OR LOWER(description) LIKE LOWER(?) 
                   OR LOWER(sentence) LIKE LOWER(?)
            """, (f'%{variation}%', f'%{variation}%', f'%{variation}%'))
            
            events = cursor.fetchall()
            if events:
                if 'events' not in results[main_term]:
                    results[main_term]['events'] = []
                found_any = True
                print(f"  📅 Found {len(events)} events for '{variation}':")
                for event in events:
                    # Get document info
                    cursor.execute("SELECT filename FROM documents WHERE id = ?", (event[6],))
                    doc_result = cursor.fetchone()
                    doc_name = doc_result[0] if doc_result else "Unknown"
                    
                    event_data = {
                        'id': event[0],
                        'title': event[1],
                        'description': event[2],
                        'sentence': event[3],
                        'type': event[4],
                        'date': event[5],
                        'document': doc_name,
                        'search_term': variation
                    }
                    results[main_term]['events'].append(event_data)
                    print(f"    • ID {event[0]} from {doc_name}")
                    print(f"      Title: {event[1] or 'No title'}")
                    print(f"      Date: {event[5] or 'Unknown'}")
                    
                    # Show the relevant text snippet
                    text = event[2] or event[3] or event[1] or ""
                    if text:
                        # Find and highlight the matching term
                        pattern = re.compile(re.escape(variation), re.IGNORECASE)
                        match = pattern.search(text)
                        if match:
                            start = max(0, match.start() - 50)
                            end = min(len(text), match.end() + 50)
                            snippet = text[start:end]
                            highlighted = pattern.sub(f"**{variation.upper()}**", snippet)
                            print(f"      Context: ...{highlighted}...")
                    print()
            
            # Search in NLP Results
            cursor.execute("""
                SELECT id, summary, entities, topics, document_id
                FROM nlp_results 
                WHERE LOWER(summary) LIKE LOWER(?) 
                   OR LOWER(entities) LIKE LOWER(?) 
                   OR LOWER(topics) LIKE LOWER(?)
            """, (f'%{variation}%', f'%{variation}%', f'%{variation}%'))
            
            nlp_results = cursor.fetchall()
            if nlp_results:
                if 'nlp_results' not in results[main_term]:
                    results[main_term]['nlp_results'] = []
                found_any = True
                print(f"  🧠 Found {len(nlp_results)} NLP results for '{variation}':")
                for nlp in nlp_results:
                    # Get document info
                    cursor.execute("SELECT filename FROM documents WHERE id = ?", (nlp[4],))
                    doc_result = cursor.fetchone()
                    doc_name = doc_result[0] if doc_result else "Unknown"
                    
                    nlp_data = {
                        'id': nlp[0],
                        'summary': nlp[1],
                        'entities': nlp[2],
                        'topics': nlp[3],
                        'document': doc_name,
                        'search_term': variation
                    }
                    results[main_term]['nlp_results'].append(nlp_data)
                    print(f"    • NLP ID {nlp[0]} from {doc_name}")
                    
                    # Show relevant summary snippet
                    if nlp[1]:
                        pattern = re.compile(re.escape(variation), re.IGNORECASE)
                        match = pattern.search(nlp[1])
                        if match:
                            start = max(0, match.start() - 50)
                            end = min(len(nlp[1]), match.end() + 50)
                            snippet = nlp[1][start:end]
                            highlighted = pattern.sub(f"**{variation.upper()}**", snippet)
                            print(f"      Summary: ...{highlighted}...")
                    
                    # Check entities
                    if nlp[2]:
                        try:
                            entities = json.loads(nlp[2]) if isinstance(nlp[2], str) else nlp[2]
                            if isinstance(entities, list):
                                matching_entities = [e for e in entities if isinstance(e, dict) and 
                                                   variation.lower() in str(e.get('text', '')).lower()]
                                if matching_entities:
                                    print(f"      Matching entities: {matching_entities}")
                        except:
                            if variation.lower() in str(nlp[2]).lower():
                                print(f"      Entities contain term: {nlp[2]}")
                    print()
            
            # Search in Documents
            cursor.execute("""
                SELECT id, filename, metadata_json, decade 
                FROM documents 
                WHERE LOWER(filename) LIKE LOWER(?) OR LOWER(metadata_json) LIKE LOWER(?)
            """, (f'%{variation}%', f'%{variation}%'))
            
            docs = cursor.fetchall()
            if docs:
                if 'documents' not in results[main_term]:
                    results[main_term]['documents'] = []
                found_any = True
                print(f"  📄 Found {len(docs)} documents for '{variation}':")
                for doc in docs:
                    doc_data = {
                        'id': doc[0],
                        'filename': doc[1],
                        'metadata': doc[2],
                        'decade': doc[3],
                        'search_term': variation
                    }
                    results[main_term]['documents'].append(doc_data)
                    print(f"    • Doc ID {doc[0]}: {doc[1]}")
                    print(f"      Decade: {doc[3] or 'Unknown'}")
                    if doc[2] and variation.lower() in str(doc[2]).lower():
                        print(f"      Metadata contains term")
                    print()
        
        if not found_any:
            print(f"  ❌ No results found for '{main_term}' or any variations\n")
        
        print("=" * 80)
        print()
    
    conn.close()
    
    # Save results to JSON file
    with open('comprehensive_search_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Search results saved to 'comprehensive_search_results.json'")
    
    # Summary
    print("\n=== SUMMARY ===")
    for term in term_variations.keys():
        total_results = 0
        if term in results:
            total_results += len(results[term].get('events', []))
            total_results += len(results[term].get('nlp_results', []))
            total_results += len(results[term].get('documents', []))
        print(f"{term}: {total_results} total results")

if __name__ == "__main__":
    search_database()