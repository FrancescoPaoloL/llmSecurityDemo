#!/bin/bash
# scripts/bump-version.sh
# Usage: ./scripts/bump-version.sh [major|minor|patch]
#       Patch (bug fixes)
#       Minor (new features)
#       Major (breaking changes / 1.0.0)

set -e

TYPE=${1:-patch}

# Validate argument
if [[ ! "$TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Usage: $0 [major|minor|patch]"
    exit 1
fi

# Read current version
CURRENT=$(grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' api/__version__.py)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

# Calculate new version
case $TYPE in
    major)
        NEW="$((MAJOR+1)).0.0"
        ;;
    minor)
        NEW="$MAJOR.$((MINOR+1)).0"
        ;;
    patch)
        NEW="$MAJOR.$MINOR.$((PATCH+1))"
        ;;
esac

echo "Bumping version: $CURRENT → $NEW ($TYPE)"

# Update files
echo "__version__ = \"$NEW\"" > api/__version__.py
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW\"/" frontend/package.json
sed -i "s/frontendVersion: '[^']*'/frontendVersion: '$NEW'/" frontend/views/index.ejs

# Git operations
git add api/__version__.py frontend/package.json frontend/views/index.ejs
git commit -m "chore: bump version to $NEW"
git tag "v$NEW"

echo ""
echo "Version bumped to $NEW"
echo "Don't forget: git push && git push --tags"

