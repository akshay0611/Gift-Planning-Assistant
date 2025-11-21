"""
Gift Planning Assistant - Main Agent Entry Point for ADK
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk import Agent
from google import genai
from config import GEMINI_API_KEY, MODEL_NAME, validate_config
from memory import MemoryManager
from tools import date_calculator, budget_calculator
from agents import (
    RecipientManagerAgent,
    OccasionTrackerAgent,
    GiftFinderAgent,
    BudgetManagerAgent,
    PurchaseCoordinatorAgent,
)

# Validate configuration
validate_config()

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize session state
session_state = {}

# Initialize memory manager
memory_manager = MemoryManager(session_state)

# Initialize specialized agents
recipient_agent = RecipientManagerAgent(client, memory_manager)
occasion_agent = OccasionTrackerAgent(client, memory_manager, date_calculator)
gift_finder = GiftFinderAgent(client, memory_manager)
budget_agent = BudgetManagerAgent(client, memory_manager, budget_calculator)
purchase_agent = PurchaseCoordinatorAgent(client)

# Create the main agent (root_agent is the standard name for ADK)
root_agent = Agent(
    model=MODEL_NAME,
    name="GiftPlanningAssistant",
    description="AI assistant that helps you plan and manage gift-giving for all occasions",
    instruction="""You are the Gift Planning Assistant, an AI coordinator that helps users manage their gift-giving needs.

You coordinate a team of specialized agents:
1. RecipientManager - Manages recipient profiles
2. OccasionTracker - Tracks important dates and occasions
3. GiftFinder - Suggests personalized gifts
4. BudgetManager - Manages spending and budgets
5. PurchaseCoordinator - Finds where to buy gifts

Your role is to:
- Understand user intent and help users naturally
- Track recipients with their interests, age, and preferences
- Remember important occasions like birthdays and anniversaries
- Suggest personalized gifts based on recipient profiles
- Manage budgets and track spending
- Find where to buy gifts at the best prices

Be friendly, helpful, and proactive. Guide users through the gift planning process.

When users want to add recipients, track occasions, find gifts, manage budgets, or find purchase options, help them accomplish these tasks conversationally."""
)

# Store references to specialized agents for later use
root_agent._recipient_agent = recipient_agent
root_agent._occasion_agent = occasion_agent
root_agent._gift_finder = gift_finder
root_agent._budget_agent = budget_agent
root_agent._purchase_agent = purchase_agent
root_agent._memory = memory_manager
