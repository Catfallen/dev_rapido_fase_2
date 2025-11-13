import random
import socketio
from kivy.clock import Clock
from kivy.animation import Animation
from screens.base_game_screen import BaseGameScreen  # Certifique-se de que o caminho está correto
from game.ui.components import HistorySquare, WinnerItem

class CrashGameScreen(BaseGameScreen):
    def __init__(self, **kwargs):
        # Extrai argumentos customizados
        game_manager = kwargs.pop('game_manager', None)
        super().__init__(game_manager=game_manager, **kwargs)

        # Dados do jogador
        self.balance = game_manager.get_balance() if game_manager else 0
        self.current_bet = 0
        self.is_in_round = False
        self.has_cashed_out = False
        self.current_multiplier = 1.0

        self.names = [
            "An***ymous", "Pl***er", "Ga***r", "Lu***y", "Wi***r",
            "Cr***h", "Be***r", "Fa***t", "Bi***n", "Ac***e",
            "Ph***x", "Sh***w", "Vo***x", "Bl***e", "Ti***n",
            "Sp***e", "Ro***e", "Ze***h", "No***a", "St***r"
        ]

        # Conecta WebSocket
        self.socket = socketio.Client()
        self.setup_socket_events()
        try:
            self.socket.connect("http://localhost:3000")
        except Exception as e:
            print("❌ Erro ao conectar ao servidor:", e)

        Clock.schedule_interval(self.update_winners_display, 3)

    # ---------------- Sobrescreve add_bet para usar place_bet ----------------
    def add_bet(self):
        """Sobrescreve add_bet da base para integrar com a lógica de WebSocket."""
        print(f"[DEBUG] add_bet chamado em CrashGameScreen: bet_amount={self.bet_amount}")
        
        # Verificações básicas da base (reutilizando lógica de BaseGameScreen se possível)
        if self.bet_amount <= 0:
            from game.ui.components import show_snackbar
            show_snackbar("⚠️ Aposta inválida")
            return
        
        # Chama place_bet com o valor atual
        self.place_bet(self.bet_amount)

    # ---------------- Sobrescreve cashout_all para usar cashout ----------------
    def cashout_all(self):
        """Sobrescreve cashout_all da base para integrar com a lógica de WebSocket."""
        print(f"[DEBUG] cashout_all chamado em CrashGameScreen")
        
        # Em crash, "retirar tudo" significa fazer cashout da aposta atual (se houver)
        if self.current_bet > 0 and self.is_in_round and not self.has_cashed_out:
            self.cashout()  # Chama o cashout local
            from game.ui.components import show_snackbar
            show_snackbar("💰 Cashout realizado!")
        else:
            from game.ui.components import show_snackbar
            show_snackbar("⚠️ Nenhuma aposta ativa para retirar")

    # ---------------- Eventos WebSocket ----------------
    def setup_socket_events(self):
        @self.socket.event
        def connect():
            print("✅ Conectado ao WebSocket")

        @self.socket.event
        def disconnect():
            print("🔌 Desconectado do WebSocket")

        @self.socket.on("round_start")
        def on_round_start(data=None):
            print("🟢 Nova rodada")
            self.is_in_round = True
            self.has_cashed_out = False
            self.current_multiplier = 1.0
            self.current_bet = 0
            self.update_balance_display()
            self.animate_countdown()

        @self.socket.on("multiplier_update")
        def on_multiplier_update(data):
            self.current_multiplier = data.get("multiplier", 1.0)
            area = self._get_game_area_ids()
            lbl = area.get("multiplier_display")
            if lbl:
                lbl.text = f"{self.current_multiplier:.2f}x"

        @self.socket.on("crash")
        def on_crash(data):
            crash_point = data.get("crashPoint", 1.0)
            print(f"💥 Crash em {crash_point:.2f}x")
            self.is_in_round = False
            self.animate_plane_crash()

            # Perde a aposta se não sacou
            if self.current_bet > 0 and not self.has_cashed_out:
                print("❌ Você perdeu a aposta!")
                self.current_bet = 0
                self.update_balance_display()

            Clock.schedule_once(self.reset_round, 2)

        @self.socket.on("cashout_all")
        def on_cashout_all(data):
            ganhos = data.get("ganhos", 0)
            print(f"💰 Cashout: {ganhos:.2f}")
            self.has_cashed_out = True
            self.current_bet = 0
            if self.game_manager:
                self.game_manager.add_balance(ganhos)
            self.balance += ganhos
            self.update_balance_display()

        @self.socket.on("state_change")
        def on_state_change(data):
            state = data.get("state")
            countdown = data.get("countdown", 0)

            # Atualiza o estado interno da rodada
            self.is_in_round = state == "FLYING"

            # Atualiza o label da contagem regressiva
            area_ids = self._get_game_area_ids()
            countdown_label = area_ids.get("countdown")
            round_status_label = area_ids.get("round_status")

            if countdown_label:
                countdown_label.text = f"Iniciando em {countdown}s" if countdown > 0 else "Rodada iniciando..."
            if round_status_label:
                round_status_label.text = f"Estado: {state}"

            if countdown > 0 and countdown_label:
                anim = Animation(text_color=[1, 0.8, 0.2, 1], duration=0.3) + Animation(
                    text_color=[0.9, 0.9, 0.9, 1], duration=0.3
                )
                anim.start(countdown_label)

    # ---------------- Lógica de apostas ----------------
    def place_bet(self, amount):
        print(f"[DEBUG] place_bet chamado com amount={amount}")
        if self.is_in_round:
            print("⚠️ Não é possível apostar durante a rodada")
            from game.ui.components import show_snackbar
            show_snackbar("⚠️ Não é possível apostar durante a rodada")
            return
        if self.balance >= amount:
            self.current_bet = amount
            self.balance -= amount
            if self.game_manager:
                self.game_manager.subtract_balance(amount)
            self.update_balance_display()
            print(f"🎯 Aposta de {amount} colocada")
            self.socket.emit("place_bet", {"amount": amount})
        else:
            print("⚠️ Saldo insuficiente")
            from game.ui.components import show_snackbar
            show_snackbar("⚠️ Saldo insuficiente")

    def cashout(self):
        if self.is_in_round and not self.has_cashed_out and self.current_bet > 0:
            ganhos = self.current_bet * self.current_multiplier
            self.balance += ganhos
            if self.game_manager:
                self.game_manager.add_balance(ganhos)
            self.current_bet = 0
            self.has_cashed_out = True
            print(f"💸 Cashout realizado: {ganhos:.2f}")
            self.update_balance_display()
            self.socket.emit("cashout", {"ganhos": ganhos})
        else:
            print("⚠️ Não é possível fazer cashout agora")

    # ---------------- Atualizações visuais ----------------
    def reset_round(self, dt):
        self.current_bet = 0
        self.has_cashed_out = False
        self.is_in_round = False
        area = self._get_game_area_ids()
        if area.get("multiplier_display"):
            area["multiplier_display"].text = "1.00x"
        if area.get("round_status"):
            area["round_status"].text = "Aguardando próxima rodada..."

    def update_winners_display(self, dt):
        if not hasattr(self.ids, "winners_bar"):
            return
        self.ids.winners_bar.clear_widgets()
        for _ in range(5):
            name = random.choice(self.names)
            amount = random.uniform(50, 2000)
            multiplier = random.uniform(1.5, 8.0)
            winner_widget = WinnerItem(name=name, amount=amount, multiplier=multiplier)
            winner_widget.size_hint_x = 0.2
            self.ids.winners_bar.add_widget(winner_widget)

    def animate_countdown(self):
        lbl = self._get_game_area_ids().get("round_status")
        if not lbl:
            return
        anim = Animation(text_color=[1, 0.8, 0.2, 1], duration=0.3) + Animation(
            text_color=[0.9, 0.9, 0.9, 1], duration=0.3
        )
        anim.start(lbl)

    def animate_plane_crash(self):
        lbl = self._get_game_area_ids().get("multiplier_display")
        if not lbl:
            return
        anim = Animation(text_color=[1, 0, 0, 1], duration=0.5)
        anim.start(lbl)
        Clock.schedule_once(lambda dt: setattr(lbl, "text_color", [0, 1, 0, 1]), 2.0)

    def _get_game_area_ids(self):
        if hasattr(self, "ids") and hasattr(self.ids, "game_area"):
            return self.ids.game_area.ids
        return {}
