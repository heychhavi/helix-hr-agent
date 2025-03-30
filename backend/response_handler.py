import os
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

class HelixResponseHandler:
    def __init__(self, model_name: str = "models/gemini-1.5-flash"):
        # Initialize Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(model_name)
        self.turn_count = 0
        self.conversation_history = []
        self.required_info = {
            'role': None,
            'company': None,
            'requirements': None,
            'unique_value': None
        }
        self.MAX_TURNS_BEFORE_EMAIL = 3
        
        # Define persona introductions and questions
        self.persona_data = {
            'corporate_pro': {
                'intro': "I'm your professional recruiting assistant. I'll help you craft a polished and impactful email sequence that reflects your company's corporate standards.",
                'style': 'formal and professional',
                'questions': {
                    'role': "Could you describe the role you're hiring for, including the level and key responsibilities?",
                    'company': "What are the key business objectives and market position of your company?",
                    'requirements': "What are the essential qualifications and experience requirements for this position?",
                    'unique_value': "What sets your company apart in terms of professional development and career advancement opportunities?"
                }
            },
            'startup_founder': {
                'intro': "Hey! I'm here to help you create an energetic and compelling email sequence that captures your startup's mission and potential.",
                'style': 'enthusiastic and mission-driven',
                'questions': {
                    'role': "What's the exciting role you're looking to fill in your startup?",
                    'company': "Tell me about your startup's mission and the problem you're solving!",
                    'requirements': "What kind of talented individuals are you looking for to join your journey?",
                    'unique_value': "What makes your startup a unique and exciting place to work?"
                }
            },
            'friendly_recruiter': {
                'intro': "Hi there! I'm your friendly recruiting partner, ready to help you create warm and engaging emails that connect with candidates.",
                'style': 'warm and personable',
                'questions': {
                    'role': "Can you tell me about the role you're looking to fill and the team they'll be joining?",
                    'company': "What makes your company culture special and welcoming?",
                    'requirements': "What qualities and experience would make someone a great fit for your team?",
                    'unique_value': "How does your company support work-life balance and employee well-being?"
                }
            },
            'tech_expert': {
                'intro': "I'm your technical recruiting specialist. Let's create detailed and tech-focused emails that resonate with engineering candidates.",
                'style': 'technical and detailed',
                'questions': {
                    'role': "What technical role are you hiring for, and what tech stack will they be working with?",
                    'company': "What interesting technical challenges is your engineering team tackling?",
                    'requirements': "What specific technical skills and experience are you looking for?",
                    'unique_value': "What makes your engineering culture and technical environment unique?"
                }
            }
        }
        self.current_question_type = None

    def get_persona_intro(self, persona: str) -> str:
        """Get the introduction message for the selected persona."""
        logging.info(f"Getting persona introduction for {persona}")
        persona_data = self.persona_data.get(persona, self.persona_data['corporate_pro'])
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
        
    def get_next_question(self, persona: str) -> Optional[str]:
        persona_questions = self.persona_data.get(persona, self.persona_data['corporate_pro'])['questions']
        
        # Find the first missing information and ask corresponding question
        for info_type, value in self.required_info.items():
            if not value and info_type in persona_questions:
                self.current_question_type = info_type
                return persona_questions[info_type]
        
        return None
        
    def update_required_info(self, message: str):
        """Update which information we've gathered from the conversation."""
        message_lower = message.lower()
        
        # Role keywords
        role_keywords = ['engineer', 'developer', 'manager', 'director', 'lead', 'architect', 'designer', 'analyst', 'consultant']
        if any(word in message_lower for word in role_keywords):
            self.required_info['role'] = message
            logging.info("Role information detected")
            
        # Company keywords
        company_keywords = ['company', 'startup', 'business', 'organization', 'firm', 'enterprise', 'mission', 'vision']
        if any(word in message_lower for word in company_keywords):
            self.required_info['company'] = message
            logging.info("Company information detected")
            
        # Requirements keywords
        requirements_keywords = ['requirements', 'experience', 'skills', 'qualifications', 'needs', 'looking for', 'must have', 'should have']
        if any(word in message_lower for word in requirements_keywords):
            self.required_info['requirements'] = message
            logging.info("Requirements information detected")
            
        # Unique value proposition keywords
        value_keywords = ['unique', 'exciting', 'challenging', 'innovative', 'cutting-edge', 'latest', 'new', 'different']
        if any(word in message_lower for word in value_keywords):
            self.required_info['unique_value'] = message
            logging.info("Unique value proposition detected")
            
        logging.info(f"Updated required info status: {self.required_info}")
        
    def should_generate_sequence(self) -> bool:
        """Check if we have enough information to generate a sequence."""
        return all(value is not None for value in self.required_info.values())
        
    def generate_email_sequence(self, messages: List[Dict], persona: str, company_context: Optional[Dict] = None) -> str:
        """Generate the email sequence based on collected information."""
        try:
            # Extract key information from conversation
            role_info = ""
            company_info = ""
            requirements = ""
            unique_value = ""
            
            for msg in messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '').lower()
                    if any(keyword in content for keyword in ['engineer', 'developer', 'manager', 'director']):
                        role_info = msg.get('content')
                    if any(keyword in content for keyword in ['company', 'startup', 'mission', 'product']):
                        company_info = msg.get('content')
                    if any(keyword in content for keyword in ['requirements', 'experience', 'skills']):
                        requirements = msg.get('content')
                    if any(keyword in content for keyword in ['unique', 'exciting', 'opportunity']):
                        unique_value = msg.get('content')

            # Get persona style
            persona_style = self.persona_data.get(persona, self.persona_data['corporate_pro'])['style']
            
            # Create context for the prompt
            context = {
                'persona': persona,
                'style': persona_style,
                'role_info': role_info,
                'company_info': company_info,
                'requirements': requirements,
                'unique_value': unique_value,
                'history': self.format_history(messages)
            }
            
            # Add company context if available
            if company_context:
                context.update({
                    'company_name': company_context.get('name'),
                    'industry': company_context.get('industry'),
                    'company_size': company_context.get('size'),
                    'company_description': company_context.get('description'),
                    'website': company_context.get('website')
                })
            
            prompt = self.load_prompt('generate_email_prompt.txt', context)
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
        
    def generate_response(self, messages: List[Dict], persona: str, company_context: Optional[Dict] = None) -> str:
        """Generate the next response or question in the conversation."""
        self.conversation_history = messages
        
        # If this is the first message, return the persona introduction
        if not messages or len(messages) == 1:
            logging.info(f"Generating persona introduction for {persona}")
            return self.get_persona_intro(persona)
            
        # Update required info from the latest message
        self.update_required_info(messages[-1]['content'])
        
        # Get next question based on missing information
        next_question = self.get_next_question(persona)
        if next_question:
            logging.info(f"Generating next question: {next_question}")
            return next_question
        
        # If we have all required info, acknowledge and prepare for sequence generation
        logging.info("All required information gathered, preparing for sequence generation")
        return "Thank you for providing all the details. I'll help you generate an engaging email sequence for this role."

    def reset(self):
        """Reset the conversation state."""
        self.turn_count = 0
        self.conversation_history = []
        self.required_info = {key: None for key in self.required_info}
        
    def edit_sequence(self, sequence: str, instruction: str) -> str:
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

    def handle_sequence_feedback(self, feedback: str) -> str:
        """Handle feedback on the generated sequence and provide appropriate responses."""
        feedback_lower = feedback.lower()
        
        # Detect the type of feedback
        if any(word in feedback_lower for word in ['technical', 'tech', 'stack', 'framework']):
            return "I'll enhance the technical details. Would you like me to focus on specific technologies or technical challenges?"
            
        elif any(word in feedback_lower for word in ['specific', 'example', 'concrete']):
            return "I'll add more specific examples. Should I focus on project examples, technical achievements, or both?"
            
        elif any(word in feedback_lower for word in ['tone', 'formal', 'casual', 'friendly']):
            return "I can adjust the tone. Would you prefer it to be more formal and professional, or more casual and conversational?"
            
        elif any(word in feedback_lower for word in ['concise', 'shorter', 'brief']):
            return "I'll make it more concise. Would you like me to focus on shortening specific emails or the entire sequence?"
            
        elif any(word in feedback_lower for word in ['personal', 'personalize', 'customize']):
            return "I'll add more personalization. Should I focus on personalizing based on the candidate's background, skills, or potential impact?"
            
        elif any(word in feedback_lower for word in ['good', 'great', 'perfect', 'works']):
            return "I'm glad you like the sequence! Feel free to use the magic actions to download it or make any final tweaks."
            
        else:
            return "I'd be happy to improve the sequence. Could you specify what aspects you'd like me to focus on? For example:\n1. Technical details\n2. Specific examples\n3. Tone adjustment\n4. Length/conciseness\n5. Personalization"

    def enhance_personalization(self, sequence: str, company_context: Optional[Dict] = None) -> str:
        """Enhance the personalization of the email sequence using conversation context."""
        try:
            # Create context for enhancement
            context = {
                'sequence': sequence
            }

            # Add company context if available
            if company_context:
                context.update({
                    'company_name': company_context.get('name'),
                    'industry': company_context.get('industry'),
                    'company_size': company_context.get('size'),
                    'company_description': company_context.get('description'),
                    'website': company_context.get('website')
                })

            prompt = self.load_prompt('enhance_personalization_prompt.txt', context)
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error enhancing personalization: {str(e)}")
            return sequence  # Return original sequence if enhancement fails 