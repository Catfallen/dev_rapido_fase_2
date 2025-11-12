require('dotenv').config();
const express = require('express');
const http = require('http');
const {initWebSocket} = require('./websocket/crash.socket');
const app = express();


// ✅ Middleware JSON unificado com rawBody preservado
app.use(express.json({
    limit: '1mb',
    verify: (req, res, buf) => {
        req.rawBody = buf.toString();
    }
}));



const paymentRoutes = require('./routes/payment.routes'); //rotas de pagamentos
const authRoutes = require('./routes/authRoutes'); //routas de autenticação
const betRoutes = require('./routes/bet.routes'); //rota dos jogos



app.use('/auth',authRoutes,betRoutes);
app.use("/payments", paymentRoutes);
app.use("/bet",betRoutes)

//teste do websocket 
const server = http.createServer(app);
initWebSocket(server);
//servidor WebSocket
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log("HTTP + WebSocket rodando!"));