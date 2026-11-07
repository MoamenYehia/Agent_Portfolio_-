from services.tools.kb_search import search_portfolio_kb
from services.tools.skill_tool import filter_projects_by_skill

# Export as a list for easy agent binding
portfolio_tools = [
    search_portfolio_kb,
    filter_projects_by_skill
]

__all__ = ["search_portfolio_kb", "filter_projects_by_skill", "portfolio_tools"]