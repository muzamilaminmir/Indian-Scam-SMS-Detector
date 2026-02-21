import pickle
import string
import os

MODEL_FILE = os.path.join(os.path.dirname(__file__), "logreg_model.pkl")
VECTORIZER_FILE = os.path.join(os.path.dirname(__file__), "tfidf_vectorizer.pkl")

def preprocess_text(text: str) -> str:
    # 1. Lowercase normalization
    text = text.lower()
    
    # 2. Remove punctuation but keep numbers and text
    # string.punctuation is !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    return text

def load_model():
    if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
        with open(VECTORIZER_FILE, 'rb') as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    return None, None

def predict_message(text: str):
    model, vectorizer = load_model()
    if not model or not vectorizer:
        return 0.0 # Return 0 if model is not trained yet
    
    cleaned_text = preprocess_text(text)
    
    # Vectorize
    X = vectorizer.transform([cleaned_text])
    
    # Predict probabilities
    prob = model.predict_proba(X)[0]
    classes = model.classes_
    
    # Find the probability of 'scam'
    scam_idx = list(classes).index('scam') if 'scam' in classes else 1
    scam_prob = prob[scam_idx]
    
    return float(scam_prob)
