import os
import logging
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class HelixResponseHandler:
    def __init__(self, model_name: str = "models/gemini-1.5-flash"):
        # Initialize Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(model_name)
        self.turn_count = 0
        self.conversation_history = []
        self.required_info = {
            'role': False,
            'company': False,
            'requirements': False,
            'unique_value': False
        }
        self.MAX_TURNS_BEFORE_EMAIL = 3
        
        # Define persona introductions
        self.persona_intros = {
            'corporate_pro': {
                'intro': "I'm your Corporate Professional Recruiting Assistant. I help create formal, structured outreach sequences that reflect corporate excellence. I'll guide you through gathering information about the role, company, and requirements to craft compelling recruiting messages.",
                'style': 'professional and structured'
            },
            'startup_founder': {
                'intro': "I'm your Startup Founder Recruiting Assistant. I bring startup energy and vision to help you craft engaging outreach sequences. I'll help you highlight growth opportunities and innovative challenges to attract top talent.",
                'style': 'direct and passionate'
            },
            'friendly_recruiter': {
                'intro': "I'm your Friendly Recruiting Assistant. I help create warm, personalized messages that build genuine connections with candidates. I'll guide you through crafting welcoming outreach sequences that resonate with potential hires.",
                'style': 'warm and personable'
            },
            'tech_expert': {
                'intro': "I'm your Technical Recruiting Assistant. I specialize in crafting detailed, technical outreach sequences that speak the language of developers. I'll help you highlight technical challenges and engineering opportunities to attract top tech talent.",
                'style': 'technical and detailed'
            }
        }

    def get_persona_intro(self, persona: str) -> str:
        """Get the introduction message for the selected persona."""
        logging.info(f"Getting persona introduction for {persona}")
        persona_data = self.persona_intros.get(persona, self.persona_intros['corporate_pro'])
        intro = persona_data['intro']
        logging.info(f"Generated intro message: {intro}")
        return intro

    def load_prompt(self, prompt_file: str, context: Dict) -> str:
        """Load and format a prompt template."""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', prompt_file)
            logging.info(f"Loading prompt from: {prompt_path}")
            
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            # Replace template variables with context
            for key, value in context.items():
                prompt_template = prompt_template.replace('{{' + key + '}}', str(value))
            
            logging.info(f"Formatted prompt: {prompt_template}")
            return prompt_template
        except Exception as e:
            logging.error(f"Error loading prompt: {str(e)}")
            # Return a default prompt if template loading fails
            if 'persona' in context:
                return f"You are a {context['persona']}. Please ask the next relevant question about the role, company, or requirements."
            return "What role are you looking to hire for? Please provide the title and level."
        
    def format_history(self, messages: List[Dict]) -> str:
        """Format conversation history for prompt context."""
        history = []
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            history.append(f"{role}: {msg['content']}")
        return "\n".join(history)
        
    def get_next_question(self) -> str:
        """Determine the next question to ask based on missing information."""
        logging.info(f"Current required info status: {self.required_info}")
        
        if not self.required_info['role']:
            return "What role are you looking to hire for? Please provide the title and level."
        elif not self.required_info['company']:
            return "Could you tell me about your company and what you're building?"
        elif not self.required_info['requirements']:
            return "What are the key requirements and qualifications for this role?"
        elif not self.required_info['unique_value']:
            return "What makes this opportunity unique or exciting for candidates?"
        return None
        
    def update_required_info(self, message: str):
        """Update which information we've gathered from the conversation."""
        message_lower = message.lower()
        
        # Role keywords
        role_keywords = ['engineer', 'developer', 'manager', 'director', 'lead', 'architect', 'designer', 'analyst', 'consultant']
        if any(word in message_lower for word in role_keywords):
            self.required_info['role'] = True
            logging.info("Role information detected")
            
        # Company keywords
        company_keywords = ['company', 'startup', 'business', 'organization', 'firm', 'enterprise', 'mission', 'vision']
        if any(word in message_lower for word in company_keywords):
            self.required_info['company'] = True
            logging.info("Company information detected")
            
        # Requirements keywords
        requirements_keywords = ['requirements', 'experience', 'skills', 'qualifications', 'needs', 'looking for', 'must have', 'should have']
        if any(word in message_lower for word in requirements_keywords):
            self.required_info['requirements'] = True
            logging.info("Requirements information detected")
            
        # Unique value proposition keywords
        value_keywords = ['unique', 'exciting', 'challenging', 'innovative', 'cutting-edge', 'latest', 'new', 'different']
        if any(word in message_lower for word in value_keywords):
            self.required_info['unique_value'] = True
            logging.info("Unique value proposition detected")
            
        logging.info(f"Updated required info status: {self.required_info}")
        
    def should_generate_sequence(self) -> bool:
        """Check if we have enough information to generate a sequence."""
        has_all_info = all(self.required_info.values())
        logging.info(f"Required info status: {self.required_info}")
        return has_all_info
        
    async def generate_email_sequence(self, messages: List[Dict], persona: str) -> str:
        """Generate the email sequence based on collected information."""
        try:
            prompt = self.load_prompt('generate_email_prompt.txt', {
                'persona': persona,
                'history': self.format_history(messages)
            })
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error generating sequence: {str(e)}")
            return "Error generating sequence. Please try again."
            
    def should_generate_email(self) -> bool:
        """Determine if we should switch to email generation."""
        # Check if we have enough context to generate an email
        has_role = False
        has_requirements = False
        has_company_info = False
        
        for msg in self.conversation_history:
            content = msg.get('content', '').lower()
            if any(keyword in content for keyword in ['engineer', 'developer', 'manager', 'director']):
                has_role = True
            if any(keyword in content for keyword in ['requirements', 'experience', 'skills']):
                has_requirements = True
            if any(keyword in content for keyword in ['company', 'startup', 'mission', 'product']):
                has_company_info = True
                
        return has_role and (has_requirements or has_company_info)
        
    async def handle_response(self, 
                            message: str, 
                            history: List[Dict], 
                            persona: str) -> Dict:
        """Main response handling logic."""
        self.turn_count += 1
        self.conversation_history = history
        
        try:
            if self.should_generate_email():
                # Switch to email generation
                prompt = self.load_prompt('generate_email_prompt.txt', {
                    'persona': persona,
                    'answers': self.format_history(history)
                })
                response = await self.model.generate_content(prompt)
                return {
                    'type': 'email',
                    'content': response.text,
                    'turn_count': self.turn_count
                }
            else:
                # Continue with questioning
                prompt = self.load_prompt('persona_questioning_prompt.txt', {
                    'persona': persona,
                    'history': self.format_history(history)
                })
                response = await self.model.generate_content(prompt)
                return {
                    'type': 'question',
                    'content': response.text,
                    'turn_count': self.turn_count
                }
                
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                'type': 'error',
                'content': f"Error generating response: {str(e)}",
                'turn_count': self.turn_count
            }
            
    def reset(self):
        """Reset the conversation state."""
        self.turn_count = 0
        self.conversation_history = []
        self.required_info = {key: False for key in self.required_info}
        
    async def edit_sequence(self, sequence: str, instruction: str) -> str:
        """Edit the email sequence based on the given instruction."""
        try:
            prompt = self.load_prompt('edit_sequence_prompt.txt', {
                'sequence': sequence,
                'instruction': instruction
            })
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error editing sequence: {str(e)}")
            return f"Error editing sequence: {str(e)}"

    async def generate_response(self, message: str, history: List[Dict], persona: str) -> str:
        """Generate the next response or question in the conversation."""
        self.conversation_history = history
        
        # If this is the first message, return the persona introduction
        if not history or len(history) == 1:
            logging.info(f"Generating persona introduction for {persona}")
            return self.get_persona_intro(persona)
            
        # Update required info from the latest message
        self.update_required_info(message)
        
        # Get next question based on missing information
        next_question = self.get_next_question()
        if next_question:
            logging.info(f"Generating next question: {next_question}")
            return next_question
        
        # If we have all required info, acknowledge and prepare for sequence generation
        logging.info("All required information gathered, preparing for sequence generation")
        return "Thank you for providing all the details. I'll help you generate an engaging email sequence for this role." 