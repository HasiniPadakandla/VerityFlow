import re
from typing import List, Dict, Tuple

class ScamRuleDetector:
    def __init__(self):
        self.urgency_keywords = [
            'act now', 'limited time', 'urgent', 'expires soon', 'hurry',
            'immediate action', 'don\'t miss', 'last chance', 'only today',
            'time sensitive', 'act immediately', 'respond now'
        ]
        
        self.lottery_keywords = [
            'congratulations', 'won', 'winner', 'prize', 'lottery',
            'lucky draw', 'claim', 'reward', 'million', 'cash prize',
            'selected winner', 'you have been chosen'
        ]
        
        self.otp_kyc_keywords = [
            'otp', 'one time password', 'verify account', 'kyc',
            'know your customer', 'update kyc', 'verify identity',
            'account verification', 'confirm identity', 'bank verification',
            'update bank details', 'debit card', 'credit card', 'cvv',
            'card number', 'expiry date', 'atm pin'
        ]
        
        self.financial_keywords = [
            'bank account', 'account number', 'ifsc', 'routing number',
            'wire transfer', 'payment pending', 'refund', 'tax refund',
            'unclaimed money', 'inheritance', 'covid relief'
        ]
        
        self.threat_keywords = [
            'suspended', 'blocked', 'deactivated', 'locked', 'arrested',
            'legal action', 'court', 'police', 'warrant', 'fine',
            'penalty', 'unauthorized access'
        ]

    def detect_suspicious_urls(self, text: str) -> List[str]:
        """Detect suspicious URLs and shortened links"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        suspicious_urls = []
        url_shorteners = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly']
        
        for url in urls:
            if any(shortener in url.lower() for shortener in url_shorteners):
                suspicious_urls.append(url)
            elif re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
                suspicious_urls.append(url)
        
        return suspicious_urls

    def check_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Check if any keywords are present in text"""
        text_lower = text.lower()
        found = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(keyword)
        return found

    def analyze(self, message: str) -> Dict:
        """Run rule-based analysis on the message"""
        red_flags = []
        risk_score = 0.0
        
        urgency = self.check_keywords(message, self.urgency_keywords)
        if urgency:
            red_flags.append(f"Urgency keywords detected: {', '.join(urgency[:3])}")
            risk_score += 0.2
        
        lottery = self.check_keywords(message, self.lottery_keywords)
        if lottery:
            red_flags.append(f"Lottery/Prize scam indicators: {', '.join(lottery[:3])}")
            risk_score += 0.3
        
        otp_kyc = self.check_keywords(message, self.otp_kyc_keywords)
        if otp_kyc:
            red_flags.append(f"OTP/KYC request detected: {', '.join(otp_kyc[:3])}")
            risk_score += 0.3
        
        financial = self.check_keywords(message, self.financial_keywords)
        if financial:
            red_flags.append(f"Financial information request: {', '.join(financial[:3])}")
            risk_score += 0.25
        
        threats = self.check_keywords(message, self.threat_keywords)
        if threats:
            red_flags.append(f"Threat/Fear tactics detected: {', '.join(threats[:3])}")
            risk_score += 0.2
        
        suspicious_urls = self.detect_suspicious_urls(message)
        if suspicious_urls:
            red_flags.append(f"Suspicious URLs found: {len(suspicious_urls)} link(s)")
            risk_score += 0.3
        
        has_excessive_caps = len(re.findall(r'[A-Z]{4,}', message)) > 2
        if has_excessive_caps:
            red_flags.append("Excessive use of capital letters")
            risk_score += 0.1
        
        has_excessive_punctuation = len(re.findall(r'[!]{2,}', message)) > 0
        if has_excessive_punctuation:
            red_flags.append("Excessive punctuation (multiple exclamation marks)")
            risk_score += 0.1
        
        risk_score = min(risk_score, 1.0)
        
        return {
            'red_flags': red_flags,
            'risk_score': risk_score,
            'suspicious_urls': suspicious_urls
        }
