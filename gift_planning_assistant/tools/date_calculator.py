"""
Custom date calculator tool for the Gift Planning Agent.
Provides date calculation and formatting utilities.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DateCalculatorTool:
    """Tool for date calculations and formatting."""
    
    def __init__(self):
        self.name = "date_calculator"
        self.description = (
            "Calculate days until events, parse dates, and format dates. "
            "Accepts date strings in various formats and returns days until the event."
        )
    
    def calculate_days_until(self, target_date_str: str) -> Dict[str, Any]:
        """
        Calculate the number of days until a target date.
        
        Args:
            target_date_str: Date string in format YYYY-MM-DD or similar
            
        Returns:
            Dictionary with days_until, formatted_date, and status
        """
        try:
            # Parse the target date
            target_date = self._parse_date(target_date_str)
            
            # Get current date (without time for day comparison)
            today = datetime.now().date()
            
            # Calculate days difference
            days_until = (target_date - today).days
            
            # Determine status
            if days_until < 0:
                status = "past"
            elif days_until == 0:
                status = "today"
            elif days_until <= 7:
                status = "this_week"
            elif days_until <= 30:
                status = "this_month"
            else:
                status = "future"
            
            return {
                "success": True,
                "days_until": days_until,
                "target_date": target_date.strftime("%Y-%m-%d"),
                "formatted_date": target_date.strftime("%B %d, %Y"),
                "status": status,
                "message": self._format_message(days_until, target_date)
            }
            
        except Exception as e:
            logger.error(f"Error calculating days until date: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Could not parse date: {target_date_str}"
            }
    
    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse date string into datetime.date object."""
        # Try multiple date formats
        formats = [
            "%Y-%m-%d",      # 2024-12-25
            "%m/%d/%Y",      # 12/25/2024
            "%d-%m-%Y",      # 25-12-2024
            "%B %d, %Y",     # December 25, 2024
            "%b %d, %Y",     # Dec 25, 2024
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}. Use format YYYY-MM-DD")
    
    def _format_message(self, days_until: int, target_date: datetime.date) -> str:
        """Format a human-readable message about the date."""
        formatted = target_date.strftime("%B %d, %Y")
        
        if days_until < 0:
            return f"{formatted} was {abs(days_until)} days ago"
        elif days_until == 0:
            return f"Today is {formatted}!"
        elif days_until == 1:
            return f"{formatted} is tomorrow!"
        elif days_until <= 7:
            return f"{formatted} is in {days_until} days (this week)"
        elif days_until <= 30:
            return f"{formatted} is in {days_until} days (about {days_until // 7} weeks)"
        else:
            months = days_until // 30
            if months == 1:
                return f"{formatted} is in about 1 month"
            else:
                return f"{formatted} is in about {months} months"
    
    def get_reminder_dates(self, target_date_str: str, days_before: list = None) -> Dict[str, Any]:
        """
        Calculate reminder dates before an event.
        
        Args:
            target_date_str: Target event date
            days_before: List of days before event to set reminders (default: [14, 7, 3, 1])
            
        Returns:
            Dictionary with reminder dates
        """
        if days_before is None:
            days_before = [14, 7, 3, 1]
        
        try:
            target_date = self._parse_date(target_date_str)
            reminders = []
            
            for days in days_before:
                reminder_date = target_date - timedelta(days=days)
                reminders.append({
                    "days_before": days,
                    "reminder_date": reminder_date.strftime("%Y-%m-%d"),
                    "formatted": reminder_date.strftime("%B %d, %Y")
                })
            
            return {
                "success": True,
                "target_date": target_date.strftime("%Y-%m-%d"),
                "reminders": reminders
            }
            
        except Exception as e:
            logger.error(f"Error calculating reminder dates: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
date_calculator = DateCalculatorTool()
