"""
Gift Planning Assistant - ADK compliant entry point.

This module exposes `root_agent`, the object consumed by the ADK runtime.
It wires custom FunctionTools around the domain logic so that every response
is grounded in explicit tool calls that show up in the ADK trace UI.
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional

# Ensure package imports resolve when ADK loads this module directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google import genai
from google.adk import Agent
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.tool_context import ToolContext

from config import GEMINI_API_KEY, MODEL_NAME, validate_config
from memory import MemoryManager
from tools import budget_calculator, date_calculator
from agents import (
    BudgetManagerAgent,
    GiftFinderAgent,
    OccasionTrackerAgent,
    PurchaseCoordinatorAgent,
    RecipientManagerAgent,
)

# ---------------------------------------------------------------------------
# Shared resources
# ---------------------------------------------------------------------------

# Store state in the user namespace so it persists across turns per ADK session.
APP_STATE_KEY = "user:gift_planning_assistant"

validate_config()
_CLIENT = genai.Client(api_key=GEMINI_API_KEY)


def _get_memory_manager(tool_context: ToolContext) -> MemoryManager:
    """Return a MemoryManager scoped to the ADK session state."""
    if tool_context is None:
        raise ValueError("tool_context is required for stateful tools")

    session_bucket = tool_context.state.setdefault(APP_STATE_KEY, {})
    return MemoryManager(session_bucket)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def add_recipient_profile(
    name: str,
    age: Optional[int] = None,
    interests: Optional[List[str]] = None,
    relationship: Optional[str] = None,
    preferred_style: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Create or update a recipient profile in memory.

    Use this whenever the user shares details about a new recipient (name
    required, other attributes optional). Provide interests and budget info
    when available so downstream agents can personalise gift ideas.
    """
    memory = _get_memory_manager(tool_context)
    recipient_agent = RecipientManagerAgent(_CLIENT, memory)

    budget_range = None
    if min_budget is not None and max_budget is not None:
        budget_range = (float(min_budget), float(max_budget))

    return recipient_agent.add_recipient_direct(
        name=name,
        age=age,
        interests=interests or [],
        relationship=relationship,
        budget_range=budget_range,
        style=preferred_style,
    )


