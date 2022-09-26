const { ipcRenderer } = require('electron');

process.once('loaded', () => {
  window.addEventListener('message', (evt) => {
    if (evt.data.type != 'select-dirs') return;

    ipcRenderer.send('select-dirs');
  });
});
