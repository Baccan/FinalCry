const fs = require('fs');
const { BACKUP_PATH } = require('../constants');

module.exports = function getConfigContent() {
  const config_content = JSON.parse(fs.readFileSync(BACKUP_PATH, 'utf8'));

  return config_content;
};
