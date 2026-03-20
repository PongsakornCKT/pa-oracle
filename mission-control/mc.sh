#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Mission Control — pa Oracle 𓂀
# "ทุก keystroke ที่ไม่จำเป็นคือ distraction"
# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Convert to Windows path for Python compatibility
PROJECTS_FILE_WIN="$(cygpath -w "$SCRIPT_DIR/projects.json" 2>/dev/null || echo "$SCRIPT_DIR/projects.json")"
PROJECTS_FILE="$SCRIPT_DIR/projects.json"
MC_VERSION="1.0.0"
export PYTHONIOENCODING=utf-8

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

show_banner() {
    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║     𓂀  Mission Control  v${MC_VERSION}      ║"
    echo "  ║     pa Oracle — Eye of Ma'at          ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

show_help() {
    echo -e "${BOLD}Usage:${NC}"
    echo "  mc              Show dashboard (project list)"
    echo "  mc [number]     Jump to project by number"
    echo "  mc add          Add new project interactively"
    echo "  mc remove [id]  Remove project by ID"
    echo "  mc status       Show all project statuses"
    echo ""
    echo -e "${DIM}ปรัชญา: กด 1 ครั้ง ได้ทำเลย${NC}"
}

# Parse projects from JSON (portable — no jq required)
get_projects() {
    python3 -c "
import json, sys
with open(r'$PROJECTS_FILE_WIN', encoding='utf-8') as f:
    data = json.load(f)
for p in data['projects']:
    print(f\"{p['id']}|{p['name']}|{p['path']}|{p['description']}|{p['status']}\")
" 2>/dev/null || python -c "
import json, sys
with open(r'$PROJECTS_FILE_WIN', encoding='utf-8') as f:
    data = json.load(f)
for p in data['projects']:
    print('{0}|{1}|{2}|{3}|{4}'.format(p['id'], p['name'], p['path'], p['description'], p['status']))
"
}

show_dashboard() {
    show_banner
    echo -e "${BOLD}  #   Project                Status${NC}"
    echo "  ─── ────────────────────── ──────"

    get_projects | while IFS='|' read -r id name path desc status; do
        case "$status" in
            active)   status_icon="${GREEN}●${NC}" ;;
            paused)   status_icon="${YELLOW}◐${NC}" ;;
            archived) status_icon="${DIM}○${NC}" ;;
            *)        status_icon="${RED}?${NC}" ;;
        esac
        printf "  ${CYAN}%s${NC}  %-24s %b %s\n" "$id" "$name" "$status_icon" "$desc"
    done

    echo ""
    echo -e "${DIM}  Type: mc [number] to jump │ mc add to register │ mc --help${NC}"
}

jump_to_project() {
    local target_id="$1"
    local target_path=""

    target_path=$(get_projects | while IFS='|' read -r id name path desc status; do
        if [ "$id" = "$target_id" ] || [ "$name" = "$target_id" ]; then
            echo "$path"
            break
        fi
    done)

    if [ -z "$target_path" ]; then
        echo -e "${RED}Project '$target_id' not found.${NC}"
        echo "Use 'mc' to see available projects."
        return 1
    fi

    # Convert Windows path to Unix path for Git Bash
    local unix_path
    unix_path=$(echo "$target_path" | sed 's|\\|/|g' | sed 's|^\([A-Z]\):|/\L\1|')

    if [ -d "$unix_path" ]; then
        cd "$unix_path" || return 1
        echo -e "${GREEN}➜${NC} Jumped to: ${BOLD}$unix_path${NC}"
        echo -e "${DIM}  Ready. Type 'claude' to start Oracle session.${NC}"
    else
        echo -e "${RED}Directory not found: $unix_path${NC}"
        return 1
    fi
}

add_project() {
    echo -e "${BOLD}Add new project to Mission Control${NC}"
    echo ""

    # Get next ID
    local max_id
    max_id=$(get_projects | tail -1 | cut -d'|' -f1)
    local next_id
    next_id=$(printf "%02d" $((10#$max_id + 1)))

    read -p "  Project name: " proj_name
    read -p "  Path: " proj_path
    read -p "  Description: " proj_desc
    read -p "  Oracle name (or blank): " proj_oracle

    [ -z "$proj_oracle" ] && proj_oracle="none"

    python3 -c "
import json
with open(r'$PROJECTS_FILE_WIN', 'r', encoding='utf-8') as f:
    data = json.load(f)
data['projects'].append({
    'id': '$next_id',
    'name': '$proj_name',
    'path': r'$proj_path',
    'description': '$proj_desc',
    'oracle': '$proj_oracle',
    'status': 'active'
})
with open(r'$PROJECTS_FILE_WIN', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print('Done!')
" 2>/dev/null && echo -e "${GREEN}Added: [$next_id] $proj_name${NC}" || echo -e "${RED}Failed to add project${NC}"
}

show_status() {
    show_banner
    echo -e "${BOLD}  Project Status Report${NC}"
    echo "  ═════════════════════"
    echo ""

    get_projects | while IFS='|' read -r id name path desc status; do
        local unix_path
        unix_path=$(echo "$path" | sed 's|\\|/|g' | sed 's|^\([A-Z]\):|/\L\1|')

        echo -e "  ${CYAN}[$id]${NC} ${BOLD}$name${NC}"
        echo -e "       Path: $unix_path"

        # Check git status if it's a git repo
        if [ -d "$unix_path/.git" ]; then
            local branch
            branch=$(git -C "$unix_path" branch --show-current 2>/dev/null)
            local changes
            changes=$(git -C "$unix_path" status --porcelain 2>/dev/null | wc -l)
            echo -e "       Git:  ${GREEN}$branch${NC} (${changes} changes)"
        fi

        # Check if CLAUDE.md exists (is it an Oracle?)
        if [ -f "$unix_path/CLAUDE.md" ]; then
            echo -e "       Oracle: ${GREEN}yes${NC} 𓂀"
        else
            echo -e "       Oracle: ${DIM}no${NC}"
        fi
        echo ""
    done
}

# ─── Main ─────────────────────────────────────────────────────

case "${1:-}" in
    ""|"dashboard"|"list")
        show_dashboard
        ;;
    "add")
        add_project
        ;;
    "remove"|"rm")
        echo "Remove project: not yet implemented (Nothing is Deleted — archive instead)"
        ;;
    "status"|"s")
        show_status
        ;;
    "--help"|"-h"|"help")
        show_banner
        show_help
        ;;
    *)
        # Try to jump to project by number or name
        jump_to_project "$1"
        ;;
esac
