import pickle
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np

class MLClassifier:
    def __init__(self):
        self.model = None
        self.classes = ['legitimate', 'scam', 'fake_news', 'phishing']
        self.model_path = Path(__file__).parent / 'trained_model.pkl'
        
        if self.model_path.exists():
            self._load_model()
        else:
            self._train_model()
    
    def _train_model(self):
        """Train a simple model with synthetic data"""
        training_data = [
            ("Hey, are we still meeting for lunch tomorrow?", "legitimate"),
            ("Thanks for your help with the project yesterday", "legitimate"),
            ("Can you send me the report by end of day?", "legitimate"),
            ("Happy birthday! Hope you have a great day", "legitimate"),
            ("Meeting rescheduled to 3 PM. See you then", "legitimate"),
            ("CONGRATULATIONS! You have WON $1,000,000 in our lottery! Click here to CLAIM NOW!", "scam"),
            ("URGENT: Your bank account will be SUSPENDED. Verify your details immediately at bit.ly/xyz", "scam"),
            ("You have been selected as a LUCKY WINNER! Act now to claim your prize money!", "scam"),
            ("FINAL NOTICE: Pay Rs.50,000 or face legal action. Call immediately!", "scam"),
            ("Claim your tax refund of $5000 now! Limited time offer. Send your bank details", "scam"),
            ("Your ATM card has been blocked. Share your CVV and PIN to reactivate", "phishing"),
            ("Update your KYC details: Click here and enter your OTP, password and card number", "phishing"),
            ("Verify your identity: www.bankscam123.com - Enter your full bank account details", "phishing"),
            ("Security Alert: Suspicious activity detected. Confirm your password at http://192.168.1.1/secure", "phishing"),
            ("Your package is held. Pay customs fee and provide card details: tinyurl.com/xyz", "phishing"),
            ("BREAKING: Government announces free money for everyone! Share this message!", "fake_news"),
            ("Scientists confirm drinking 10 liters of water daily cures all diseases!", "fake_news"),
            ("SHOCKING: Famous celebrity died in accident! Click to see photos!", "fake_news"),
            ("New miracle cure discovered! Big pharma doesn't want you to know!", "fake_news"),
            ("ALERT: 5G towers spreading virus! Share to save lives!", "fake_news"),
            ("Good morning! Have a wonderful day ahead", "legitimate"),
            ("Reminder: Doctor's appointment at 10 AM tomorrow", "legitimate"),
            ("Can you pick up groceries on your way home?", "legitimate"),
            ("Congratulations on your promotion! Well deserved", "legitimate"),
            ("Movie night this Friday? Let me know if you're free", "legitimate"),
        ]
        
        texts = [text for text, _ in training_data]
        labels = [label for _, label in training_data]
        
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
            ('clf', LogisticRegression(max_iter=1000, random_state=42))
        ])
        
        self.model.fit(texts, labels)
        
        self._save_model()
    
    def _save_model(self):
        """Save trained model to disk"""
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
    
    def _load_model(self):
        """Load trained model from disk"""
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
    
    def predict(self, message: str):
        """Predict class and probability for a message"""
        prediction = self.model.predict([message])[0]
        probabilities = self.model.predict_proba([message])[0]
        
        class_probabilities = dict(zip(self.model.classes_, probabilities))
        confidence = max(probabilities)
        
        return {
            'predicted_class': prediction,
            'confidence': float(confidence),
            'class_probabilities': {k: float(v) for k, v in class_probabilities.items()}
        }
