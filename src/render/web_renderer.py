from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_web_html(issue):
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    tpl = env.get_template("web_newsletter.html.j2")
    return tpl.render(issue=issue)
