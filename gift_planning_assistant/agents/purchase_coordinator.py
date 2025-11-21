"""
Purchase Coordinator Agent - Finds best prices and purchase links.
"""

from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)


class PurchaseCoordinatorAgent:
    """
    Agent responsible for finding purchase options and comparing prices.
    Uses Google Search to find products and prices.
    """
    
    def __init__(self, model: genai.Client):
        """
        Initialize the Purchase Coordinator Agent.
        
        Args:
            model: Gemini model client
        """
        self.model = model
        self.name = "PurchaseCoordinator"
        
        self.system_instruction = """You are a Purchase Coordinator for a gift planning system.

Your responsibilities:
- Search for product availability
- Compare prices across different retailers
- Provide purchase links
- Find the best deals
- Check product reviews when available
- Suggest reliable sellers

When searching for products:
1. Find multiple retailers for comparison
2. Include price information
3. Note any sales or discounts
4. Check shipping options
5. Provide direct purchase links when possible
6. Warn about unreliable sellers

For each product option, provide:
- Product name and description
- Price
- Retailer name
- Direct link (if available)
- Shipping information
- Any special notes (sale, limited stock, etc.)

Help users find the best deals!
"""
    
    def process(self, user_message: str, product_name: str = None, context: dict = None) -> dict:
        """
        Process purchase coordination request.
        
        Args:
            user_message: User's message
            product_name: Optional product name to search
            context: Additional context
            
        Returns:
            Response with purchase options
        """
        try:
            search_query = user_message
            if product_name:
                search_query = f"Find where to buy: {product_name}"
            
            # Create prompt
            prompt = f"""{self.system_instruction}

User request: {search_query}

Search for the product and provide detailed purchase options with prices and links."""
            
            # Use Google Search tool
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
                'product': product_name,
                'message': response.text
            }
            
        except Exception as e:
            logger.error(f"PurchaseCoordinator error: {e}")
            # Fallback without search
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
                logger.error(f"PurchaseCoordinator fallback error: {e2}")
                return {
                    'success': False,
                    'agent': self.name,
                    'error': str(e2),
                    'message': f"Sorry, I couldn't find purchase options: {e2}"
                }
    
    def compare_prices(self, product_name: str) -> dict:
        """
        Compare prices for a specific product.
        
        Args:
            product_name: Name of product
            
        Returns:
            Price comparison results
        """
        message = f"Compare prices for: {product_name}. Find at least 3 different retailers."
        return self.process(message, product_name=product_name)
