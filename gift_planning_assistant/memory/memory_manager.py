"""
Memory Bank manager for Gift Planning Agent.
Manages persistent storage of recipient profiles and occasions in session state.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages the Memory Bank for recipients and occasions.
    Uses session state as the persistence layer.
    """
    
    def __init__(self, session_state: Dict[str, Any]):
        """
        Initialize the Memory Manager with session state.
        
        Args:
            session_state: The session state dictionary for persistence
        """
        self.state = session_state
        
        # Initialize memory structures if they don't exist
        if 'recipients' not in self.state:
            self.state['recipients'] = {}
        if 'occasions' not in self.state:
            self.state['occasions'] = {}
        if 'budget' not in self.state:
            self.state['budget'] = {
                'total': 0.0,
                'spent': 0.0,
                'expenses': []
            }
    
    # ==================== Recipient Management ====================
    
    def add_recipient(
        self,
        name: str,
        age: Optional[int] = None,
        interests: Optional[List[str]] = None,
        relationship: Optional[str] = None,
        budget_range: Optional[tuple] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new recipient to memory.
        
        Args:
            name: Recipient's name
            age: Recipient's age
            interests: List of interests/hobbies
            relationship: Relationship to user (friend, family, etc.)
            budget_range: Tuple of (min, max) budget
            style: Gift style preference (practical, luxury, etc.)
            
        Returns:
            Dictionary with recipient data and ID
        """
        recipient_id = str(uuid.uuid4())
        
        recipient = {
            'recipient_id': recipient_id,
            'name': name,
            'age': age,
            'interests': interests or [],
            'relationship': relationship,
            'gift_history': [],
            'preferences': {
                'budget_range': budget_range,
                'style': style
            },
            'created_at': datetime.now().isoformat()
        }
        
        self.state['recipients'][recipient_id] = recipient
        logger.info(f"Added recipient: {name} (ID: {recipient_id})")
        
        return {
            'success': True,
            'recipient_id': recipient_id,
            'recipient': recipient,
            'message': f"Added {name} to your recipients"
        }
    
    def get_recipient(self, recipient_id: str) -> Optional[Dict[str, Any]]:
        """Get recipient by ID."""
        return self.state['recipients'].get(recipient_id)
    
    def get_recipient_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get recipient by name (case-insensitive)."""
        name_lower = name.lower()
        for recipient in self.state['recipients'].values():
            if recipient['name'].lower() == name_lower:
                return recipient
        return None
    
    def get_all_recipients(self) -> List[Dict[str, Any]]:
        """Get all recipients."""
        return list(self.state['recipients'].values())
    
    def update_recipient(
        self,
        recipient_id: str,
        **updates
    ) -> Dict[str, Any]:
        """
        Update recipient information.
        
        Args:
            recipient_id: ID of recipient to update
            **updates: Fields to update
            
        Returns:
            Update result
        """
        if recipient_id not in self.state['recipients']:
            return {
                'success': False,
                'error': f"Recipient {recipient_id} not found"
            }
        
        recipient = self.state['recipients'][recipient_id]
        
        # Update allowed fields
        for key, value in updates.items():
            if key in ['name', 'age', 'interests', 'relationship']:
                recipient[key] = value
            elif key in ['budget_range', 'style']:
                recipient['preferences'][key] = value
        
        recipient['updated_at'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'recipient': recipient,
            'message': f"Updated {recipient['name']}"
        }
    
    def add_gift_to_history(
        self,
        recipient_id: str,
        gift: str,
        occasion: str,
        cost: float,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a gift to recipient's history."""
        if recipient_id not in self.state['recipients']:
            return {
                'success': False,
                'error': f"Recipient {recipient_id} not found"
            }
        
        recipient = self.state['recipients'][recipient_id]
        
        gift_entry = {
            'date': date or datetime.now().strftime("%Y-%m-%d"),
            'occasion': occasion,
            'gift': gift,
            'cost': cost
        }
        
        recipient['gift_history'].append(gift_entry)
        
        return {
            'success': True,
            'message': f"Added gift to {recipient['name']}'s history"
        }
    
    # ==================== Occasion Management ====================
    
    def add_occasion(
        self,
        recipient_id: str,
        occasion_type: str,
        date: str,
        reminder_days_before: int = 14
    ) -> Dict[str, Any]:
        """
        Add a new occasion.
        
        Args:
            recipient_id: ID of associated recipient
            occasion_type: Type of occasion (birthday, anniversary, etc.)
            date: Date of occasion (YYYY-MM-DD)
            reminder_days_before: Days before to remind
            
        Returns:
            Occasion data and ID
        """
        if recipient_id not in self.state['recipients']:
            return {
                'success': False,
                'error': f"Recipient {recipient_id} not found"
            }
        
        occasion_id = str(uuid.uuid4())
        
        occasion = {
            'occasion_id': occasion_id,
            'recipient_id': recipient_id,
            'type': occasion_type,
            'date': date,
            'reminder_days_before': reminder_days_before,
            'status': 'upcoming',
            'created_at': datetime.now().isoformat()
        }
        
        self.state['occasions'][occasion_id] = occasion
        
        recipient = self.state['recipients'][recipient_id]
        logger.info(f"Added occasion: {occasion_type} for {recipient['name']} on {date}")
        
        return {
            'success': True,
            'occasion_id': occasion_id,
            'occasion': occasion,
            'message': f"Added {occasion_type} for {recipient['name']} on {date}"
        }
    
    def get_occasion(self, occasion_id: str) -> Optional[Dict[str, Any]]:
        """Get occasion by ID."""
        return self.state['occasions'].get(occasion_id)
    
    def get_upcoming_occasions(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming occasions within specified days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming occasions with recipient info
        """
        from tools.date_calculator import date_calculator
        
        upcoming = []
        today = datetime.now().date()
        
        for occasion in self.state['occasions'].values():
            if occasion['status'] != 'upcoming':
                continue
            
            # Calculate days until occasion
            result = date_calculator.calculate_days_until(occasion['date'])
            
            if result['success'] and 0 <= result['days_until'] <= days_ahead:
                # Get recipient info
                recipient = self.get_recipient(occasion['recipient_id'])
                
                upcoming.append({
                    **occasion,
                    'days_until': result['days_until'],
                    'recipient_name': recipient['name'] if recipient else 'Unknown',
                    'recipient': recipient
                })
        
        # Sort by days_until
        upcoming.sort(key=lambda x: x['days_until'])
        
        return upcoming
    
    def get_occasions_for_recipient(self, recipient_id: str) -> List[Dict[str, Any]]:
        """Get all occasions for a specific recipient."""
        return [
            occ for occ in self.state['occasions'].values()
            if occ['recipient_id'] == recipient_id
        ]
    
    def mark_occasion_complete(self, occasion_id: str) -> Dict[str, Any]:
        """Mark an occasion as complete."""
        if occasion_id not in self.state['occasions']:
            return {
                'success': False,
                'error': f"Occasion {occasion_id} not found"
            }
        
        self.state['occasions'][occasion_id]['status'] = 'complete'
        
        return {
            'success': True,
            'message': "Occasion marked as complete"
        }
    
    # ==================== Budget Management ====================
    
    def set_total_budget(self, amount: float) -> Dict[str, Any]:
        """Set the total budget."""
        self.state['budget']['total'] = amount
        
        return {
            'success': True,
            'total_budget': amount,
            'message': f"Total budget set to ${amount:.2f}"
        }
    
    def add_expense(
        self,
        recipient_id: str,
        amount: float,
        description: str
    ) -> Dict[str, Any]:
        """Add an expense to the budget."""
        if recipient_id not in self.state['recipients']:
            return {
                'success': False,
                'error': f"Recipient {recipient_id} not found"
            }
        
        recipient = self.state['recipients'][recipient_id]
        
        expense = {
            'recipient_id': recipient_id,
            'recipient_name': recipient['name'],
            'amount': amount,
            'description': description,
            'date': datetime.now().isoformat()
        }
        
        self.state['budget']['expenses'].append(expense)
        self.state['budget']['spent'] += amount
        
        return {
            'success': True,
            'expense': expense,
            'message': f"Added ${amount:.2f} expense for {recipient['name']}"
        }
    
    def get_budget_summary(self) -> Dict[str, Any]:
        """Get budget summary."""
        budget = self.state['budget']
        
        return {
            'total': budget['total'],
            'spent': budget['spent'],
            'remaining': budget['total'] - budget['spent'],
            'expenses': budget['expenses'],
            'expense_count': len(budget['expenses'])
        }
    
    # ==================== Utility Methods ====================
    
    def search_recipients(self, query: str) -> List[Dict[str, Any]]:
        """Search recipients by name or interests."""
        query_lower = query.lower()
        results = []
        
        for recipient in self.state['recipients'].values():
            # Check name
            if query_lower in recipient['name'].lower():
                results.append(recipient)
                continue
            
            # Check interests
            if any(query_lower in interest.lower() for interest in recipient['interests']):
                results.append(recipient)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        return {
            'total_recipients': len(self.state['recipients']),
            'total_occasions': len(self.state['occasions']),
            'upcoming_occasions': len(self.get_upcoming_occasions(30)),
            'total_budget': self.state['budget']['total'],
            'total_spent': self.state['budget']['spent']
        }
