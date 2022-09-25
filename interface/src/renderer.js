const path = require('path');
const { execFile } = require('child_process');

function handleSpectreFunction(fileToExecute) {
  const executablePath = `C:\\Program Files (x86)\\Spectre\\${fileToExecute}`;

  execFile(executablePath, (err, data) => {
    if (err) return console.error(err);

    // everything went fine
    // console.log(data.toString());
  });
}

function writeBackupConfig(path) {
  console.log('writing backup config at', path);
}

document.querySelector('#pick-folder').addEventListener('change', (ev) => {
  const { dir } = path.parse(ev.target.files[0].path);
  const fullPath = dir.substring(0, dir.lastIndexOf('\\'));

  writeBackupConfig(fullPath);
});

document.querySelector('#open-executable').addEventListener('click', (ev) => {
  const currentClassName = ev.target.className;

  // function to execute when user wants to activate spectre
  if (currentClassName == 'to-activate') {
    ev.target.className = 'to-deactivate';
    ev.target.innerHTML = 'Desativar Spectre';

    return handleSpectreFunction('unins000.exe');
    // return handleSpectreFunction('activate.py')
  }

  // otherwise, deactivate spectre
  ev.target.className = 'to-activate';
  ev.target.innerHTML = 'Ativar Spectre';

  return handleSpectreFunction('unins000.exe');
  // return handleSpectreFunction('deactivate.py')
});
