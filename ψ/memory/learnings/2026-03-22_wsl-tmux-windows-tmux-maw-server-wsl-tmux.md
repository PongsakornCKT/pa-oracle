---
title: WSL tmux ≠ Windows tmux — maw server ใช้ WSL tmux เสมอ. ถ้า maw API ตอบ sessions
tags: [tmux, wsl, maw-js, gemini, windows, multi-agent, infrastructure, bun]
created: 2026-03-22
source: rrr: pa-Oracle v2
---

# WSL tmux ≠ Windows tmux — maw server ใช้ WSL tmux เสมอ. ถ้า maw API ตอบ sessions

WSL tmux ≠ Windows tmux — maw server ใช้ WSL tmux เสมอ. ถ้า maw API ตอบ sessions แต่ local tmux ว่าง → ใช้ `wsl tmux` แทน. maw server runs from /tmp/maw-js-server ไม่ใช่จาก repo ตรง — rebuild แล้วต้อง copy ไป. Duplicate imports ใน Bun = silent route failure (404 เงียบๆ). Gemini CLI busy detection ต้องเพิ่ม `gemini` ใน regex ทุกจุดใน maw-js.

---
*Added via Oracle Learn*
