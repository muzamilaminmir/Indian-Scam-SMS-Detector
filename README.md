# Indian Scam SMS & Call Detector

A robust, AI-powered MVP web application designed to detect and flag fraudulent SMS and call transcripts specifically tailored to the Indian context.



## Features

- **Hybrid Detection Engine**: Combines a Machine Learning model (>98% accuracy) with a heavily customized Rule-Based intent engine.
- **Intent-based OTP Protection**: Distinguishes between explicitly dangerous OTP requests vs. benign banking warnings ("Do not share OTP").
- **Transactional Safe Signals**: Dynamically lowers risk scores when genuine banking transaction formats (debited, credited, a/c) are detected.
- **Premium Glassmorphism UI**: A beautiful, dependency-free frontend utilizing vanilla HTML/CSS/JS with modern animations and glow effects.

## Project Architecture

- `backend/main.py`: The FastAPI application server serving the model and frontend.
- `backend/model.py`: Text preprocessing and Logistic Regression model inference.
- `backend/rules.py`: Our mathematical weighted-scoring rules engine designed to flag Indian phishing patterns and safe signals.
- `backend/train.py`: The script to train the `TfidfVectorizer` and `LogisticRegression` on our dataset.
- `frontend/`: Contains the sleek, responsive UI.

## Tech Stack

- **Backend**: Python 3, FastAPI, Uvicorn
- **Machine Learning**: Scikit-Learn (Logistic Regression, TF-IDF Vectorizer), Pandas
- **Frontend**: Vanilla HTML5, CSS3, ES6 JavaScript

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <repository-folder>
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the initial model:**
   Navigate into the `backend` directory and run the training script:
   ```bash
   cd backend
   python train.py
   ```
   *This will generate `logreg_model.pkl` and `tfidf_vectorizer.pkl`.*

4. **Run the API server:**
   Start the FastAPI server via Uvicorn:
   ```bash
   python -m uvicorn main:app --reload
   ```

5. **Test the Application:**
   Open your web browser and go to:
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Usage Examples

Paste a variety of messages to see the engine adapt:

- **Dangerous**: "URGENT: SBI KYC suspended. Share OTP immediately or face legal action."
- **Suspicious**: "Click here to claim your Rs 5000 reward."
- **Safe**: "Rs 500 debited from a/c 1234. Do not share your OTP with anyone."

## Credits
**Built by [Muzamil Mir](https://github.com/muzamilaminmir)**.

## Contributing
Feel free to open an issue or submit a pull request if you'd like to extend the functionality or include more sophisticated ML NLP transformers!
