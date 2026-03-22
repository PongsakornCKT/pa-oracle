# Claude Code TUI Cannot Be Automated via tmux

**Date**: 2026-03-22
**Source**: rrr: pa-Oracle-v2
**Tags**: claude-code, tmux, automation, tui, ink

## Lesson

Claude Code's interactive prompts (trust folder, bypass permissions) use Ink (React-based TUI) which does NOT accept standard terminal input via `tmux send-keys`. Tried: Down arrow, Tab, number keys, ANSI escapes, `yes` pipe — none work.

## Workarounds

1. **`-p` flag** — skips trust dialog (print mode). Run `claude -p "echo trusted" --dangerously-skip-permissions` first to mark folder as trusted
2. **`skipDangerousModePermissionPrompt: true`** — in `~/.claude/settings.json` (version-dependent)
3. **Manual accept** — `tmux attach -t agent` then accept, `Ctrl+B D` to detach

## Takeaway

Some security prompts are intentionally manual. Don't fight it — design startup scripts to handle the parts that CAN be automated, and leave explicit manual steps for the rest.
