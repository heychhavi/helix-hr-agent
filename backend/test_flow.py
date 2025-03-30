import asyncio
from response_handler import HelixResponseHandler
import logging

logging.basicConfig(level=logging.INFO)

async def test_conversation_flow():
    # Initialize the response handler
    handler = HelixResponseHandler()
    messages = []
    persona = "startup_founder"
    
    logging.info("Starting conversation flow test...")
    
    # Test 1: Initial question
    logging.info("\nTest 1: Getting initial question")
    response = await handler.generate_response("", messages, persona)
    logging.info(f"Initial question: {response}")
    
    # Test 2: Role information
    logging.info("\nTest 2: Providing role information")
    user_msg = {
        "role": "user",
        "content": "I need to hire a Senior Full Stack Engineer who can lead our core product development"
    }
    messages.append(user_msg)
    response = await handler.generate_response(user_msg["content"], messages, persona)
    logging.info(f"Response after role info: {response}")
    
    # Test 3: Company information
    logging.info("\nTest 3: Providing company information")
    user_msg = {
        "role": "user",
        "content": "We're building an AI-powered recruiting platform that helps companies find and engage top talent through intelligent workflows"
    }
    messages.append(user_msg)
    response = await handler.generate_response(user_msg["content"], messages, persona)
    logging.info(f"Response after company info: {response}")
    
    # Test 4: Requirements information
    logging.info("\nTest 4: Providing requirements")
    user_msg = {
        "role": "user",
        "content": "Requirements: 5+ years of full-stack experience with Python and React, experience with AI/ML, strong system design skills"
    }
    messages.append(user_msg)
    response = await handler.generate_response(user_msg["content"], messages, persona)
    logging.info(f"Response after requirements: {response}")
    
    # Test 5: Unique value proposition
    logging.info("\nTest 5: Providing unique value")
    user_msg = {
        "role": "user",
        "content": "This is a founding engineer role with significant equity, full autonomy, and the chance to shape our AI architecture"
    }
    messages.append(user_msg)
    response = await handler.generate_response(user_msg["content"], messages, persona)
    logging.info(f"Response after unique value: {response}")
    
    # Test 6: Check if ready for sequence generation
    logging.info("\nTest 6: Checking sequence generation trigger")
    should_generate = handler.should_generate_sequence()
    logging.info(f"Should generate sequence: {should_generate}")
    
    if should_generate:
        # Test 7: Generate sequence
        logging.info("\nTest 7: Generating email sequence")
        sequence = await handler.generate_email_sequence(messages, persona)
        logging.info(f"Generated sequence: {sequence}")
        
        # Test 8: Edit sequence
        logging.info("\nTest 8: Testing sequence editing")
        edit_instruction = "make it more concise"
        edited_sequence = await handler.edit_sequence(sequence, edit_instruction)
        logging.info(f"Edited sequence: {edited_sequence}")
    
    logging.info("\nTest flow completed!")

if __name__ == "__main__":
    asyncio.run(test_conversation_flow()) 