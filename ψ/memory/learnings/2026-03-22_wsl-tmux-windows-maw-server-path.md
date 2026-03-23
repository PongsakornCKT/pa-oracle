# WSL tmux, Windows tmux, and maw server path separation

**Date**: 2026-03-22
**Tags**: tmux, wsl, maw-js, windows, multi-agent, infrastructure

## Pattern

1. **WSL tmux ≠ Windows tmux** — maw server ใช้ WSL tmux เสมอ ถ้า `curl localhost:4000/api/sessions` ตอบ sessions แต่ `tmux list-sessions` ว่าง → ใช้ `wsl tmux` แทน

2. **maw server runs from /tmp/maw-js-server** — ไม่ใช่จาก repo ตรง rebuild office แล้วต้อง copy ไฟล์ไปที่ `/tmp/maw-js-server/dist-office/` ด้วย

3. **Duplicate imports = silent route failure** — Bun ไม่ crash จาก duplicate import แต่ routes ที่ define หลังจุดนั้นอาจไม่ถูก register (404 เงียบๆ)

4. **Gemini CLI busy detection** — ต้องเพิ่ม `gemini` ใน regex `/claude|codex|node|gemini/i` ทุกจุดใน maw-js (engine.ts, handlers.ts, comm.ts, talk-to.ts)

## Impact

เสียเวลา ~15 นาทีจากการไม่รู้ว่า tmux อยู่ใน WSL และ server path แยกจาก repo
