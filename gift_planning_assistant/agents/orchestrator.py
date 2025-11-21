"""
Gift Planning Assistant - Main Orchestrator Agent.
Coordinates all specialized agents and manages the overall workflow.
"""

from google.adk import Agent
from google import genai
from google.genai import types
from config import MODEL_NAME
from pydantic import ConfigDict, Field
from typing import Any, ClassVar
import logging

logger = logging.getLogger(__name__)


class GiftPlanningAssistant(Agent):
    """
    Main orchestrator agent that coordinates all specialized agents.
    Delegates tasks to appropriate sub-agents based on user intent.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    client: Any = Field(description="Gemini client instance")
    memory: Any = Field(description="Memory manager instance")
    recipient_agent: Any = Field(description="Recipient manager agent")
    occasion_agent: Any = Field(description="Occasion tracker agent")
    gift_finder: Any = Field(description="Gift finder agent")
    budget_agent: Any = Field(description="Budget manager agent")
    purchase_agent: Any = Field(description="Purchase coordinator agent")
    
    SYSTEM_INSTRUCTION: ClassVar[str] = """You are the Gift Planning Assistant, an AI coordinator that helps users manage their gift-giving needs.

You coordinate a team of specialized agents:
1. RecipientManager - Manages recipient profiles
2. OccasionTracker - Tracks important dates and occasions
3. GiftFinder - Suggests personalized gifts
4. BudgetManager - Manages spending and budgets
5. PurchaseCoordinator - Finds where to buy gifts

Your role is to:
- Understand user intent
- Delegate to appropriate agents
- Coordinate multi-step workflows
- Provide a seamless user experience
- Remember context across the conversation

Common workflows:
- Add Recipient → Add Occasion → Find Gifts → Check Budget → Find Purchase Options
- View Upcoming Occasions → Get Gift Suggestions → Compare Prices
- Set Budget → Track Spending → Get Budget Advice

