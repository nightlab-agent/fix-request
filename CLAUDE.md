# fix-request: notes for whoever works on this repo

Read this, then `00-catalog/CATALOG.md`, then only what it points to.

This repo holds one GitHub issue form, "Fix request", and its README. A stranger
fills in the form to ask for a fix to one fault in their own public tool. Rules: one form only, blank issues stay off, the terms at the top of the form
stay word for word, the price appears once in the form and never in the README,
and the form and the README each say plainly that the work is AI-written.
`tests/check_form.py` checks those (for AI-written, only that the words "AI
agent" and "written by AI" appear); run it before every push.
