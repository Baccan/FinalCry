const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 750,
    height: 600,
    // frame: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      icon: path.join(__dirname, 'assets', 'logo.ico'),
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadFile('../index.html');

  // TODO: dev only
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.on('select-dirs', async () => {
  try {
    const result = await dialog.showOpenDialog({ properties: ['openDirectory'] });

    mainWindow.webContents.send('selected-folder', result);
  } catch (error) {
    alert('Algo deu errado ao selecionar a pasta');
  }
});
