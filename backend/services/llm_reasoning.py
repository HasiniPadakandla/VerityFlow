import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

class LLMReasoning:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_reasoning(self, message: str, verdict: str, confidence: float, red_flags: list) -> dict:
        """Generate human-readable reasoning using LLM"""
        
        system_message = """You are a security analyst helping users identify scam, fake news, and phishing messages.
Provide clear, educational explanations without legal or medical claims.
Be direct but not alarming. Focus on facts and safety."""
        
        user_prompt = f"""Analyze this WhatsApp message and explain why it's classified as "{verdict}" (confidence: {confidence:.2%}).

Message: "{message}"

Detected red flags: {', '.join(red_flags) if red_flags else 'None'}

Provide:
1. A brief 2-3 sentence explanation of why this is {verdict}
2. 2-3 specific reasons (bullet points)
3. One safety recommendation

Be concise, clear, and educational. Format your response as:
EXPLANATION: [your explanation]
REASONS:
- [reason 1]
- [reason 2]
- [reason 3]
SAFETY_ADVICE: [your advice]"""
        
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"verityflow-{hash(message)}",
                system_message=system_message
            ).with_model("openai", "gpt-5.2")
            
            user_message = UserMessage(text=user_prompt)
            response = await chat.send_message(user_message)
            
            explanation = ""
            reasons = []
            safety_advice = ""
            
            lines = response.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
                    current_section = 'explanation'
                elif line.startswith('REASONS:'):
                    current_section = 'reasons'
                elif line.startswith('SAFETY_ADVICE:'):
                    safety_advice = line.replace('SAFETY_ADVICE:', '').strip()
                    current_section = 'safety'
                elif line.startswith('- ') and current_section == 'reasons':
                    reasons.append(line[2:])
                elif current_section == 'explanation' and not line.startswith('REASONS:'):
                    explanation += ' ' + line
                elif current_section == 'safety' and line:
                    safety_advice += ' ' + line
            
            return {
                'explanation': explanation.strip(),
                'reasons': reasons,
                'safety_advice': safety_advice.strip()
            }
        
        except Exception as e:
            return {
                'explanation': f"This message is classified as {verdict} based on detected patterns.",
                'reasons': red_flags[:3] if red_flags else ["Pattern matching analysis"],
                'safety_advice': "Always verify unexpected messages before taking action. Never share personal or financial information."
            }
