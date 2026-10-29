const { app, BrowserWindow, dialog, ipcMain, shell } = require('electron');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const trial = require('./trial.cjs');

const CONTACT = 'murukutlassl@gmail.com';
let mainWindow;

function stateFile() { return path.join(app.getPath('userData'), 'license-state.json'); }
function publicState() {
  const state = trial.readState(stateFile());
  return { ...trial.entitlement(state), completedRuns: state.completedRuns, device: state.deviceHash.slice(0, 12) };
}

async function chooseAndVerify() {
  let state = trial.readState(stateFile());
  if (!trial.entitlement(state).allowed) return { ok: false, code: 'LICENSE_REQUIRED', state: publicState() };
  const picked = await dialog.showOpenDialog(mainWindow, { title: 'Choose a document to verify locally', properties: ['openFile'] });
  if (picked.canceled || !picked.filePaths[0]) return { ok: false, code: 'CANCELLED', state: publicState() };

  const file = picked.filePaths[0];
  const bytes = fs.readFileSync(file);
  const stat = fs.statSync(file);
  const passport = {
    schema: 'sampling-sigma/passport-demo/v1',
    artifact: { name: path.basename(file), size: stat.size, sha256: crypto.createHash('sha256').update(bytes).digest('hex') },
    scope: 'Local demonstration: byte-integrity commitment only',
    limitations: [
      'A matching digest does not prove truth, authorship, authorization, safety, or completeness.',
      'The selected document remains on this device and is not uploaded by this demo.'
    ],
    generatedAt: new Date().toISOString()
  };
  state = trial.recordCompletedRun(stateFile(), state);
  return { ok: true, passport, state: publicState() };
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1040, height: 760, minWidth: 760, minHeight: 600,
    backgroundColor: '#f6f7fb', title: 'Sampling Sigma Verifier',
    webPreferences: { preload: path.join(__dirname, 'preload.cjs'), contextIsolation: true, nodeIntegration: false, sandbox: true }
  });
  mainWindow.loadFile(path.join(__dirname, 'index.html'));
}

ipcMain.handle('trial:state', () => publicState());
ipcMain.handle('passport:verify', () => chooseAndVerify());
ipcMain.handle('license:contact', () => shell.openExternal(`mailto:${CONTACT}?subject=${encodeURIComponent('Sampling Sigma license or subscription request')}`));
app.whenReady().then(createWindow);
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
