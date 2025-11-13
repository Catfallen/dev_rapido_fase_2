const { Server } = require("socket.io");
const jwt = require("jsonwebtoken");

let io;
const userSocketMap = new Map(); // userId -> socket.id

function initWebSocket(server) {
  io = new Server(server, {
    cors: {
      origin: "*", // altere para FRONTEND_URL em produção
      methods: ["GET", "POST"],
    },
  });

  io.on("connection", (socket) => {
    console.log("🧠 Novo cliente conectado:", socket.id);

    // 🔹 Autenticação via token JWT
    socket.on("autenticar", (token) => {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const userId = decoded.id;
        socket.data.userId = userId;
        userSocketMap.set(userId, socket.id);

        console.log(`✅ Usuário ${userId} autenticado no socket ${socket.id}`);

        socket.join(String(userId));
        socket.emit("autenticado", { userId });
        io.emit("usuario_autenticado", { userId });

      } catch (err) {
        console.error("❌ Token inválido:", err.message);
        socket.emit("erro_autenticacao", { msg: "Token inválido" });
        socket.disconnect();
      }
    });

    // 🔹 Eventos do jogo que podem vir do cliente Python
    const eventosJogo = [
      "round_start",
      "cashout_all",
      "clear_bets",
      "state_change",
      "multiplier_update",
      "crash",
      "auto_cashout",
      "history_update"
    ];
    
    // 🔁 Repassa os eventos do jogo para todos os outros clientes conectados
    eventosJogo.forEach((evento) => {
      socket.on(evento, (dados) => {
        console.log(`📩 Evento '${evento}' recebido de ${socket.id}:`, dados);
        // Reenvia para todos os outros clientes conectados (exceto o remetente)
        socket.broadcast.emit(evento, dados);
      });
    });

    // 🔌 Quando o cliente desconecta
    socket.on("disconnect", () => {
      const userId = socket.data.userId;
      if (userId && userSocketMap.get(userId) === socket.id) {
        userSocketMap.delete(userId);
        console.log(`🔌 Usuário ${userId} desconectado (${socket.id})`);
      }
    });
  });
}

/**
 * 🎯 Envia um evento diretamente para um usuário específico (via userId)
 */
function emitParaUsuario(userId, evento, dados) {
  const socketId = userSocketMap.get(userId);
  if (socketId) {
    io.to(socketId).emit(evento, dados);
    console.log(`🎯 Evento '${evento}' enviado para ${userId}:`, dados);
  } else {
    console.log(`⚠️ Usuário ${userId} não está conectado.`);
  }
}

/**
 * 🌍 Envia um evento para todos os clientes conectados
 */
function emitEvento(evento, dados) {
  if (io) {
    io.emit(evento, dados);
    console.log(`🌍 Evento global '${evento}' emitido:`, dados);
  } else {
    console.error("❌ Servidor WebSocket não inicializado.");
  }
}

module.exports = { initWebSocket, emitEvento, emitParaUsuario };
