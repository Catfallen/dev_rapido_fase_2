require('dotenv').config();
const express = require('express');
const http = require('http');
const {initWebSocket} = require('./websocket/crash.socket');
const app = express();
const cors = require('cors');
const path = require('path');

// ✅ Middleware JSON unificado com rawBody preservado
app.use(express.json({
    limit: '1mb',
    verify: (req, res, buf) => {
        req.rawBody = buf.toString();
    }
}));

app.use(cors());



app.use(express.static(path.join(__dirname, 'public')));


const paymentRoutes = require('./routes/payment.routes'); //rotas de pagamentos
const authRoutes = require('./routes/authRoutes'); //routas de autenticação
const betRoutes = require('./routes/bet.routes'); //rota dos jogos
const publicRoutes = require('./routes/public.routes');


app.use('/auth',authRoutes,betRoutes);
app.use("/payments", paymentRoutes);
app.use("/bet",betRoutes)
app.use('/public',publicRoutes);
//teste do websocket 
const server = http.createServer(app);
initWebSocket(server);
//servidor WebSocket
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log("HTTP + WebSocket rodando!"));