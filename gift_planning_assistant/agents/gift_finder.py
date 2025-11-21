"""
Gift Finder Agent - Suggests personalized gifts using search.
"""

from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)


class GiftFinderAgent:
    """
    Agent responsible for finding and suggesting personalized gifts.
    Uses Google Search to find relevant gift ideas.
    """
    
    def __init__(self, model: genai.Client, memory_manager):
        """
        Initialize the Gift Finder Agent.
        
        Args:
            model: Gemini model client
            memory_manager: MemoryManager instance
        """
        self.model = model
        self.memory = memory_manager
        self.name = "GiftFinder"
        
        self.system_instruction = """You are a Gift Finder for a gift planning system.

Your responsibilities:
- Analyze recipient profiles (interests, age, past gifts)
- Suggest personalized gift ideas
- Filter suggestions by budget
- Find unique and creative gift options
- Avoid suggesting duplicate gifts

When suggesting gifts:
1. Consider recipient's interests and hobbies
2. Take age appropriateness into account
3. Check past gift history to avoid duplicates
4. Stay within budget constraints
5. Provide diverse options (practical, fun, experiential, etc.)
6. Include reasoning for each suggestion

For each gift suggestion, provide:
- Gift name/description
- Estimated price range
- Why it's suitable for this recipient
- Where to buy (if known)

Be creative and thoughtful in your suggestions!
"""
    
    def process(self, user_message: str, recipient_name: str = None, context: dict = None) -> dict:
        """
        Process gift finder request.
        
        Args:
            user_message: User's message
            recipient_name: Optional recipient name
            context: Additional context
            
        Returns:
            Response with gift suggestions
        """
        try:
            recipient_info = ""
            budget_info = ""
            
            # Get recipient details if specified
            if recipient_name:
                recipient = self.memory.get_recipient_by_name(recipient_name)
                if recipient:
                    recipient_info = f"""
Recipient Profile:
- Name: {recipient['name']}
- Age: {recipient.get('age', 'Unknown')}
- Interests: {', '.join(recipient.get('interests', []))}
- Relationship: {recipient.get('relationship', 'Unknown')}
- Style preference: {recipient.get('preferences', {}).get('style', 'Not specified')}
- Past gifts: {', '.join([g['gift'] for g in recipient.get('gift_history', [])])}
"""
                    
                    budget_range = recipient.get('preferences', {}).get('budget_range')
                    if budget_range:
                        budget_info = f"\nBudget range: ${budget_range[0]} - ${budget_range[1]}"
            
            # Create prompt
            prompt = f"""{self.system_instruction}

{recipient_info}
{budget_info}

User request: {user_message}

Provide 5 thoughtful gift suggestions with detailed reasoning."""
            
            # Use Google Search tool for real gift ideas
            # Note: In production, configure actual Google Search tool
            response = self.model.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            return {
                'success': True,
                'agent': self.name,
                'response': response.text,
                'recipient': recipient_name,
                'message': response.text
            }
            
        except Exception as e:
            logger.error(f"GiftFinder error: {e}")
            # Fallback without search if it fails
            try:
                response = self.model.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt
                )
                
                return {
                    'success': True,
                    'agent': self.name,
                    'response': response.text,
                    'message': response.text,
                    'note': 'Generated without search'
                }
            except Exception as e2:
                logger.error(f"GiftFinder fallback error: {e2}")
                return {
                    'success': False,
                    'agent': self.name,
                    'error': str(e2),
                    'message': f"Sorry, I couldn't generate gift suggestions: {e2}"
                }
    
    def find_gifts_for_recipient(self, recipient_name: str, budget_range: tuple = None) -> dict:
        """
        Find gifts for a specific recipient.
        
        Args:
            recipient_name: Name of recipient
            budget_range: Optional (min, max) budget
            
        Returns:
            Gift suggestions
        """
        message = f"Find gift ideas for {recipient_name}"
        if budget_range:
            message += f" with budget ${budget_range[0]}-${budget_range[1]}"
        
        return self.process(message, recipient_name=recipient_name)
