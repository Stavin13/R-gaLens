from transformers import pipeline
import spacy
import os

def download_models():
    print("Pre-downloading NLP models...")
    
    # List of models to cache
    models = [
        ("ner", "dslim/bert-base-NER"),
        ("zero-shot-classification", "facebook/bart-large-mnli"),
        ("summarization", "facebook/bart-large-cnn")
    ]
    
    for task, model_name in models:
        print(f"Downloading {model_name} for {task}...")
        pipeline(task, model=model_name)
    
    print("Downloading SpaCy model...")
    os.system("python -m spacy download en_core_web_sm")
    
    print("All models downloaded successfully.")

if __name__ == "__main__":
    download_models()
