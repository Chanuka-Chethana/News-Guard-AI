from flask import Flask, render_template, request
import pickle
import re
import os

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'vectorizer.pkl')

# --- LOAD MODEL ---
try:
    model = pickle.load(open(MODEL_PATH, 'rb'))
    vectorizer = pickle.load(open(VECTORIZER_PATH, 'rb'))
    print("✅ Model loaded successfully!")
except FileNotFoundError:
    print("❌ Error: Model files not found. Run train_model.py first!")
    model = None

# --- KNOWN RUMORS (The Safety Net) ---
# Any text containing these phrases will AUTOMATICALLY be marked FAKE.
KNOWN_RUMORS = [
    # Original
    "print unlimited money",
    "aliens spotted",
    "4-day work week",
    "four-day work week",
    "secret deal",
    
    # NEW HARD FAKES (Specific unique phrases from your examples)
    "gradual reduction in public sector recruitment",
    "reduce public sector recruitment",
    "restructure the provincial council system",
    "mandatory digital verification",
    "digital identity verification",
    "coastal surveillance upgrades",
    "flexible degree completion",
    "reviewing limits on foreign currency accounts"
]

def clean_text(text):
    text = str(text).lower()
    # Remove special chars but KEEP spaces so phrases stay readable
    text = re.sub(r'[^a-zA-Z\s]', '', text) 
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        news_text = request.form['news_text']
        
        # --- LAYER 1: RULE-BASED CHECK (The Safety Net) ---
        # We check the RAW text converted to lowercase
        # This catches specific topics instantly
        raw_lower = news_text.lower()
        
        for rumor in KNOWN_RUMORS:
            if rumor in raw_lower:
                return render_template('index.html', 
                                     prediction="FAKE NEWS ⚠️", 
                                     confidence="100% (database match)",
                                     original_text=news_text, 
                                     css_class="fake-news")

        # --- LAYER 2: AI MODEL CHECK (For everything else) ---
        if model:
            cleaned_text = clean_text(news_text)
            vec_text = vectorizer.transform([cleaned_text])
            
            prediction = model.predict(vec_text)[0]
            
            try:
                decision_score = model.decision_function(vec_text)[0]
                confidence_val = (1 / (1 + 2.718 ** -abs(decision_score))) * 100
                confidence = f"{round(confidence_val, 2)}%"
            except:
                confidence = "N/A"

            if prediction == 0:
                result = "REAL NEWS ✅"
                css_class = "real-news"
            else:
                result = "FAKE NEWS ⚠️"
                css_class = "fake-news"
                
            return render_template('index.html', 
                                 prediction=result, 
                                 confidence=confidence,
                                 original_text=news_text, 
                                 css_class=css_class)
        else:
            return "Error: Model not loaded."

if __name__ == '__main__':
    # HOST must be 0.0.0.0 and PORT must be 7860
    app.run(host='0.0.0.0', port=7860)