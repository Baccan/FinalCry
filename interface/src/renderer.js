const fs = require('fs');
const { ipcRenderer, shell } = require('electron');

// const { SPECTRE_FOLDER, BACKUP_PATH } = require('./constants');
// const { getConfigContent } = require('./helpers/get-config');

const SPECTRE_FOLDER = 'C:\\Program Files (x86)\\Spectre';
const BACKUP_PATH = `${SPECTRE_FOLDER}\\config.json`;

function getConfigContent() {
  const config_content = JSON.parse(fs.readFileSync(BACKUP_PATH, 'utf8'));

  return config_content;
}

const $EXECUTABLE_BUTTON = document.querySelector('#open-executable');

function removeBlacklistClassnames(className) {
  const blacklistClasses = ['to-activate', 'to-deactivate'];
  const otherClasses = className
    .split(' ')
    .filter((className) => !blacklistClasses.includes(className));

  return otherClasses;
}

function handleSpectreFunction(fileToExecute) {
  const executablePath = `${SPECTRE_FOLDER}\\${fileToExecute}`;

  shell.openPath(executablePath);
}

function writeBackupConfig(path) {
  const backupButton = document.querySelector('.backup-input label');
  const currentBackupButtonContent = backupButton.innerHTML;

  backupButton.innerHTML = 'Carregando...';

  const content = { ...getConfigContent(), backupsRootFolder: path };

  fs.writeFile(BACKUP_PATH, JSON.stringify(content), (err) => {
    if (err) return console.error(err);

    // everything went ok
    alert('Pasta de backups salva com sucesso!');
  });

  document.querySelector('.backup-input label').innerHTML = currentBackupButtonContent;

  console.log({ path, content });
}

ipcRenderer.on('selected-folder', (_, { canceled, filePaths }) => {
  if (canceled) return;

  writeBackupConfig(filePaths.join(''));
});

document.querySelector('#pick-folder').addEventListener('click', (ev) => {
  ev.preventDefault();

  window.postMessage({ type: 'select-dirs' });
});

document.querySelector('#open-executable').addEventListener('click', (ev) => {
  const currentClassName = ev.target.className;

  // function to execute when user wants to activate spectre
  if (currentClassName.includes('to-activate')) {
    const confirmation = confirm('Tem certeza que deseja desativar o Spectre?');

    if (!confirmation) return;

    localStorage.setItem('spectre-active', 'false');

    ev.target.className = [
      ...removeBlacklistClassnames(currentClassName),
      'to-deactivate',
    ].join(' ');
    ev.target.innerHTML = 'Ativar Spectre';

    return handleSpectreFunction('unins001.exe');
    // return handleSpectreFunction('activate.py')
  }

  // otherwise, deactivate spectre
  localStorage.setItem('spectre-active', 'true');

  ev.target.className = [
    ...removeBlacklistClassnames(currentClassName),
    'to-activate',
  ].join(' ');
  ev.target.innerHTML = 'Desativar Spectre';

  return handleSpectreFunction('unins001.exe');
  // return handleSpectreFunction('deactivate.py')
});

// init
const isSpectreActive = localStorage.getItem('spectre-active');

if (isSpectreActive === 'false') {
  const currentClassName = $EXECUTABLE_BUTTON.className;

  $EXECUTABLE_BUTTON.className = [
    ...removeBlacklistClassnames(currentClassName),
    'to-deactivate',
  ].join(' ');
  $EXECUTABLE_BUTTON.innerHTML = 'Ativar Spectre';
}
