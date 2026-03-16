from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_issue(issue, template_name: str, out_path: str):
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"])
    )
    tpl = env.get_template(template_name)
    html = tpl.render(issue=issue)
    Path(out_path).write_text(html, encoding="utf-8")
    return html
