const fs = require('fs');

try {
  fs.accessSync('./producao-843114-b_de_bet.p12', fs.constants.R_OK);
  console.log('✅ Certificado encontrado!');
} catch (err) {
  console.error('❌ Certificado não encontrado:', err);
}
