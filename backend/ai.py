import logging
import google.generativeai as genai
from response_handler import HelixResponseHandler
from typing import List, Dict, Optional
import os
import re
from recruiting_graph import generate_email_sequence, EmailConfig

logger = logging.getLogger(__name__)

class RecruitingAI:
    def __init__(self, api_key: str, live_mode: bool = True):
        self.live_mode = live_mode
        genai.configure(api_key=api_key)
        self.response_handler = HelixResponseHandler()
        logging.info(f"Initialized RecruitingAI in {'live' if live_mode else 'mock'} mode")
        
    async def generate_response(self, message: str, messages: list, persona: str) -> str:
        """Generate a response based on the conversation context."""
        if not self.live_mode:
            return "Mock response in test mode"
            
        try:
            response = await self.response_handler.handle_response(
                message=message,
                history=messages,
                persona=persona
            )
            
            if response['type'] == 'error':
                return "I apologize, but I encountered an error. Please try again."
                
            return response['content']
            
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error. Please try again."
            
    def reset_conversation(self):
        """Reset the conversation state."""
        self.response_handler.reset()
        
    def generate_sequence(self, role: str, tone: str = "professional", step_count: int = 3, company_info: Optional[str] = None) -> List[Dict]:
        """Generate an email sequence using LangChain"""
        if not self.live_mode:
            return self._generate_mock_sequence(role)
            
        config = EmailConfig(
            role=role,
            tone=tone,
            step_count=step_count,
            company_info=company_info or "Not provided"
        )
        
        try:
            return generate_email_sequence(config)
        except Exception as e:
            logging.error(f"Error generating sequence: {str(e)}")
            return self._generate_mock_sequence(role)
            
    def _extract_role_info(self, message: str) -> Optional[str]:
        """Extract role information from the message using multiple strategies"""
        if not message:
            return None
            
        message_lower = message.lower()
        
        # Strategy 1: Direct role mention with common titles
        common_roles = [
            "engineer", "developer", "manager", "director", "vp", "lead",
            "architect", "designer", "product manager", "data scientist",
            "founding engineer", "senior engineer", "software engineer",
            "fullstack engineer", "frontend engineer", "backend engineer"
        ]
        
        for role in common_roles:
            pattern = fr'\b{role}\b'
            match = re.search(pattern, message_lower)
            if match:
                # Get the full role with any prefixes (e.g., "senior", "founding", etc.)
                start = max(0, match.start() - 20)  # Look back up to 20 chars
                prefix = message_lower[start:match.start()].strip()
                if prefix:
                    # Only include relevant prefixes
                    prefix_words = prefix.split()
                    relevant_prefixes = [word for word in prefix_words if word in ["senior", "founding", "lead", "principal"]]
                    if relevant_prefixes:
                        return f"{' '.join(relevant_prefixes)} {role}".title()
                return role.title()
        
        # Strategy 2: Role after keywords
        role_keywords = ["role", "position", "job", "candidate", "hiring", "recruiting for", "hire"]
        for keyword in role_keywords:
            if keyword in message_lower:
                start_idx = message_lower.find(keyword) + len(keyword)
                end_idx = message_lower.find(".", start_idx)
                if end_idx == -1:
                    end_idx = len(message_lower)
                
                role = message[start_idx:end_idx].strip()
                if role:
                    return role.strip("., ").title()
        
        # Strategy 3: Look for experience requirements
        exp_patterns = [
            r"(\d+)[\+]?\s*years?\s+(?:of\s+)?experience\s+(?:as\s+(?:a|an)\s+)?([^,.]+)",
            r"looking\s+for\s+(?:a|an)\s+([^,.]+)",
            r"hiring\s+(?:a|an)\s+([^,.]+)",
            r"need\s+(?:a|an)\s+([^,.]+)"
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, message_lower)
            if match:
                role = match.group(-1).strip()
                if any(tech in role for tech in common_roles):
                    return role.title()
        
        return None
        
    def _generate_mock_sequence(self, role: str) -> List[Dict]:
        """Generate a mock email sequence for testing"""
        return [
            {
                "subject": f"Exciting {role} Opportunity at Our Company",
                "body": f"""Hi there,

I hope this email finds you well. I came across your profile and was impressed by your experience in {role} roles.

Would you be interested in learning more about an exciting opportunity we have?

Best regards,
Recruiter"""
            },
            {
                "subject": f"Following up on {role} Position",
                "body": f"""Hi again,

I wanted to follow up on my previous email about the {role} position.

I'd love to schedule a brief call to discuss this opportunity in more detail.

Best regards,
Recruiter"""
            }
        ] 