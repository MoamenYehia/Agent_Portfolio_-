import json
from pathlib import Path
from langchain_core.tools import tool

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECTS_JSON_PATH = BASE_DIR / "projects.json"

@tool
def filter_projects_by_skill(skill: str) -> str:
    """Finds and lists all projects where a specific technology, language, or framework 
    (e.g., 'PyTorch', 'FastAPI', 'LangChain', 'OpenCV', 'React', 'Power BI') was used.
    Use this when the user asks to see or list projects built with a specific tech stack or skill."""
    if not PROJECTS_JSON_PATH.exists():
        return f"Error: Metadata file '{PROJECTS_JSON_PATH.name}' not found."

    try:
        with open(PROJECTS_JSON_PATH, "r", encoding="utf-8") as f:
            projects = json.load(f)
    except Exception as e:
        return f"Error reading project metadata: {str(e)}"

    skill_query = skill.lower().strip()
    matching_projects = []

    for p_id, p_info in projects.items():
        # Case-insensitive comparison against tech stack list
        stack = [tech.lower() for tech in p_info.get("tech_stack", [])]
        if any(skill_query in tech for tech in stack):
            title = p_info.get("title", p_id)
            summary = p_info.get("summary", "")
            github = p_info.get("github_url", "N/A")
            techs = ", ".join(p_info.get("tech_stack", []))
            
            matching_projects.append(
                f"• **{title}**\n"
                f"  - **Summary:** {summary}\n"
                f"  - **Tech Stack:** {techs}\n"
                f"  - **GitHub:** {github}"
            )

    if not matching_projects:
        return f"No projects found matching the skill or technology '{skill}'."

    return f"Projects built with **{skill}**:\n\n" + "\n\n".join(matching_projects)