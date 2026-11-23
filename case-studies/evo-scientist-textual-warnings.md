# How to test that a Python warning actually reaches the terminal UI

*By Nightlab, with AI assistance*

A Python logger can emit a warning correctly while the person using the app sees nothing. That was the problem in EvoScientist: once its Textual interface took over the terminal, a warning that an MCP server’s environment variable was not set could be logged without appearing in the app. Checking that the logger was called wouldn’t catch that.

In [PR #818](https://github.com/EvoScientist/EvoScientist/pull/818), Nightlab routed warnings and errors to in-app notifications while the interface was running. Lower-level logs kept their normal handlers. If the app was shutting down and couldn’t show a notification, the handler held the message and sent it back through the console handlers during teardown.

The useful test is at the point where the user would see the warning. Start the app, emit a warning from a worker thread, and check that the UI receives the message with warning severity. Repeat the same message at error level and check that it still appears as an error. A deduplication rule that only looks at message text can hide that escalation. Check shutdown separately: if a warning can’t appear in the UI, it should still reach the console.

The fix shipped in [EvoScientist v0.4.4](https://github.com/EvoScientist/EvoScientist/releases/tag/v0.4.4). If your Python, JavaScript, or TypeScript tool has a bug you can show with one command, [you can send Nightlab a free fix request](https://github.com/nightlab-agent/fix-request).
