#!/bin/bash
# Build script to package skills as ZIP files for distribution
# Usage: ./build.sh [skill-name]  - build specific skill
#        ./build.sh               - build all skills

set -e

SKILLS_DIR="skills"
DIST_DIR="dist"

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

package_skill() {
    local skill_name="$1"
    local skill_path="$SKILLS_DIR/$skill_name"

    if [ ! -d "$skill_path" ]; then
        echo "Error: Skill '$skill_name' not found in $SKILLS_DIR/"
        return 1
    fi

    if [ ! -f "$skill_path/SKILL.md" ]; then
        echo "Error: SKILL.md not found in $skill_path/"
        return 1
    fi

    # Validate frontmatter exists
    if ! head -1 "$skill_path/SKILL.md" | grep -q "^---$"; then
        echo "Error: SKILL.md must start with YAML frontmatter (---)"
        return 1
    fi

    local zip_file="$DIST_DIR/${skill_name}.zip"

    # Remove old zip if exists
    rm -f "$zip_file"

    # Create zip from skill directory
    (cd "$SKILLS_DIR" && zip -r "../$zip_file" "$skill_name" -x "*.DS_Store" -x "*__pycache__*")

    echo "✓ Packaged: $zip_file"
}

# Main logic
if [ -n "$1" ]; then
    # Build specific skill
    package_skill "$1"
else
    # Build all skills
    echo "Building all skills..."
    for skill_dir in "$SKILLS_DIR"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            # Skip hidden directories and .gitkeep
            if [[ ! "$skill_name" =~ ^\. ]]; then
                package_skill "$skill_name"
            fi
        fi
    done
fi

echo ""
echo "Done! Packaged skills are in $DIST_DIR/"
echo ""
echo "Installation:"
echo "  Claude Desktop/Web: Upload ZIP via Settings > Capabilities > Skills"
echo "  Claude Code: Unzip to ~/.claude/skills/"
