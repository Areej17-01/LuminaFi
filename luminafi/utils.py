import re
import streamlit as st

def sanitize_markdown(md: str) -> str:
    """Remove incomplete HTML tags and trailing partial markdown to prevent UI breakage."""
    # Remove any trailing unclosed <div> or <span> tags
    md = re.sub(r'<[^>]*$', '', md)
    # Optionally, close unclosed <div> tags (simple heuristic)
    open_divs = md.count('<div')
    close_divs = md.count('</div>')
    for _ in range(open_divs - close_divs):
        md += '</div>'
    return md 