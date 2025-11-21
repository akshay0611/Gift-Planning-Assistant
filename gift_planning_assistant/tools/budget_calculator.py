"""
Custom budget calculator tool for the Gift Planning Agent.
Provides budget tracking and allocation utilities.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BudgetCalculatorTool:
    """Tool for budget calculations and tracking."""
    
    def __init__(self):
        self.name = "budget_calculator"
        self.description = (
            "Calculate budget allocations, track spending, and analyze budget limits. "
            "Helps manage gift budgets across multiple recipients."
        )
    
    def calculate_budget_summary(
        self, 
        total_budget: float, 
        expenses: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Calculate budget summary with spending breakdown.
        
        Args:
            total_budget: Total available budget
            expenses: List of expenses with 'recipient' and 'amount'
            
        Returns:
            Dictionary with budget analysis
        """
        try:
            # Calculate total spent
            total_spent = sum(expense.get('amount', 0) for expense in expenses)
            remaining = total_budget - total_spent
            percentage_used = (total_spent / total_budget * 100) if total_budget > 0 else 0
            
            # Determine budget status
            if percentage_used >= 100:
                status = "over_budget"
                alert_level = "critical"
            elif percentage_used >= 90:
                status = "near_limit"
                alert_level = "warning"
            elif percentage_used >= 75:
                status = "high_usage"
                alert_level = "caution"
            else:
                status = "healthy"
                alert_level = "normal"
            
            return {
                "success": True,
                "total_budget": total_budget,
                "total_spent": total_spent,
                "remaining": remaining,
                "percentage_used": round(percentage_used, 1),
                "status": status,
                "alert_level": alert_level,
                "expense_count": len(expenses),
                "message": self._format_budget_message(
                    total_budget, total_spent, remaining, percentage_used
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating budget summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def suggest_allocation(
        self, 
        total_budget: float, 
        recipients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Suggest budget allocation across recipients.
        
        Args:
            total_budget: Total available budget
            recipients: List of recipients with optional 'priority' field
            
        Returns:
            Dictionary with suggested allocations
        """
        try:
            if not recipients:
                return {
                    "success": False,
                    "error": "No recipients provided"
                }
            
            # Calculate allocations based on priority if available
            allocations = []
            num_recipients = len(recipients)
            
            # Check if priorities are specified
            has_priorities = any('priority' in r for r in recipients)
            
            if has_priorities:
                # Weight-based allocation
                total_priority = sum(r.get('priority', 1) for r in recipients)
                
                for recipient in recipients:
                    priority = recipient.get('priority', 1)
                    weight = priority / total_priority
                    allocation = total_budget * weight
                    
                    allocations.append({
                        "recipient": recipient.get('name', 'Unknown'),
                        "suggested_amount": round(allocation, 2),
                        "priority": priority,
                        "percentage": round(weight * 100, 1)
                    })
            else:
                # Equal allocation
                per_person = total_budget / num_recipients
                
                for recipient in recipients:
                    allocations.append({
                        "recipient": recipient.get('name', 'Unknown'),
                        "suggested_amount": round(per_person, 2),
                        "priority": 1,
                        "percentage": round(100 / num_recipients, 1)
                    })
            
            return {
                "success": True,
                "total_budget": total_budget,
                "recipients_count": num_recipients,
                "allocation_method": "weighted" if has_priorities else "equal",
                "allocations": allocations,
                "message": f"Budget allocated across {num_recipients} recipients"
            }
            
        except Exception as e:
            logger.error(f"Error suggesting allocation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_budget_limit(
        self, 
        item_cost: float, 
        budget_range: tuple
    ) -> Dict[str, Any]:
        """
        Check if an item cost is within budget range.
        
        Args:
            item_cost: Cost of the item
            budget_range: Tuple of (min_budget, max_budget)
            
        Returns:
            Dictionary with budget check result
        """
        try:
            min_budget, max_budget = budget_range
            
            within_budget = min_budget <= item_cost <= max_budget
            
            if item_cost < min_budget:
                status = "below_range"
                message = f"${item_cost} is below your minimum budget of ${min_budget}"
            elif item_cost > max_budget:
                status = "above_range"
                message = f"${item_cost} exceeds your maximum budget of ${max_budget}"
            else:
                status = "within_range"
                percentage = ((item_cost - min_budget) / (max_budget - min_budget) * 100)
                message = f"${item_cost} is within budget (at {round(percentage, 0)}% of range)"
            
            return {
                "success": True,
                "item_cost": item_cost,
                "min_budget": min_budget,
                "max_budget": max_budget,
                "within_budget": within_budget,
                "status": status,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error checking budget limit: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_budget_message(
        self, 
        total: float, 
        spent: float, 
        remaining: float, 
        percentage: float
    ) -> str:
        """Format a human-readable budget message."""
        if percentage >= 100:
            return f"⚠️ Over budget! Spent ${spent:.2f} of ${total:.2f} budget (${abs(remaining):.2f} over)"
        elif percentage >= 90:
            return f"⚠️ Approaching budget limit! ${remaining:.2f} remaining of ${total:.2f}"
        elif percentage >= 75:
            return f"You've used {percentage:.1f}% of your budget. ${remaining:.2f} remaining."
        else:
            return f"Budget is healthy. ${remaining:.2f} remaining of ${total:.2f} ({100-percentage:.1f}% available)"


# Singleton instance
budget_calculator = BudgetCalculatorTool()
