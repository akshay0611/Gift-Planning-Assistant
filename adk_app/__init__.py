"""
ADK application entry module.

Re-exports the root agent defined in `gift_planning_assistant.agent` so that
`adk run` and `adk web` can discover it using the conventional `adk_app`
package.
"""

from gift_planning_assistant.agent import root_agent

__all__ = ["root_agent"]

