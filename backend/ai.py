import google.generativeai as genai
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecruitingAI:
    def __init__(self, api_key: str):
        self.use_mock = api_key == "PLACEHOLDER_KEY"
        if self.use_mock:
            logger.warning("Using mock responses since no valid API key was provided")
        else:
            try:
                if not api_key:
                    raise ValueError("API key is missing")
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Successfully initialized Gemini model")
            except Exception as e:
                logger.error(f"Error initializing Gemini: {str(e)}")
                self.use_mock = True
                logger.warning("Falling back to mock responses")

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response based on the conversation history."""
        if self.use_mock:
            return self._generate_mock_response(messages)
            
        try:
            if not messages:
                return "Hello! I'm your HR recruiting assistant. How can I help you today?"

            # Convert messages to Gemini format
            prompt = "You are an expert HR recruiting assistant. Respond to the following conversation:\n\n"
            for msg in messages:
                role = "Human" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n\n"
            
            logger.info(f"Generating response for prompt length: {len(prompt)}")
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    candidate_count=1,
                    max_output_tokens=1000,
                )
            )
            
            if not response.text:
                logger.warning("Empty response received from Gemini")
                return "I apologize, but I received an empty response. Please try again."
                
            logger.info(f"Successfully generated response of length: {len(response.text)}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def generate_sequence(self, role_info: Dict[str, Any]) -> str:
        """Generate a complete recruiting sequence based on role information."""
        if self.use_mock:
            return self._generate_mock_sequence(role_info)
            
        try:
            prompt = f"""Create a recruiting outreach sequence for the following role:
            Role: {role_info.get('role', 'Not specified')}
            Target Audience: {role_info.get('target_audience', 'Not specified')}
            Key Requirements: {role_info.get('requirements', 'Not specified')}
            Company Culture: {role_info.get('company_culture', 'Not specified')}
            
            Please create a sequence that includes:
            1. Initial outreach message
            2. Follow-up message (if no response)
            3. Final message (if still no response)
            
            Format the output in markdown with clear sections and professional tone."""
            
            logger.info(f"Generating sequence for role: {role_info.get('role', 'Not specified')}")
            
            # Generate sequence
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    candidate_count=1,
                    max_output_tokens=1500,
                )
            )
            
            if not response.text:
                logger.warning("Empty sequence received from Gemini")
                return "I apologize, but I received an empty response. Please try again."
                
            logger.info(f"Successfully generated sequence of length: {len(response.text)}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
            
    def _generate_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a mock response for testing."""
        if not messages:
            return "Hello! I'm your HR recruiting assistant. How can I help you today?"
            
        last_message = messages[-1]["content"].lower()
        
        if "hello" in last_message or "hi" in last_message:
            return "Hi there! I'm your recruiting assistant. I can help you create personalized outreach sequences for your job openings. What role are you recruiting for?"
            
        if "role" in last_message or "position" in last_message or "job" in last_message:
            return "Great! Could you tell me more about the target audience for this role? What kind of candidates are you looking to attract?"
            
        if "candidate" in last_message or "audience" in last_message:
            return "That's helpful. What are the key requirements or skills needed for this position?"
            
        if "requirement" in last_message or "skill" in last_message:
            return "Excellent. One last question - how would you describe your company culture? This will help me craft messages that reflect your organization's values."
            
        if "culture" in last_message or "company" in last_message:
            return "Thank you for providing all this information! I've created a recruiting sequence based on what you've shared. You can view and edit it in the workspace panel."
            
        return "I understand. Is there anything specific about the recruiting sequence you'd like me to modify or explain?"
        
    def _generate_mock_sequence(self, role_info: Dict[str, Any]) -> str:
        """Generate a mock sequence for testing."""
        role = role_info.get('role', 'the position')
        
        return """# Recruiting Outreach Sequence

## Initial Outreach

**Subject:** Exciting Opportunity at Our Company

Dear [Candidate Name],

I hope this message finds you well. I came across your profile and was impressed by your background in [relevant field]. We're currently looking for a talented professional to join our team as a **{role}**, and I believe your experience could be a great fit.

Our company offers [brief value proposition] and a culture that [company culture highlight].

Would you be interested in learning more about this opportunity? I'd be happy to share additional details or schedule a brief call at your convenience.

Best regards,
[Your Name]

## Follow-up (5 days later)

**Subject:** Re: Exciting Opportunity at Our Company

Hello [Candidate Name],

I wanted to follow up on my previous message regarding the **{role}** position at our company. 

The role offers [key benefit/opportunity], and we're looking for someone with your expertise in [relevant skill].

If you're interested, I'd love to hear back from you. If now isn't the right time, I completely understand.

Warm regards,
[Your Name]

## Final Outreach (7 days after follow-up)

**Subject:** One Last Note About Our Opportunity

Hi [Candidate Name],

I'm reaching out one final time regarding our **{role}** position. 

Our team is moving forward with interviews, and I wanted to ensure you had the chance to be considered if you're interested.

Feel free to reach out if you'd like to discuss this opportunity now or in the future.

All the best,
[Your Name]
""".format(role=role) 