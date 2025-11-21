"""Compatibility shim so ADK can import `adk_app.agent.root_agent`."""

from gift_planning_assistant.agent import root_agent

__all__ = ["root_agent"]

