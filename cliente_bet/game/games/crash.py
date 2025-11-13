import socketio
import random
import time
from typing import Optional, Callable
from game.core.base_game import BaseGame, BetItem


# -------------------------------
# Configuração do WebSocket
# -------------------------------
sio = socketio.Client()

@sio.event
def connect():
    print("🔗 Conectado ao servidor WebSocket")

@sio.event
def disconnect():
    print("❌ Desconectado do servidor")

try:
    sio.connect("http://localhost:3000")
    print('conectado')
except Exception as e:
    print("⚠️ Não foi possível conectar ao WebSocket:", e)


# -------------------------------
# Estados e classes do jogo
# -------------------------------
class GameState:
    WAITING = "WAITING"
    BETTING = "BETTING"
    FLYING = "FLYING"
    CRASHED = "CRASHED"


class CrashBetItem(BetItem):
    def __init__(self, amount: float, auto_cashout: Optional[float] = None):
        super().__init__(amount, auto_cashout)


class CrashGame(BaseGame):
    def __init__(self):
        super().__init__("Crash")
        self.state = GameState.WAITING
        self.multiplier = 1.0
        self.crash_multiplier = 1.0
        self.countdown_timer = 5
        self.round_interval = 3
        self.last_results = []
        self.max_history = 20

        self.on_state_change: Optional[Callable] = None
        self.on_multiplier_update: Optional[Callable] = None
        self.on_crash: Optional[Callable] = None
        self.on_auto_cashout: Optional[Callable] = None
        self.on_round_start: Optional[Callable] = None

        self._last_update_time = time.time()
        self._betting_start_time = 0
        self._flying_start_time = 0

    # 🔹 Método auxiliar para emitir eventos via socket
    def _emit(self, event, data = None, callback = None):
        if sio.connected:
            sio.emit(event, data or {},callback = callback)
        else:
            print(f"⚠️ Socket não conectado — evento ignorado: {event}")

    # ---------------------------------
    # Ciclo do jogo
    # ---------------------------------
    def start_new_round(self):
        self.state = GameState.BETTING
        self.multiplier = 1.0
        self.countdown_timer = 5
        self.active_bets = []
        self._betting_start_time = time.time()
        self.crash_multiplier = self._generate_crash_point()

        # Emitir via WebSocket
        self._emit("round_start", {"state": self.state, "countdown": self.countdown_timer})
        print('round_start')
        # Mantém os callbacks originais
        if self.on_round_start:
            self.on_round_start()
        if self.on_state_change:
            self.on_state_change(self.state, self.countdown_timer)

    def can_bet(self) -> bool:
        return self.state == GameState.BETTING

    def add_bet(self, amount: float, auto_cashout: Optional[float] = None) -> bool:
        if not self.can_bet():
            return False

        bet = CrashBetItem(amount, auto_cashout)
        self.active_bets.append(bet)
        return True

    def cashout_all(self) -> float:
        if self.state != GameState.FLYING:
            return 0.0

        total_winnings = 0.0
        for bet in self.active_bets:
            if not bet.cashed_out:
                winnings = bet.amount * self.multiplier
                total_winnings += winnings
                bet.cashed_out = True
                bet.cashout_multiplier = self.multiplier

        # 🔹 Emite o cashout global
        self._emit("cashout_all", {"ganhos": total_winnings})

        return total_winnings

    def clear_bets(self) -> float:
        if self.state != GameState.BETTING:
            return 0.0

        total_returned = sum(bet.amount for bet in self.active_bets)
        self.active_bets = []

        self._emit("clear_bets", {"retornado": total_returned})
        return total_returned

    def get_game_state(self) -> dict:
        return {
            'state': self.state,
            'multiplier': self.multiplier,
            'crash_point': self.crash_multiplier,
            'countdown': self.countdown_timer,
            'round_status': self._get_status_text(),
            'can_cashout': self.state == GameState.FLYING and any(not bet.cashed_out for bet in self.active_bets),
        }

    def update(self, dt: float):
        current_time = time.time()

        if self.state == GameState.BETTING:
            elapsed = current_time - self._betting_start_time
            remaining = 5 - int(elapsed)

            if remaining != self.countdown_timer:
                self.countdown_timer = max(0, remaining)
                self._emit("state_change", {"state": self.state, "countdown": self.countdown_timer})

                if self.on_state_change:
                    self.on_state_change(self.state, self.countdown_timer)

            if elapsed >= 5:
                self._start_flying()

        elif self.state == GameState.FLYING:
            elapsed = current_time - self._flying_start_time
            self.multiplier = 1.0 + (elapsed * 0.5)

            self._emit("multiplier_update", {"multiplier": round(self.multiplier, 2)})

            if self.on_multiplier_update:
                self.on_multiplier_update(self.multiplier)

            self._check_auto_cashouts()

            if self.multiplier >= self.crash_multiplier:
                self._crash()

    def cleanup(self):
        self.active_bets = []
        self.state = GameState.WAITING

    def _generate_crash_point(self) -> float:
        rand = random.random()

        if rand < 0.50:
            return random.uniform(1.0, 2.0)
        elif rand < 0.80:
            return random.uniform(2.0, 5.0)
        elif rand < 0.95:
            return random.uniform(5.0, 10.0)
        else:
            return random.uniform(10.0, 50.0)

    def _start_flying(self):
        self.state = GameState.FLYING
        self.multiplier = 1.0
        self._flying_start_time = time.time()

        self._emit("state_change", {"state": self.state})

        if self.on_state_change:
            self.on_state_change(self.state, 0)

    def _crash(self):
        self.state = GameState.CRASHED
        self.multiplier = self.crash_multiplier
        self.last_results.append(round(self.crash_multiplier, 2))

        # Mantém o tamanho máximo do histórico
        if len(self.last_results) > self.max_history:
            self.last_results.pop(0)

        # 🔹 Emite o evento principal do crash
        self._emit("crash", {"crashPoint": round(self.crash_multiplier, 2)})

        # 🔹 Emite também o histórico atualizado
        self._emit("history_update", {"history": self.last_results})

        # Callbacks locais (caso existam)
        if self.on_crash:
            self.on_crash(self.crash_multiplier)

        if self.on_state_change:
            self.on_state_change(self.state, 0)

    def _check_auto_cashouts(self):
        for bet in self.active_bets:
            if not bet.cashed_out and bet.auto_cashout:
                if self.multiplier >= bet.auto_cashout:
                    winnings = bet.amount * bet.auto_cashout
                    bet.cashed_out = True
                    bet.cashout_multiplier = bet.auto_cashout

                    self._emit("auto_cashout", {"ganhos": winnings})

                    if self.on_auto_cashout:
                        self.on_auto_cashout(winnings)

    def _get_status_text(self) -> str:
        if self.state == GameState.WAITING:
            return "Aguardando..."
        elif self.state == GameState.BETTING:
            return "Apostas abertas!"
        elif self.state == GameState.FLYING:
            return "Voando!"
        elif self.state == GameState.CRASHED:
            return f"CRASH em {self.crash_multiplier:.2f}x!"
        return ""
    @sio.on('lista_players')
    def receber_lista_players(jogadores):
        print("👥 Jogadores recebidos:", jogadores)

        # Atualiza o CrashGame ativo
        if CrashGame._instancia_atual:
            CrashGame._instancia_atual.names = jogadores
            print("✅ CrashGame.names atualizado")