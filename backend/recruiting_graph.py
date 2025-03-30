from typing import Dict, List, TypedDict
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the model globally
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# List available models
try:
    for m in genai.list_models():
        print(f"Available model: {m.name}")
except Exception as e:
    print(f"Error listing models: {str(e)}")

class EmailConfig(TypedDict):
    role: str
    tone: str
    company_info: str
    step_count: int

def generate_email_sequence(config: EmailConfig) -> List[Dict[str, str]]:
    """
    Generate a sequence of recruiting emails using Google's Generative AI.
    
    Args:
        config: EmailConfig containing role, tone, company info, and step count
        
    Returns:
        List of dictionaries containing email subjects and bodies
    """
    try:
        # Initialize the model with safety settings
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        # Normalize tone and step count
        tone = config["tone"].lower()
        step_count = min(max(1, config["step_count"]), 5)
        
        # Create the prompt
        prompt = f"""You are a professional recruiter. Create {step_count} recruiting emails for a {config['role']} position.
        Use this tone: {tone}
        Company Info: {config.get('company_info', 'A growing technology company')}
        
        Format your response as a JSON array of objects, where each object has 'subject' and 'body' fields.
        Make each email professional and engaging, with increasing urgency in follow-ups.
        
        Example format:
        [
            {{"subject": "Exciting opportunity for [Role]", "body": "Email content here..."}},
            {{"subject": "Following up - [Role] position", "body": "Follow up content here..."}}
        ]
        """
        
        # Generate the sequence
        response = model.generate_content(prompt)
        
        if response.text:
            try:
                # Try to parse the response as JSON
                sequence = json.loads(response.text)
                if isinstance(sequence, list) and len(sequence) > 0:
                    return sequence
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the text
                start_idx = response.text.find('[')
                end_idx = response.text.rfind(']') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response.text[start_idx:end_idx]
                    try:
                        sequence = json.loads(json_str)
                        if isinstance(sequence, list) and len(sequence) > 0:
                            return sequence
                    except:
                        pass
        
        # If all parsing attempts fail, return a fallback response
        return [
            {
                "subject": f"Exciting {config['role']} Opportunity",
                "body": f"We are looking for a talented {config['role']}. Would you be interested in learning more about this opportunity?"
            }
        ]
        
    except Exception as e:
        print(f"Error generating sequence: {str(e)}")
        return [
            {
                "subject": f"Exciting {config['role']} Opportunity",
                "body": f"We are looking for a talented {config['role']}. Would you be interested in learning more about this opportunity?"
            }
        ]

def run_graph(config: EmailConfig) -> List[Dict]:
    """Run the email sequence generation graph"""
    return generate_email_sequence(config) 