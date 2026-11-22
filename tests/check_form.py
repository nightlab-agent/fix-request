"""Check the fix-request issue form, its config and the README.

Run from the repository root: python3 tests/check_form.py
Exits 0 when every check passes, 1 with one line per failure otherwise.
"""
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML is needed (pip install pyyaml)")
    sys.exit(1)

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / ".github" / "ISSUE_TEMPLATE"
FORM = TEMPLATES / "fix-request.yml"
CONFIG = TEMPLATES / "config.yml"
README = ROOT / "README.md"

TERMS = (
    "Send the command that fails and what you expected. "
    "If the job fits, Nightlab will confirm the $49 price with you in writing. "
    "Payment is due after we open a pull request with the fix, a regression test, "
    "and instructions for checking it."
)
REQUIRED_IDS = ["repo", "version", "command", "expected", "actual", "environment"]
FIELD_TYPES = {
    "repo": "input",
    "version": "input",
    "command": "textarea",
    "expected": "textarea",
    "actual": "textarea",
    "environment": "input",
    "issue": "input",
    "confirm": "checkboxes",
}
CREDIT = (
    "Built and maintained by Nightlab, an AI agent created by xnfinite "
    "([@xnfinite](https://github.com/xnfinite))."
)
PROCESS_WORDS = ["gate", "door", "tray", "ledger", "falsifier", "kill date", "morty", "floor"]

failures = []


def check(ok, message):
    if not ok:
        failures.append(message)


def load(path):
    text = path.read_text(encoding="utf-8")
    check(text.isascii(), f"{path.name} has non-ASCII characters")
    return text, yaml.safe_load(text)


form_text, form = load(FORM)
config_text, config = load(CONFIG)
readme = README.read_text(encoding="utf-8")

# One form, blank issues off.
others = sorted(p.name for p in TEMPLATES.iterdir() if p.name not in ("fix-request.yml", "config.yml"))
check(not others, f"other files in ISSUE_TEMPLATE: {others}")
check(config.get("blank_issues_enabled") is False, "config.yml does not turn blank issues off")

# The form's own shape.
check(form.get("name") == "Fix request", "form name is not 'Fix request'")
check(form.get("description"), "form has no description")
body = form.get("body") or []
check(body and body[0].get("type") == "markdown", "form does not start with a markdown block")
top = body[0].get("attributes", {}).get("value", "") if body else ""
check(top.startswith(TERMS), "the terms are not word for word at the top of the form")
check(form_text.count("$49") == 1, "the price must appear once in the form, in the terms")
check("AI agent" in top and "written by AI" in top, "the form does not say plainly it is AI-written")
check("free" in top, "the form does not say it is free to submit")

fields = [item for item in body if item.get("type") != "markdown"]
ids = [item.get("id") for item in fields]
check(len(ids) == len(set(ids)), f"duplicate field ids: {ids}")
labels = [item.get("attributes", {}).get("label") for item in fields]
check(len(labels) == len(set(labels)), f"duplicate field labels: {labels}")
by_id = {item.get("id"): item for item in fields}
# Check this form's field layout, not the complete GitHub schema.
for field_id, field_type in FIELD_TYPES.items():
    check(by_id.get(field_id, {}).get("type") == field_type,
          f"field '{field_id}' is missing or is not {field_type}")
for item in body:
    if "render" in item.get("attributes", {}):
        check(item.get("type") == "textarea", "render is only allowed on textarea fields")
for field_id in REQUIRED_IDS:
    item = by_id.get(field_id)
    check(item is not None, f"field '{field_id}' is missing")
    if item is not None:
        check((item.get("validations") or {}).get("required") is True, f"field '{field_id}' is not required")

# The repository address: a one-line input, asked for as github.com/owner/repo.
repo = by_id.get("repo", {})
check(repo.get("type") == "input", "the repository field is not a one-line input")
check(repo.get("attributes", {}).get("placeholder") == "github.com/owner/repo", "repository placeholder is not github.com/owner/repo")
check("github.com/owner/repo" in repo.get("attributes", {}).get("description", ""), "repository field does not say the form to write it in")
check(ids and ids[0] == "repo", "the repository field is not the first field")

confirm_options = by_id.get("confirm", {}).get("attributes", {}).get("options", [])
check(len(confirm_options) == 3, "confirm must have all three acknowledgement checkboxes")
for item in fields:
    if item.get("type") == "checkboxes":
        for option in item.get("attributes", {}).get("options", []):
            check(option.get("required") is True, f"checkbox not required: {option.get('label')}")

# The README: the form linked, no price, the credit line, plain words.
check("issues/new?template=fix-request.yml" in readme, "README does not link to the form")
check(not re.search(r"\$\s*\d|\b49\b|USD|dollar", readme, re.IGNORECASE), "README names a price")
check(CREDIT in readme, "README lacks the credit line")
check("AI agent" in readme and "written by AI" in readme, "README does not say plainly it is AI-written")
check(readme.isascii(), "README has non-ASCII characters")
for text, name in ((readme, "README"), (form_text, "form")):
    for word in PROCESS_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            failures.append(f"{name} uses the word '{word}'")

if failures:
    for line in failures:
        print("FAIL:", line)
    sys.exit(1)
print(f"ok: form with {len(fields)} fields, {len(REQUIRED_IDS)} required, blank issues off, README checked")
