"""
Occasion Tracker Agent - Manages occasions and reminders.
"""

from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)


class OccasionTrackerAgent:
    """
    Agent responsible for tracking occasions and managing reminders.
    """
    
    def __init__(self, model: genai.Client, memory_manager, date_calculator):
        """
        Initialize the Occasion Tracker Agent.
        
        Args:
            model: Gemini model client
            memory_manager: MemoryManager instance
            date_calculator: DateCalculatorTool instance
        """
        self.model = model
        self.memory = memory_manager
        self.date_calc = date_calculator
        self.name = "OccasionTracker"
        
        self.system_instruction = """You are an Occasion Tracker for a gift planning system.

Your responsibilities:
- Add occasions (birthdays, anniversaries, holidays, custom events)
- Calculate days until events
- List upcoming occasions
- Set up reminders
- Help users stay organized with important dates

When adding an occasion, extract:
- Recipient name or ID
- Occasion type (birthday, anniversary, wedding, graduation, holiday, etc.)
- Date (in various formats like "December 25", "12/25/2024", etc.)
- Reminder preferences (how many days before)

For upcoming occasions, provide:
- Event details
- Days until event
- Gift suggestions status
- Budget information if available

Be helpful and proactive in reminding users about upcoming events.
"""
    
    def process(self, user_message: str, context: dict = None) -> dict:
        """
        Process user request related to occasion tracking.
        
        Args:
            user_message: User's message
            context: Additional context
            
        Returns:
            Response dictionary
        """
        try:
            # Get upcoming occasions
            upcoming = self.memory.get_upcoming_occasions(days_ahead=90)
            
            # Build context
            context_info = f"\n\nUpcoming occasions: {len(upcoming)}"
            if upcoming:
                context_info += "\n" + "\n".join([
                    f"- {occ['recipient_name']}'s {occ['type']} in {occ['days_until']} days ({occ['date']})"
                    for occ in upcoming[:5]
                ])
            
            # Create prompt
            prompt = f"""{self.system_instruction}

{context_info}

User request: {user_message}

Respond helpfully to the user's request about occasions."""
            
            # Generate response
            response = self.model.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            return {
                'success': True,
                'agent': self.name,
                'response': response.text,
                'upcoming_count': len(upcoming),
                'message': response.text
            }
            
        except Exception as e:
            logger.error(f"OccasionTracker error: {e}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'message': f"Sorry, I encountered an error: {e}"
            }
    
    def add_occasion_direct(self, recipient_name: str, occasion_type: str, date: str, **kwargs) -> dict:
        """
        Directly add an occasion (for programmatic use).
        
        Args:
            recipient_name: Name of recipient
            occasion_type: Type of occasion
            date: Date string
            **kwargs: Additional parameters
            
        Returns:
            Result dictionary
        """
        # Find recipient
        recipient = self.memory.get_recipient_by_name(recipient_name)
        
        if not recipient:
            return {
                'success': False,
                'message': f"Recipient '{recipient_name}' not found"
            }
        
        return self.memory.add_occasion(
            recipient_id=recipient['recipient_id'],
            occasion_type=occasion_type,
            date=date,
            **kwargs
        )
    
    def get_upcoming(self, days_ahead: int = 30) -> dict:
        """Get upcoming occasions."""
        upcoming = self.memory.get_upcoming_occasions(days_ahead=days_ahead)
        
        return {
            'success': True,
            'count': len(upcoming),
            'occasions': upcoming,
            'message': f"Found {len(upcoming)} upcoming occasions"
        }
