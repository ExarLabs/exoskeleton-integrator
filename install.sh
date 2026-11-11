#!/usr/bin/env bash
# Install Exoskeleton Integrator into a Frappe app repository.
#
#   ./install.sh /path/to/your-frappe-app
#
# Copies, without overwriting anything that already exists:
#   - the AI Dev Exoskeleton payload (upstream/ai-dev-exoskeleton): .ai-dev-exoskeleton/,
#     AGENTS.md, CLAUDE.md, GEMINI.md
#   - the Frappe layer: docs/context/FRAPPE.md, GOTCHAS-frappe.md, SAFE_EXEC-frappe.md,
#     TESTING-frappe.md, REVIEW-frappe.md, overrides/PROPOSED-implementer.md
#   - the scripts: .exoskeleton-integrator/scripts/
# Files that already exist are listed as skipped; compare them by hand.
set -euo pipefail

if [ "$#" -ne 1 ] || [ ! -d "$1" ]; then
  echo "usage: $0 /path/to/frappe-app-repo" >&2
  exit 1
fi

here="$(cd "$(dirname "$0")" && pwd)"
target="$(cd "$1" && pwd)"
copied=0
skipped=0

place() {
  local src="$1" dst="$2"
  if [ -e "$dst" ]; then
    echo "skip (exists): ${dst#"$target"/}"
    skipped=$((skipped + 1))
  else
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    copied=$((copied + 1))
  fi
}

copy_tree() {
  local src_root="$1" dst_root="$2" rel
  while IFS= read -r -d '' file; do
    rel="${file#"$src_root"/}"
    place "$file" "$dst_root/$rel"
  done < <(find "$src_root" -type f -print0)
}

up="$here/upstream/ai-dev-exoskeleton"
copy_tree "$up/.ai-dev-exoskeleton" "$target/.ai-dev-exoskeleton"
for f in AGENTS.md CLAUDE.md GEMINI.md; do
  place "$up/$f" "$target/$f"
done

copy_tree "$here/frappe-layer/docs/context" "$target/docs/context"

for f in safe_exec_names.py triage_console.py triage_rest.py; do
  place "$here/scripts/$f" "$target/.exoskeleton-integrator/scripts/$f"
done
place "$here/VERSION" "$target/.exoskeleton-integrator/VERSION"

echo "copied $copied file(s), skipped $skipped."
cat <<'NEXT'

Next steps:
  1. Run the Exoskeleton onboarding:
     .ai-dev-exoskeleton/guides/workflows/new-project-onboarding.md
  2. Add a row for docs/context/FRAPPE.md to docs/context/README.md (the index onboarding writes).
  3. Claude Code users: install the hooks plugin
     /plugin marketplace add ExarLabs/exoskeleton-integrator
     /plugin install exoskeleton-integrator@exarlabs
NEXT
