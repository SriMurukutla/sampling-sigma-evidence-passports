const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const FREE_RUNS = 2;

function platformMachineSource() {
  try {
    if (process.platform === 'darwin') {
      return execFileSync('ioreg', ['-rd1', '-c', 'IOPlatformExpertDevice'], { encoding: 'utf8' })
        .match(/"IOPlatformUUID"\s*=\s*"([^"]+)"/)?.[1];
    }
    if (process.platform === 'win32') {
      return execFileSync('powershell.exe', ['-NoProfile', '-Command', '(Get-CimInstance Win32_ComputerSystemProduct).UUID'], { encoding: 'utf8' }).trim();
    }
    return fs.readFileSync('/etc/machine-id', 'utf8').trim();
  } catch {
    return null;
  }
}

function deviceHash() {
  const source = platformMachineSource() || [os.hostname(), os.platform(), os.arch()].join('|');
  return crypto.createHash('sha256').update(`sampling-sigma-v1|${source}`).digest('hex');
}

function emptyState(id = deviceHash()) {
  return { schema: 1, deviceHash: id, completedRuns: 0, licensed: false, updatedAt: null };
}

function readState(file, id = deviceHash()) {
  try {
    const state = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (state.schema !== 1 || state.deviceHash !== id) return emptyState(id);
    return state;
  } catch {
    return emptyState(id);
  }
}

function writeState(file, state) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temp = `${file}.tmp`;
  fs.writeFileSync(temp, JSON.stringify(state, null, 2), { mode: 0o600 });
  fs.renameSync(temp, file);
}

function entitlement(state) {
  const remaining = Math.max(0, FREE_RUNS - state.completedRuns);
  return { allowed: state.licensed || remaining > 0, remaining, licensed: state.licensed };
}

function recordCompletedRun(file, state) {
  const next = { ...state, completedRuns: state.completedRuns + 1, updatedAt: new Date().toISOString() };
  writeState(file, next);
  return next;
}

module.exports = { FREE_RUNS, deviceHash, emptyState, readState, writeState, entitlement, recordCompletedRun };
