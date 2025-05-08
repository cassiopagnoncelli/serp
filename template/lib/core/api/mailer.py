from fastapi import APIRouter, HTTPException, Query, Depends
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Mailer API"])

# Initialize Jinja2 environment
template_dir = Path("app/emails")
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=True
)

@router.get("/mailer/{template_name}", response_class=HTMLResponse, include_in_schema=False)
async def mailer(template_name: str):
    # Construct the full template name with extension
    template_path = f"{template_name}.jinja2"
    
    # Check if template exists
    if not (template_dir / template_path).exists():
        raise HTTPException(
            status_code=404,
            detail=f"Template {template_name} not found"
        )
    
    try:
        # Load and render the template
        template = env.get_template(template_path)
        rendered_html = template.render()
        
        return rendered_html
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error rendering template: {str(e)}"
        )
