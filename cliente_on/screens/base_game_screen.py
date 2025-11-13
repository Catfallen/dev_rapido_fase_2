# base_game_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
from abc import abstractmethod
from game.ui.components import show_snackbar  # Certifique-se de que isso existe
from typing import Optional

class BaseGameScreen(Screen):
    # ================= PROPRIEDADES =================
    bet_amount = NumericProperty(1)
    auto_cashout_enabled = BooleanProperty(False)
    auto_cashout_value = NumericProperty(2.0)  # valor padrão

    # ================= INICIALIZAÇÃO =================
    def __init__(self, **kwargs):
        self.game_instance = kwargs.pop('game_instance', None)
        self.game_manager = kwargs.pop('game_manager', None)
        self.update_event = None
        super().__init__(**kwargs)

    def on_enter(self):
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_loop, 1/60)  # Considere reduzir para 1/30 se houver lag
        self.update_balance_display()
        self.update_bets_display()

    def on_leave(self):
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    @abstractmethod
    def update_game_display(self):
        """Cada tela de jogo deve implementar sua atualização visual."""
        pass

    # ================= BETS =================
    def decrease_bet_amount(self):
        if self.bet_amount > 1:
            self.bet_amount -= 1

    def increase_bet_amount(self):
        if self.game_manager:
            max_balance = self.game_manager.get_balance()
            # Verifica se há saldo suficiente considerando apostas ativas (se aplicável)
            available_balance = max_balance  # Ajuste se precisar subtrair apostas ativas
            if self.bet_amount < available_balance:
                self.bet_amount += 1

    def set_bet_amount(self, value):
        if not self.game_manager:
            show_snackbar("⚠️ Gerenciador de jogo não disponível")
            return
        if value == "all":
            self.bet_amount = self.game_manager.get_balance()
        else:
            try:
                value = float(value)
                self.bet_amount = min(value, self.game_manager.get_balance())
            except ValueError:
                show_snackbar("⚠️ Valor de aposta inválido")
                pass

    def on_bet_amount_focus(self, widget, focus: bool):
        if not focus:  # perdeu o foco
            try:
                if widget.text.strip() == "":
                    widget.text = f"{self.bet_amount:.2f}"  # Mantém precisão decimal
                    return
                value = float(widget.text)
                self.set_bet_amount(value)
                widget.text = f"{self.bet_amount:.2f}"  # Formata com 2 casas decimais
            except ValueError:
                widget.text = f"{self.bet_amount:.2f}"
                show_snackbar("⚠️ Valor inválido, revertido")

    def on_bet_amount_validate(self):
        if hasattr(self.ids, "bet_amount_input"):
            self.set_bet_amount(self.ids.bet_amount_input.text)

    def update_balance_display(self):
        if hasattr(self.ids, "balance_label") and self.game_manager:
            self.ids.balance_label.text = f"Saldo: R$ {self.game_manager.get_balance():.2f}"

    # ================= AUTO CASHOUT =================
    def toggle_auto_cashout(self):
        self.auto_cashout_enabled = not self.auto_cashout_enabled

    def increase_auto_cashout(self):
        if self.auto_cashout_value < 100:  # limite máximo arbitrário
            self.auto_cashout_value += 0.1

    def decrease_auto_cashout(self):
        if self.auto_cashout_value > 1.0:
            self.auto_cashout_value -= 0.1

    # ================= BET ACTIONS =================
    def place_bet(self, game):
        if not game.can_bet():
            print("[DEBUG] Não é possível apostar agora")
            show_snackbar("⚠️ Não é possível apostar agora")
            return

        # Verifica saldo disponível (ajustado para subtrair apostas ativas)
        total_active_bets = sum(bet.amount for bet in game.active_bets if not bet.cashed_out)
        available_balance = self.game_manager.get_balance() - total_active_bets
        print(f"[DEBUG] Saldo total: {self.game_manager.get_balance()}, Apostas ativas: {total_active_bets}, Disponível: {available_balance}")

        if self.bet_amount > available_balance:
            print("[DEBUG] Saldo insuficiente")
            show_snackbar("⚠️ Saldo insuficiente")
            return

        # Tenta subtrair do saldo
        subtract_success = self.game_manager.subtract_balance(self.bet_amount)
        print(f"[DEBUG] Subtração do saldo: sucesso={subtract_success}")
        if not subtract_success:
            show_snackbar("⚠️ Erro ao subtrair saldo")
            return

        auto_cashout: Optional[float] = self.auto_cashout_value if self.auto_cashout_enabled else None
        print(f"[DEBUG] Chamando game.add_bet com amount={self.bet_amount}, auto_cashout={auto_cashout}")
        success = game.add_bet(self.bet_amount, auto_cashout)
        print(f"[DEBUG] Resultado de game.add_bet: {success}")
        if success:
            print("[DEBUG] Aposta registrada com sucesso")
            show_snackbar(f"🎯 Aposta de R$ {self.bet_amount:.2f} registrada!")
            self.update_balance_display()
            self.update_bets_display()
        else:
            # Se algo falhar, devolve o saldo
            print("[DEBUG] Falha ao registrar aposta, devolvendo saldo")
            self.game_manager.add_balance(self.bet_amount)
            show_snackbar("⚠️ Falha ao registrar aposta")

    # ================= CASHOUT & CLEAR =================
    def cashout_all(self):
        if not self.game_manager or not self.game_manager.get_current_game():
            show_snackbar("⚠️ Nenhum jogo selecionado")
            return

        game = self.game_manager.get_current_game()
        total = game.cashout_all()
        if total > 0:
            self.game_manager.add_balance(total)
            show_snackbar(f"💰 Cashout realizado! Recebido: R$ {total:.2f}")
            self.update_balance_display()
            self.update_bets_display()
        else:
            show_snackbar("⚠️ Nenhuma aposta para cashout")

    def clear_bets(self):
        if not self.game_manager or not self.game_manager.get_current_game():
            return

        game = self.game_manager.get_current_game()
        returned = game.clear_bets()
        if returned > 0:
            self.game_manager.add_balance(returned)
            show_snackbar("🧹 Apostas limpas!")
            self.update_balance_display()
            self.update_bets_display()
        else:
            show_snackbar("⚠️ Nenhuma aposta para limpar")

    # ================= UPDATE BETS DISPLAY =================
    def update_bets_display(self):
        if not self.game_manager or not self.game_manager.get_current_game():
            return

        game = self.game_manager.get_current_game()
        bets = game.active_bets

        # Atualiza total
        if hasattr(self.ids, "total_bets_label"):
            total = sum(bet.amount for bet in bets if not bet.cashed_out)
            self.ids.total_bets_label.text = f"Apostas: R$ {total:.2f}"

        # Atualiza lista
        if hasattr(self.ids, "bets_list"):
            try:
                self.ids.bets_list.clear_widgets()
                from kivymd.uix.list import OneLineListItem
                for bet in bets:
                    text = f"R$ {bet.amount:.2f}"
                    if bet.auto_cashout:
                        text += f" @ {bet.auto_cashout:.1f}x"
                    self.ids.bets_list.add_widget(OneLineListItem(text=text))
            except AttributeError:
                show_snackbar("⚠️ Erro ao atualizar lista de apostas")

    # ================= UPDATE LOOP =================
    def update_loop(self, dt):
        try:
            self.update_game_display()
        except Exception as e:
            print(f"Erro no update_loop: {e}")  # Log para debug
