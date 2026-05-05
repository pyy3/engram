#!/bin/bash
# Engram Installer
#
# Installs the engram CLI and sets up configuration.
#
# Usage:
#   bash install.sh                    # install to ~/.engram
#   ENGRAM_HOME=/opt/engram bash install.sh   # custom location
#
# What it does:
#   1. Copies/links scripts to ENGRAM_HOME/bin/
#   2. Adds ENGRAM_HOME/bin to PATH (via ~/.bashrc or ~/.zshrc)
#   3. Creates default config at ~/.config/engram/config.toml
#   4. Creates template directory at ENGRAM_HOME/templates/
#   5. Verifies dependencies

set -euo pipefail

ENGRAM_HOME="${ENGRAM_HOME:-$HOME/.engram}"
BIN_DIR="$ENGRAM_HOME/bin"
CONFIG_DIR="$HOME/.config/engram"
TEMPLATES_DIR="$ENGRAM_HOME/templates"

echo "Installing Engram to: $ENGRAM_HOME"
echo ""

# Detect if running from cloned repo or curl pipe
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/bin/engram" ]; then
  SOURCE_DIR="$SCRIPT_DIR"
  echo "  Source: local repo ($SOURCE_DIR)"
else
  echo "Error: run this from the engram repository root."
  exit 1
fi

# 1. Install scripts
mkdir -p "$BIN_DIR"
for script in engram engram-init engram-start engram-end engram-search engram-sync engram-status engram-index engram-qdrant engram-hooks engram-template engram-export engram-import engram-setup; do
  if [ -f "$SOURCE_DIR/bin/$script" ]; then
    cp "$SOURCE_DIR/bin/$script" "$BIN_DIR/$script"
    chmod +x "$BIN_DIR/$script"
  fi
done
echo "  Installed scripts to $BIN_DIR/"

# 2. Install templates
mkdir -p "$TEMPLATES_DIR"
if [ -d "$SOURCE_DIR/templates" ]; then
  cp -r "$SOURCE_DIR/templates/"* "$TEMPLATES_DIR/" 2>/dev/null || true
  echo "  Installed templates to $TEMPLATES_DIR/"
fi

# 2b. Install lib/
mkdir -p "$ENGRAM_HOME/lib"
if [ -d "$SOURCE_DIR/lib" ]; then
  cp -r "$SOURCE_DIR/lib/"* "$ENGRAM_HOME/lib/" 2>/dev/null || true
  echo "  Installed lib to $ENGRAM_HOME/lib/"
fi

# 2c. Install completions
mkdir -p "$ENGRAM_HOME/completions"
if [ -d "$SOURCE_DIR/completions" ]; then
  cp "$SOURCE_DIR/completions/"* "$ENGRAM_HOME/completions/" 2>/dev/null || true
  echo "  Installed completions to $ENGRAM_HOME/completions/"
fi

# 3. Create default config
mkdir -p "$CONFIG_DIR"
if [ ! -f "$CONFIG_DIR/config.toml" ]; then
  cat > "$CONFIG_DIR/config.toml" << 'TOML'
# Engram configuration
# See: https://github.com/YOUR_USER/engram#configuration

[embedding]
provider = "ollama"
model = "nomic-embed-text"
url = "http://127.0.0.1:11434"
max_chars = 1800

[search]
file_threshold = 0.18
chunk_threshold = 0.25
chunk_lines = 200
max_results = 5

[session]
checkpoint_minutes = 30
TOML
  echo "  Created config: $CONFIG_DIR/config.toml"
else
  echo "  Config exists: $CONFIG_DIR/config.toml (kept)"
fi

# 4. Add to PATH
add_to_path() {
  local rc_file="$1"
  local marker="# Engram"

  if [ -f "$rc_file" ] && grep -q "$marker" "$rc_file"; then
    return 0
  fi

  if [ -f "$rc_file" ] || [ "$rc_file" = "$HOME/.bashrc" ]; then
    echo "" >> "$rc_file"
    echo "$marker" >> "$rc_file"
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$rc_file"
    echo "  Added to PATH in $(basename "$rc_file")"
    return 0
  fi
  return 1
}

# Detect shell
PATH_ADDED=false
if [ -n "${ZSH_VERSION:-}" ] || [ "$(basename "${SHELL:-}")" = "zsh" ]; then
  add_to_path "$HOME/.zshrc" && PATH_ADDED=true
fi
if [ "$(basename "${SHELL:-}")" = "bash" ] || [ ! "$PATH_ADDED" = true ]; then
  add_to_path "$HOME/.bashrc" && PATH_ADDED=true
fi

# 5. Verify dependencies
echo ""
echo "Dependency check:"

# Python
if command -v python3 >/dev/null 2>&1; then
  PY_VERSION=$(python3 --version 2>&1)
  echo "  [ok] $PY_VERSION"
else
  echo "  [!!] Python 3 not found — required for semantic search"
fi

# ripgrep
if command -v rg >/dev/null 2>&1; then
  RG_VERSION=$(rg --version | head -1)
  echo "  [ok] $RG_VERSION"
else
  echo "  [--] ripgrep not found — keyword search won't work"
  echo "       Install: https://github.com/BurntSushi/ripgrep#installation"
fi

# Ollama (optional)
if curl -s -o /dev/null "http://127.0.0.1:11434" 2>/dev/null; then
  echo "  [ok] Ollama running (semantic search available)"
else
  echo "  [--] Ollama not detected (optional — semantic search disabled)"
  echo "       Install: https://ollama.com then: ollama pull nomic-embed-text"
fi

echo ""
echo "Installation complete!"
echo ""
echo "To use immediately (without restarting shell):"
echo "  export PATH=\"$BIN_DIR:\$PATH\""
echo ""
echo "Initialize a project:"
echo "  cd ~/your-project && engram init"
echo ""
echo "Start a session:"
echo "  engram start \"your topic\""
