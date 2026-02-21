import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import pickle
import os

from model import preprocess_text, MODEL_FILE, VECTORIZER_FILE

def train():
    current_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(current_dir, "dataset.csv")
    
    print(f"Loading dataset from {dataset_path}...")
    try:
        df1 = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print("Error: dataset.csv not found!")
        return
        
    external_data = os.path.join(current_dir, "../data/spam.csv")
    if os.path.exists(external_data):
        print(f"Found external dataset at {external_data}! Merging...")
        df2 = pd.read_csv(external_data, encoding='latin-1')
        df2 = df2[['v1', 'v2']].rename(columns={'v1': 'label', 'v2': 'text'})
        df2['label'] = df2['label'].map({'ham': 'safe', 'spam': 'scam'})
        df = pd.concat([df1, df2], ignore_index=True)
    else:
        df = df1
        
    print(f"Total samples after merge: {len(df)}")
    print("Preprocessing text...")
    df['cleaned_text'] = df['text'].apply(preprocess_text)
    
    # We will use bi-grams and tri-grams to capture phrases like "account blocked", "pay now"
    print("Training TF-IDF Vectorizer (with n-grams)...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=3000)
    X = vectorizer.fit_transform(df['cleaned_text'])
    y = df['label']
    
    print("Training Logistic Regression Model...")
    # C=1.5 to reduce regularization slightly to fit the data better, class_weight='balanced'
    model = LogisticRegression(C=1.5, class_weight='balanced', random_state=42)
    
    # Check Accuracy internally using 5-fold Cross-Validation
    scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    mean_accuracy = scores.mean() * 100
    print(f"✅ Cross-Validation Accuracy: {mean_accuracy:.2f}%")
    
    if mean_accuracy < 90.0:
        print("⚠️ Warning: Model accuracy is below 90%!")
        
    # Fit the final model on all data
    model.fit(X, y)
    
    print("Saving model artifacts...")
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)
    with open(VECTORIZER_FILE, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    print("Training complete! Model successfully saved with high accuracy.")

if __name__ == "__main__":
    train()