def list_recipients(
    name_filter: Optional[str] = None,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Retrieve the set of known recipients.

    Use when you need to reference stored profiles or confirm whether someone
    already exists before adding new information.
    """
    memory = _get_memory_manager(tool_context)
    recipients = memory.get_all_recipients()

    if name_filter:
        name_filter_lower = name_filter.lower()
        recipients = [
            r for r in recipients if name_filter_lower in r["name"].lower()
        ]

    return {"success": True, "count": len(recipients), "recipients": recipients}


def add_occasion_for_recipient(
    recipient_name: str,
    occasion_type: str,
    date: str,
    reminder_days_before: int = 14,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Attach a dated occasion to an existing recipient.

    Invoke this after the user supplies an occasion type and date so reminders
    and gift planning timelines stay accurate.
    """
    memory = _get_memory_manager(tool_context)
    occasion_agent = OccasionTrackerAgent(_CLIENT, memory, date_calculator)
    return occasion_agent.add_occasion_direct(
        recipient_name=recipient_name,
        occasion_type=occasion_type,
        date=date,
        reminder_days_before=reminder_days_before,
    )


def list_upcoming_occasions(
    days_ahead: int = 30,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    View upcoming occasions within a time window.

    Use this to summarise what events are approaching so the user knows where
    to focus gift planning energy next.
    """
    memory = _get_memory_manager(tool_context)
    occasion_agent = OccasionTrackerAgent(_CLIENT, memory, date_calculator)
    return occasion_agent.get_upcoming(days_ahead=days_ahead)


def calculate_days_until_event(
    date: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Calculate how many days remain until a specific date.

    Helpful for quick reminders without mutating any state.
    """
    _ = tool_context  # context not needed but kept for consistent signature
    return date_calculator.calculate_days_until(date)


def set_total_budget(
    total_budget: float,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Set or update the overall gift budget.

    Call this when the user defines how much they plan to spend across all
    recipients.
    """
    memory = _get_memory_manager(tool_context)
    budget_agent = BudgetManagerAgent(_CLIENT, memory, budget_calculator)
    return budget_agent.set_budget(total_budget)


def record_gift_expense(
    recipient_name: str,
    amount: float,
    description: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Log a specific gift purchase against the budget.

    Use when the user confirms they bought something so spending stays in sync.
    """
    memory = _get_memory_manager(tool_context)
    budget_agent = BudgetManagerAgent(_CLIENT, memory, budget_calculator)
    return budget_agent.add_expense(
        recipient_name=recipient_name,
        amount=amount,
        description=description,
    )


def get_budget_status(
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Summarise the budget health (total, spent, remaining, alerts).

    Use this before recommending expensive items or whenever the user asks
    about spending progress.
    """
    memory = _get_memory_manager(tool_context)
    budget_agent = BudgetManagerAgent(_CLIENT, memory, budget_calculator)
    return budget_agent.get_budget_status()


def generate_gift_ideas(
    request: str,
    recipient_name: Optional[str] = None,
    max_price: Optional[float] = None,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Brainstorm gift suggestions using stored context plus optional criteria.

    Provide the free-form user ask in `request`. Include `recipient_name` or
    `max_price` when available so the reasoning can stay targeted.
    """
    memory = _get_memory_manager(tool_context)
    gift_agent = GiftFinderAgent(_CLIENT, memory)

    enriched_request = request
    if recipient_name:
        enriched_request = f"{request}\nRecipient: {recipient_name}"
    if max_price is not None:
        enriched_request = f"{enriched_request}\nBudget ceiling: ${max_price:.2f}"

    result = gift_agent.process(enriched_request, recipient_name=recipient_name)
    return {
        "success": result.get("success", False),
        "recipient": recipient_name,
        "ideas": result.get("response"),
        "message": result.get("message"),
    }


def find_purchase_options(
    product_description: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """
    Search for retailers, prices, and links for a product idea.

    Use this after a gift concept is chosen so the user can complete the
    purchase with confidence.
    """
    purchase_agent = PurchaseCoordinatorAgent(_CLIENT)
    result = purchase_agent.process(product_description)
    return {
        "success": result.get("success", False),
        "product": product_description,
        "options": result.get("response"),
        "message": result.get("message"),
    }


# ---------------------------------------------------------------------------
# Root agent wiring
# ---------------------------------------------------------------------------

CUSTOM_TOOLS = [
    FunctionTool(add_recipient_profile),
    FunctionTool(list_recipients),
    FunctionTool(add_occasion_for_recipient),
    FunctionTool(list_upcoming_occasions),
    FunctionTool(calculate_days_until_event),
    FunctionTool(set_total_budget),
    FunctionTool(record_gift_expense),
    FunctionTool(get_budget_status),
    FunctionTool(generate_gift_ideas),
    FunctionTool(find_purchase_options),
]

root_agent = Agent(
    model=MODEL_NAME,
    name="GiftPlanningAssistant",
    description="Coordinates gift planning by managing recipients, occasions, budgets, and purchases",
    instruction="""
You are the Gift Planning Assistant.

Always ground your answers by calling the provided tools:
1. Use add_recipient_profile/list_recipients to manage recipient data.
2. Use add_occasion_for_recipient/list_upcoming_occasions/calculate_days_until_event for scheduling questions.
3. Use set_total_budget/record_gift_expense/get_budget_status before giving financial advice.
4. Use generate_gift_ideas to produce tailored gift suggestions.
5. Use find_purchase_options (and optionally Google Search) to surface prices and links.

Never invent data that is available via a tool call. Summarise tool results clearly,
and guide the user through next best actions in their gift planning workflow.
""".strip(),
    tools=CUSTOM_TOOLS + [GoogleSearchTool(bypass_multi_tools_limit=True)],
)

__all__ = ["root_agent"]
