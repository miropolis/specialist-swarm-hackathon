import json
import re
from html.parser import HTMLParser
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / ".state"
OUTPUT_DIR = BASE_DIR / "outputs"
BETA = "managed-agents-2026-04-01"


def make_client() -> Anthropic:
    load_dotenv(BASE_DIR.parent / ".env")
    return Anthropic(default_headers={"anthropic-beta": BETA})


def read_state(name: str) -> dict:
    path = STATE_DIR / f"{name}.json"
    if not path.exists():
        raise ValueError(f"Missing {path.name}. Run setup_demo.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(name: str, value: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    (STATE_DIR / f"{name}.json").write_text(
        json.dumps(value, indent=2), encoding="utf-8"
    )


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self.tags.add(tag)
        if tag in {"script", "iframe", "object", "embed", "form", "base", "link"}:
            raise ValueError(f"Report must be standalone static HTML; found {tag}.")
        for name, value in attrs:
            if name.startswith("on") or name in {"srcdoc", "action"}:
                raise ValueError(f"Active HTML attribute is not allowed: {name}.")
            if value and re.match(r"\s*(javascript|vbscript|data):", value, re.I):
                raise ValueError("Executable or embedded data URLs are not allowed.")
        if tag == "meta" and dict(attrs).get("http-equiv", "").lower() == "refresh":
            raise ValueError("Report must not redirect the browser.")

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.handle_starttag(tag, attrs)


def extract_html(text: str) -> str:
    matches = list(re.finditer(r"<!doctype\s+html\s*>.*?</html\s*>", text, re.I | re.S))
    if not matches:
        raise ValueError("Coordinator did not return a complete HTML document.")
    document = matches[-1].group(0)
    parser = ReportParser()
    parser.feed(document)
    parser.close()
    if not {"html", "head", "title", "style", "body"}.issubset(parser.tags):
        raise ValueError("Report is missing required HTML structure or inline styling.")
    if not re.search(r"</body\s*>\s*</html\s*>$", document, re.I):
        raise ValueError("Report body was truncated.")
    return document + "\n"


def save_report(text: str, output_dir: Path = OUTPUT_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "coordinator-transcript.txt").write_text(text, encoding="utf-8")
    document = extract_html(text)
    target = output_dir / "emergency-plan.html"
    temporary = target.with_suffix(".html.tmp")
    temporary.write_text(document, encoding="utf-8")
    temporary.replace(target)
    return target