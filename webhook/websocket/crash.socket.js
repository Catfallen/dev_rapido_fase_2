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

    // 🧩 Autenticação via token JWT
    socket.on("autenticar", (token) => {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        console.log(decoded);
        const userId = decoded.id;

        // Armazena todos os dados do jogador
        userSocketMap.set(userId, {
          socketId: socket.id,
          nome: decoded.nome,
          email: decoded.email,
        });

        socket.data.userId = userId;
        console.log(`✅ Usuário ${decoded.nome} (${userId}) autenticado no socket ${socket.id}`);

        socket.join(String(userId));
        socket.emit("autenticado", { userId });
        io.emit("usuario_autenticado", { userId });

        // 🔁 Atualiza a lista de jogadores para todos
        atualizarListaJogadores();

      } catch (err) {
        console.error("❌ Token inválido:", err.message);
        socket.emit("erro_autenticacao", { msg: "Token inválido" });
        socket.disconnect();
      }
    });

    // 🎮 Eventos do jogo
    const eventosJogo = [
      "round_start",
      "cashout_all",
      "clear_bets",
      "state_change",
      "multiplier_update",
      "crash",
      "auto_cashout",
      "history_update",
    ];

    eventosJogo.forEach((evento) => {
      socket.on(evento, (dados) => {
        console.log(`📩 Evento '${evento}' recebido de ${socket.id}:`, dados);
        socket.broadcast.emit(evento, dados);
      });
    });

    // 👥 Solicitação manual de jogadores conectados
    socket.on("players", () => {
      const jogadores = Array.from(userSocketMap.keys());
      socket.emit("lista_players", jogadores);
    });

    // 🔌 Desconexão
    socket.on("disconnect", () => {
      const userId = socket.data.userId;
      if (userId && userSocketMap.get(userId) === socket.id) {
        userSocketMap.delete(userId);
        console.log(`🔌 Usuário ${userId} desconectado (${socket.id})`);
        atualizarListaJogadores();
      }
    });
  });
}

/**
 * 🧾 Atualiza a lista de jogadores para todos os clientes conectados
 */
function atualizarListaJogadores(destinoSocket = null) {
  const lista = Array.from(userSocketMap.entries()).map(([id, info]) => ({
    id,
    nome: info.nome,
    email: info.email,
  }));

  if (destinoSocket) {
    destinoSocket.emit("lista_players", lista);
  } else {
    io.emit("lista_players", lista);
  }

  console.log("📜 Lista de jogadores conectados:", lista);
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
 * 🌍 Envia um evento global
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