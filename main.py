"""
Gift Planning Assistant - Main Entry Point (CLI Interface)
"""

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
    GiftPlanningAssistant
)
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gift_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class CLIInterface:
    """Command-line interface for the Gift Planning Assistant."""
    
    def __init__(self):
        """Initialize the CLI interface."""
        self.assistant = None
        self.conversation_history = []
    
    def initialize(self):
        """Initialize the assistant and all components."""
        try:
            print("🎁 Initializing Gift Planning Assistant...")
            
            # Validate configuration
            validate_config()
            
            # Initialize Gemini client
            client = genai.Client(api_key=GEMINI_API_KEY)
            logger.info(f"Using model: {MODEL_NAME}")
            
            # Initialize session state
            session_state = {}
            
            # Initialize memory manager
            memory_manager = MemoryManager(session_state)
            
            # Initialize all specialized agents
            recipient_agent = RecipientManagerAgent(client, memory_manager)
            occasion_agent = OccasionTrackerAgent(client, memory_manager, date_calculator)
            gift_finder = GiftFinderAgent(client, memory_manager)
            budget_agent = BudgetManagerAgent(client, memory_manager, budget_calculator)
            purchase_agent = PurchaseCoordinatorAgent(client)
            
            # Initialize orchestrator
            self.assistant = GiftPlanningAssistant(
                model=client,
                memory_manager=memory_manager,
                recipient_agent=recipient_agent,
                occasion_agent=occasion_agent,
                gift_finder_agent=gift_finder,
                budget_agent=budget_agent,
                purchase_agent=purchase_agent
            )
            
            print("✓ Initialization complete!\n")
            return True
            
        except ValueError as e:
            print(f"\n❌ Configuration Error: {e}")
            print("\nPlease create a .env file with your GEMINI_API_KEY.")
            print("You can copy .env.example to .env and add your key.\n")
            return False
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            print(f"\n❌ Error: {e}\n")
            return False
    
    def print_menu(self):
        """Print the main menu."""
        print("\n" + "="*60)
        print("🎁  GIFT PLANNING ASSISTANT  🎁".center(60))
        print("="*60)
        print("\nMenu Options:")
        print("  1. Add Recipient")
        print("  2. Add Occasion")
        print("  3. Get Gift Suggestions")
        print("  4. View Budget Summary")
        print("  5. View Upcoming Occasions")
        print("  6. Chat with Assistant")
        print("  7. View Statistics")
        print("  8. Exit")
        print("\n" + "-"*60)
    
    def run_menu(self):
        """Run the menu-driven interface."""
        while True:
            self.print_menu()
            choice = input("\nYour choice (1-8): ").strip()
            
            if choice == '1':
                self.add_recipient_menu()
            elif choice == '2':
                self.add_occasion_menu()
            elif choice == '3':
                self.get_gift_suggestions_menu()
            elif choice == '4':
                self.view_budget_menu()
            elif choice == '5':
                self.view_upcoming_occasions_menu()
            elif choice == '6':
                self.chat_mode()
            elif choice == '7':
                self.view_statistics()
            elif choice == '8':
                print("\n👋 Thank you for using Gift Planning Assistant! Goodbye!\n")
                break
            else:
                print("\n❌ Invalid choice. Please select 1-8.")
    
    def add_recipient_menu(self):
        """Menu for adding a recipient."""
        print("\n--- Add New Recipient ---")
        
        name = input("Recipient name: ").strip()
        if not name:
            print("❌ Name is required.")
            return
        
        age = input("Age (press Enter to skip): ").strip()
        age = int(age) if age.isdigit() else None
        
        interests = input("Interests (comma-separated, e.g., yoga, reading): ").strip()
        interests = [i.strip() for i in interests.split(",")] if interests else []
        
        relationship = input("Relationship (friend, family, colleague, etc.): ").strip()
        
        budget_min = input("Min budget (press Enter to skip): ").strip()
        budget_max = input("Max budget (press Enter to skip): ").strip()
        
        budget_range = None
        if budget_min and budget_max:
            try:
                budget_range = (float(budget_min), float(budget_max))
            except ValueError:
                print("⚠️ Invalid budget values, skipping.")
        
        style = input("Gift style preference (practical, luxury, etc.): ").strip()
        
        # Add recipient
        result = self.assistant.recipient_agent.add_recipient_direct(
            name=name,
            age=age,
            interests=interests,
            relationship=relationship,
            budget_range=budget_range,
            style=style if style else None
        )
        
        if result['success']:
            print(f"\n✓ {result['message']}")
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
    
    def add_occasion_menu(self):
        """Menu for adding an occasion."""
        print("\n--- Add New Occasion ---")
        
        # List recipients
        recipients = self.assistant.memory.get_all_recipients()
        if not recipients:
            print("❌ No recipients found. Please add a recipient first.")
            return
        
        print("\nAvailable recipients:")
        for i, r in enumerate(recipients, 1):
            print(f"  {i}. {r['name']}")
        
        recipient_name = input("\nRecipient name: ").strip()
        
        occasion_type = input("Occasion type (birthday, anniversary, holiday, etc.): ").strip()
        date = input("Date (YYYY-MM-DD): ").strip()
        
        reminder_days = input("Reminder days before (default: 14): ").strip()
        reminder_days = int(reminder_days) if reminder_days.isdigit() else 14
        
        # Add occasion
        result = self.assistant.occasion_agent.add_occasion_direct(
            recipient_name=recipient_name,
            occasion_type=occasion_type,
            date=date,
            reminder_days_before=reminder_days
        )
        
        if result['success']:
            print(f"\n✓ {result['message']}")
            
            # Show days until
            days_result = date_calculator.calculate_days_until(date)
            if days_result['success']:
                print(f"   {days_result['message']}")
        else:
            print(f"\n❌ Error: {result.get('error', result.get('message', 'Unknown error'))}")
    
    def get_gift_suggestions_menu(self):
        """Menu for getting gift suggestions."""
        print("\n--- Get Gift Suggestions ---")
        
        recipients = self.assistant.memory.get_all_recipients()
        if not recipients:
            print("❌ No recipients found. Please add a recipient first.")
            return
        
        print("\nAvailable recipients:")
        for i, r in enumerate(recipients, 1):
            print(f"  {i}. {r['name']} ({', '.join(r.get('interests', [])[:3])})")
        
        recipient_name = input("\nRecipient name (or press Enter for general ideas): ").strip()
        
        print("\n🔍 Searching for gift ideas...\n")
        
        if recipient_name:
            result = self.assistant.gift_finder.find_gifts_for_recipient(recipient_name)
        else:
            message = input("Describe what kind of gift you're looking for: ").strip()
            result = self.assistant.gift_finder.process(message)
        
        if result['success']:
            print(result['message'])
        else:
            print(f"\n❌ Error: {result.get('error', 'Could not generate suggestions')}")
    
    def view_budget_menu(self):
        """Menu for viewing budget."""
        print("\n--- Budget Summary ---\n")
        
        result = self.assistant.budget_agent.get_budget_status()
        
        if result['success']:
            print(f"Total Budget: ${result['total']:.2f}")
            print(f"Total Spent:  ${result['spent']:.2f}")
            print(f"Remaining:    ${result['remaining']:.2f}")
            
            if result.get('percentage_used'):
                print(f"Used:         {result['percentage_used']:.1f}%")
                print(f"Status:       {result.get('status', 'N/A')}")
            
            if result['expense_count'] > 0:
                print(f"\nExpenses ({result['expense_count']}):")
                for exp in result.get('expenses', [])[:5]:
                    print(f"  - ${exp['amount']:.2f} for {exp['recipient_name']}: {exp['description']}")
            
            print(f"\n{result.get('message', '')}")
            
            # Offer to set budget if not set
            if result['total'] == 0:
                set_budget = input("\nWould you like to set a budget? (y/n): ").strip().lower()
                if set_budget == 'y':
                    amount = input("Enter total budget amount: $").strip()
                    try:
                        amount = float(amount)
                        budget_result = self.assistant.budget_agent.set_budget(amount)
                        print(f"✓ {budget_result['message']}")
                    except ValueError:
                        print("❌ Invalid amount")
        else:
            print(f"❌ Error: {result.get('error', 'Could not load budget')}")
    
    def view_upcoming_occasions_menu(self):
        """Menu for viewing upcoming occasions."""
        print("\n--- Upcoming Occasions ---\n")
        
        days_ahead = input("Show occasions in next how many days? (default: 30): ").strip()
        days_ahead = int(days_ahead) if days_ahead.isdigit() else 30
        
        result = self.assistant.occasion_agent.get_upcoming(days_ahead=days_ahead)
        
        if result['success']:
            if result['count'] == 0:
                print(f"No upcoming occasions in the next {days_ahead} days.")
            else:
                print(f"Found {result['count']} upcoming occasions:\n")
                for occ in result['occasions']:
                    print(f"📅 {occ['recipient_name']}'s {occ['type']}")
                    print(f"   Date: {occ['date']} ({occ['days_until']} days away)")
                    print(f"   Reminder: {occ['reminder_days_before']} days before")
                    print()
        else:
            print(f"❌ Error: {result.get('error', 'Could not load occasions')}")
    
    def view_statistics(self):
        """View overall statistics."""
        print("\n--- System Statistics ---\n")
        
        stats = self.assistant.memory.get_stats()
        
        print(f"Total Recipients:       {stats['total_recipients']}")
        print(f"Total Occasions:        {stats['total_occasions']}")
        print(f"Upcoming (30 days):     {stats['upcoming_occasions']}")
        print(f"Total Budget:           ${stats['total_budget']:.2f}")
        print(f"Total Spent:            ${stats['total_spent']:.2f}")
        print(f"Remaining:              ${stats['total_budget'] - stats['total_spent']:.2f}")
    
    def chat_mode(self):
        """Enter free-form chat mode."""
        print("\n--- Chat Mode ---")
        print("Type your message and press Enter. Type 'menu' to return to main menu.\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['menu', 'exit', 'quit', 'back']:
                break
            
            # Add to history
            self.conversation_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Process message
            print("\nAssistant: ", end="", flush=True)
            result = self.assistant.process(user_input, self.conversation_history)
            
            if result['success']:
                response = result.get('response', result.get('message', 'I processed your request.'))
                print(response)
                
                # Add to history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response
                })
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print()
    
    def run(self):
        """Run the main CLI application."""
        if not self.initialize():
            return
        
        # Show welcome message
        welcome = self.assistant.get_welcome_message()
        print(welcome)
        
        # Run menu
        try:
            self.run_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
            print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point."""
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()
