#!/usr/bin/env node
/**
 * npx engram-memory — thin wrapper that delegates to the bash CLI.
 *
 * Checks if engram is installed, installs it if not, then runs the command.
 */
const { execSync, spawnSync } = require('child_process');
const { existsSync } = require('fs');
const { join } = require('path');
const os = require('os');

const ENGRAM_HOME = process.env.ENGRAM_HOME || join(os.homedir(), '.engram');
const BIN_DIR = join(ENGRAM_HOME, 'bin');
const ENGRAM_BIN = join(BIN_DIR, 'engram');

function install() {
  console.log('Installing engram...');
  const repoUrl = 'https://github.com/grynn-in/engram.git';
  const tmpDir = join(os.tmpdir(), `engram-install-${Date.now()}`);

  try {
    execSync(`git clone --depth 1 ${repoUrl} ${tmpDir}`, { stdio: 'pipe' });
    execSync(`bash ${join(tmpDir, 'install.sh')}`, { stdio: 'inherit' });
  } finally {
    execSync(`rm -rf ${tmpDir}`, { stdio: 'pipe' });
  }
}

// Check if installed
if (!existsSync(ENGRAM_BIN)) {
  install();
}

// Run engram with passed arguments
const args = process.argv.slice(2);
const result = spawnSync(ENGRAM_BIN, args, {
  stdio: 'inherit',
  env: { ...process.env, PATH: `${BIN_DIR}:${process.env.PATH}` }
});

process.exit(result.status || 0);
