const EfiPay = require('sdk-node-apis-efi');
const options = require('./config');

const efipay = new EfiPay(options);

const params = {
  idEnvio: 'pix' + Date.now().toString(), // ID único, só letras e números
};

const body = {
  valor: {
    original: '10.00', // deve estar dentro de um objeto
  },
  chave: 'marcosalex9061@gmail.com', // chave PIX de quem vai receber
  infoPagador: 'Pagamento de teste via produção',
};

efipay.pixSend(params, body)
  .then(res => {
    console.log('✅ Pix enviado com sucesso!');
    console.log(res);
  })
  .catch(err => {
    console.error('❌ Erro ao enviar Pix:');
    console.error(err);
  });
