# AGENTS-github-copilot.md — GitHub Copilot-Specific Instructions

In addition to the common Permanent Operating Reminders in
[AGENTS.md](AGENTS.md), the following instructions apply specifically
when running under GitHub Copilot (VS Code / JetBrains / CLI). For the
skills table, see [`AGENTS-legacy.md`](AGENTS-legacy.md).

1. **Prefer Bash heredocs over the editor `edit` AND `create` tools for large writes.**
   Both `edit` and `create` hang on large / many-line operations (the
   `create` tool stresses the IDE renderer the same way `edit` does when
   `file_text` is large — empirically anything > ~10 KB or > ~100 lines).
   For whole-file authoring use `cat > file <<'EOF' ... EOF`; for in-place
   transforms use `python3 - <<'PY' ... PY`. The `edit` tool is reserved
   for small, uniquely-anchored surgical replacements; the `create` tool
   is reserved for short new files (< 10 KB / < 100 lines). See
   [`ai-agent-rules/shell-execution-rules.md` §2.3.2](ai-agent-rules/shell-execution-rules.md).
