import subprocess
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import tempfile

def render_contract_to_pdf(context, template_name):
    env = Environment(loader=FileSystemLoader('document/templates/latex'))
    template = env.get_template(template_name)
    rendered_tex = template.render(context)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "document.tex"
        pdf_path = Path(tmpdir) / "document.pdf"

        tex_path.write_text(rendered_tex, encoding="utf-8")

        process = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        print("XELATEX STDOUT:\n", process.stdout)
        print("XELATEX STDERR:\n", process.stderr)

        if process.returncode != 0:
            raise RuntimeError(f"xelatex failed with code {process.returncode}")

        if pdf_path.exists():
            return pdf_path.read_bytes()

    return None