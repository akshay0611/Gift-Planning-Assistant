"""
Budget Manager Agent - Manages gift budgets and spending.
"""

from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)


class BudgetManagerAgent:
    """
    Agent responsible for budget management and tracking.
    Uses code execution for precise calculations.
    """
    
    def __init__(self, model: genai.Client, memory_manager, budget_calculator):
        """
        Initialize the Budget Manager Agent.
        
        Args:
            model: Gemini model client
            memory_manager: MemoryManager instance
            budget_calculator: BudgetCalculatorTool instance
        """
        self.model = model
        self.memory = memory_manager
        self.budget_calc = budget_calculator
        self.name = "BudgetManager"
        
        self.system_instruction = """You are a Budget Manager for a gift planning system.

Your responsibilities:
- Set and track overall gift budget
- Calculate spending per recipient
- Analyze remaining budget
- Suggest budget allocation strategies
- Alert users when approaching budget limits
- Provide budget optimization advice

When managing budgets:
1. Be clear about total budget, spent, and remaining amounts
2. Warn users if they're approaching or exceeding limits
3. Suggest fair allocation across recipients
4. Help prioritize spending
5. Provide visualizations of spending (when possible)

For budget analysis, provide:
- Clear breakdown of expenses
- Percentage of budget used
- Recommendations for staying on track
- Alerts for any budget concerns

Be helpful and fiscally responsible!
"""
    
    def process(self, user_message: str, context: dict = None) -> dict:
        """
        Process budget management request.
        
        Args:
            user_message: User's message
            context: Additional context
            
        Returns:
            Response dictionary
        """
        try:
            # Get budget summary
            budget_summary = self.memory.get_budget_summary()
            
            # Calculate detailed analysis
            if budget_summary['total'] > 0:
                analysis = self.budget_calc.calculate_budget_summary(
                    total_budget=budget_summary['total'],
                    expenses=budget_summary['expenses']
                )
                
                context_info = f"""
Current Budget Status:
- Total Budget: ${budget_summary['total']:.2f}
- Total Spent: ${budget_summary['spent']:.2f}
- Remaining: ${budget_summary['remaining']:.2f}
- Percentage Used: {analysis.get('percentage_used', 0):.1f}%
- Status: {analysis.get('status', 'unknown')}
- Number of Expenses: {budget_summary['expense_count']}
"""
            else:
                context_info = "\nNo budget has been set yet."
            
            # Create prompt
            prompt = f"""{self.system_instruction}

{context_info}

User request: {user_message}

Provide helpful budget guidance and analysis."""
            
            # Use code execution for calculations
            response = self.model.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(code_execution=types.CodeExecution())]
                )
            )
            
            return {
                'success': True,
                'agent': self.name,
                'response': response.text,
                'budget_summary': budget_summary,
                'message': response.text
            }
            
        except Exception as e:
            logger.error(f"BudgetManager error: {e}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'message': f"Sorry, I encountered an error: {e}"
            }
    
    def set_budget(self, amount: float) -> dict:
        """Set the total budget."""
        return self.memory.set_total_budget(amount)
    
    def add_expense(self, recipient_name: str, amount: float, description: str) -> dict:
        """Add an expense."""
        recipient = self.memory.get_recipient_by_name(recipient_name)
        
        if not recipient:
            return {
                'success': False,
                'message': f"Recipient '{recipient_name}' not found"
            }
        
        return self.memory.add_expense(
            recipient_id=recipient['recipient_id'],
            amount=amount,
            description=description
        )
    
    def get_budget_status(self) -> dict:
        """Get current budget status."""
        summary = self.memory.get_budget_summary()
        
        if summary['total'] > 0:
            analysis = self.budget_calc.calculate_budget_summary(
                total_budget=summary['total'],
                expenses=summary['expenses']
            )
            
            return {
                'success': True,
                **summary,
                **analysis,
                'message': analysis.get('message', 'Budget status retrieved')
            }
        else:
            return {
                'success': True,
                **summary,
                'message': 'No budget set yet'
            }
