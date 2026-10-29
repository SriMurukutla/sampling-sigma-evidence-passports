const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('sigma', {
  trialState: () => ipcRenderer.invoke('trial:state'),
  verifyDocument: () => ipcRenderer.invoke('passport:verify'),
  contactLicensing: () => ipcRenderer.invoke('license:contact')
});
