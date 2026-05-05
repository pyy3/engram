#!/bin/bash
# Release automation for engram
#
# Usage: ./scripts/release.sh <version>
# Example: ./scripts/release.sh 0.6.0

set -euo pipefail

VERSION="${1:-}"
if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/release.sh <version>"
  echo "Example: ./scripts/release.sh 0.6.0"
  exit 1
fi

echo "Releasing engram v${VERSION}..."

# Update version in files
sed -i "s/VERSION=\".*\"/VERSION=\"$VERSION\"/" bin/engram
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/engram_memory/__init__.py
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Commit version bump
git add -A
git commit -m "Release v${VERSION}"

# Tag
git tag -a "v${VERSION}" -m "Release v${VERSION}"

# Push
echo ""
echo "Ready to push. Run:"
echo "  git push origin main --tags"
echo ""
echo "This will trigger:"
echo "  - CI tests on all platforms"
echo "  - PyPI publish (if tag matches v*)"
echo "  - GitHub Release creation"