Be friendly, helpful, and proactive. Guide users through the gift planning process."""
    
    def __init__(
        self,
        model: genai.Client,
        memory_manager,
        recipient_agent,
        occasion_agent,
        gift_finder_agent,
        budget_agent,
        purchase_agent,
        **kwargs
    ):
        """
        Initialize the Gift Planning Assistant orchestrator.
        """
        # Initialize parent Agent class
        super().__init__(
            model=MODEL_NAME,
            name="GiftPlanningAssistant",
            description="AI assistant that helps you plan and manage gift-giving for all occasions",
            instruction=GiftPlanningAssistant.SYSTEM_INSTRUCTION,
            client=model,
            memory=memory_manager,
            recipient_agent=recipient_agent,
            occasion_agent=occasion_agent,
            gift_finder=gift_finder_agent,
            budget_agent=budget_agent,
            purchase_agent=purchase_agent,
            **kwargs
        )
    
    def process(self, user_message: str, conversation_history: list = None) -> dict:
        """
        Process user message and coordinate agents.
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            Response dictionary
        """
        try:
            # Determine intent and route to appropriate agent(s)
            intent = self._classify_intent(user_message)
            
            logger.info(f"Classified intent: {intent}")
            
            # Route to appropriate handler
            if intent == 'add_recipient':
                return self._handle_add_recipient(user_message)
            
            elif intent == 'add_occasion':
                return self._handle_add_occasion(user_message)
            
            elif intent == 'find_gifts':
                return self._handle_find_gifts(user_message)
            
            elif intent == 'budget':
                return self._handle_budget(user_message)
            
            elif intent == 'purchase':
                return self._handle_purchase(user_message)
            
            elif intent == 'upcoming_occasions':
                return self._handle_upcoming_occasions(user_message)
            
            elif intent == 'general':
                return self._handle_general(user_message, conversation_history)
            
            else:
                return self._handle_general(user_message, conversation_history)
                
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"I encountered an error: {e}. Please try again."
            }

    def run(self, input: str, **kwargs):
        """ADK compatible run method."""
        # ADK might pass input as 'input' or 'message'
        # We'll assume 'input' based on standard practices
        result = self.process(input)
        # ADK expects a string or specific response type usually
        # But let's return the message string for now
        return result.get('message', str(result))
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent from message."""
        message_lower = message.lower()
        
        # Simple keyword-based classification
        if any(kw in message_lower for kw in ['add recipient', 'new recipient', 'add person', 'create recipient']):
            return 'add_recipient'
        
        if any(kw in message_lower for kw in ['add occasion', 'new occasion', 'birthday', 'anniversary', 'add event']):
            return 'add_occasion'
        
        if any(kw in message_lower for kw in ['find gift', 'suggest gift', 'gift idea', 'what should i get', 'gift for']):
            return 'find_gifts'
        
        if any(kw in message_lower for kw in ['budget', 'spending', 'how much', 'set budget', 'track expense']):
            return 'budget'
        
        if any(kw in message_lower for kw in ['where to buy', 'purchase', 'find price', 'compare price', 'buy']):
            return 'purchase'
        
        if any(kw in message_lower for kw in ['upcoming', 'next occasion', 'what\'s coming', 'remind']):
            return 'upcoming_occasions'
        
        return 'general'
    
    def _handle_add_recipient(self, message: str) -> dict:
        """Handle adding a recipient."""
        return self.recipient_agent.process(message)
    
    def _handle_add_occasion(self, message: str) -> dict:
        """Handle adding an occasion."""
        return self.occasion_agent.process(message)
    
    def _handle_find_gifts(self, message: str) -> dict:
        """Handle finding gifts - may run in parallel with budget check."""
        # In production, use ParallelAgent here
        gift_result = self.gift_finder.process(message)
        
        # Could also run budget check in parallel
        # For now, sequential
        return gift_result
    
    def _handle_budget(self, message: str) -> dict:
        """Handle budget management."""
        return self.budget_agent.process(message)
    
    def _handle_purchase(self, message: str) -> dict:
        """Handle purchase coordination."""
        return self.purchase_agent.process(message)
    
    def _handle_upcoming_occasions(self, message: str) -> dict:
        """Handle upcoming occasions query."""
        return self.occasion_agent.process(message)
    
    def _handle_general(self, message: str, conversation_history: list = None) -> dict:
        """Handle general queries with context awareness."""
        try:
            # Get system state for context
            stats = self.memory.get_stats()
            
            context_info = f"""
System Status:
- Recipients: {stats['total_recipients']}
- Occasions: {stats['total_occasions']}
- Upcoming occasions (next 30 days): {stats['upcoming_occasions']}
- Budget: ${stats['total_budget']:.2f}
- Spent: ${stats['total_spent']:.2f}
"""
            
            # Build conversation context
            history_text = ""
            if conversation_history:
                history_text = "\n\nRecent conversation:\n" + "\n".join(
                    [f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]]
                )
            
            prompt = f"""{GiftPlanningAssistant.SYSTEM_INSTRUCTION}

{context_info}
{history_text}

User: {message}

Respond helpfully and guide the user. If appropriate, suggest next steps."""
            
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            
            return {
                'success': True,
                'agent': self.name,
                'response': response.text,
                'message': response.text
            }
            
        except Exception as e:
            logger.error(f"General handler error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "I'm sorry, I couldn't process that request."
            }
    
    def get_welcome_message(self) -> str:
        """Get welcome message for new users."""
        stats = self.memory.get_stats()
        
        if stats['total_recipients'] == 0:
            return """Welcome to the Gift Planning Assistant! 🎁

I'm here to help you manage your gift-giving with ease. I can:
- Track recipients and their preferences
- Remember important occasions
- Suggest personalized gifts
- Manage your gift budget
- Find the best places to buy

Let's get started! Would you like to add your first recipient?"""
        else:
            return f"""Welcome back! 🎁

You currently have:
- {stats['total_recipients']} recipients
- {stats['upcoming_occasions']} upcoming occasions in the next 30 days
- ${stats['total_budget'] - stats['total_spent']:.2f} remaining in your budget

How can I help you today?"""
