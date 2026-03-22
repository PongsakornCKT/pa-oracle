---
title: Marathon sessions (8-14h) that create many files but only commit once at the end
tags: [git, marathon-sessions, nothing-is-deleted, commit-safety, data-loss]
created: 2026-03-22
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# Marathon sessions (8-14h) that create many files but only commit once at the end

Marathon sessions (8-14h) that create many files but only commit once at the end risk losing work. KnowledgeMap.tsx and DashboardView.tsx were both created during a marathon but never committed — KnowledgeMap was completely lost, DashboardView only survived in WSL /tmp. "Nothing is Deleted" only applies to what's committed. Uncommitted work IS deleted. Commit incrementally during long sessions, not just at the end. Deploy scripts should also create checkpoint commits.

---
*Added via Oracle Learn*
