"""
Recipient Manager Agent - Manages recipient profiles and data.
"""

from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)


class RecipientManagerAgent:
    """
    Agent responsible for managing recipient profiles.
    Handles adding, updating, and retrieving recipient information.
    """
    
    def __init__(self, model: genai.Client, memory_manager):
        """
        Initialize the Recipient Manager Agent.
        
        Args:
            model: Gemini model client
            memory_manager: MemoryManager instance
        """
        self.model = model
        self.memory = memory_manager
        self.name = "RecipientManager"
        
        self.system_instruction = """You are a Recipient Manager for a gift planning system.
        
Your responsibilities:
- Add new recipients with their profiles (name, age, interests, relationship)
- Update recipient information
- Retrieve recipient details and gift history
- Help users remember important details about their gift recipients

When adding a recipient, extract:
- Name (required)
- Age (if mentioned)
- Interests/hobbies (as a list)
- Relationship (friend, family member, colleague, etc.)
- Gift preferences or style (practical, luxury, handmade, etc.)
- Budget range if specified

Be conversational and friendly. Ask clarifying questions if needed.
"""
    
    def process(self, user_message: str, context: dict = None) -> dict:
        """
        Process user request related to recipient management.
        
        Args:
            user_message: User's message
            context: Additional context
            
        Returns:
            Response dictionary
        """
        try:
            # Get current recipients for context
            recipients = self.memory.get_all_recipients()
            
            # Build context message
            context_info = f"\n\nCurrent recipients: {len(recipients)}"
            if recipients:
                context_info += "\n" + "\n".join([
                    f"- {r['name']} ({r.get('relationship', 'unknown')})"
                    for r in recipients[:5]
                ])
            
            # Create prompt
            prompt = f"""{self.system_instruction}

{context_info}

User request: {user_message}

Analyze the request and respond appropriately. If the user wants to add a recipient, 
extract the details and format your response clearly."""
            
            # Generate response using Gemini
            response = self.model.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            agent_response = response.text
            
            # Try to detect if this is an add recipient request
            if any(keyword in user_message.lower() for keyword in ['add', 'new', 'create']):
                # This is a simplified extraction - in production, use function calling
                return {
                    'success': True,
                    'agent': self.name,
                    'response': agent_response,
                    'action': 'pending_add',
                    'message': agent_response
                }
            
            return {
                'success': True,
                'agent': self.name,
                'response': agent_response,
                'message': agent_response
            }
            
        except Exception as e:
            logger.error(f"RecipientManager error: {e}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'message': f"Sorry, I encountered an error: {e}"
            }
    
    def add_recipient_direct(self, name: str, **kwargs) -> dict:
        """
        Directly add a recipient (for programmatic use).
        
        Args:
            name: Recipient name
            **kwargs: Additional recipient attributes
            
        Returns:
            Result dictionary
        """
        return self.memory.add_recipient(name=name, **kwargs)
    
    def get_recipient_info(self, recipient_name: str) -> dict:
        """Get recipient information by name."""
        recipient = self.memory.get_recipient_by_name(recipient_name)
        
        if not recipient:
            return {
                'success': False,
                'message': f"Recipient '{recipient_name}' not found"
            }
        
        return {
            'success': True,
            'recipient': recipient,
            'message': f"Found {recipient['name']}"
        }
