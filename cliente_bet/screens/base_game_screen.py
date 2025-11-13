from abc import abstractmethod
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
from game.core.game_manager import GameManager
from game.ui.components import show_snackbar


class BaseGameScreen(Screen):
    
    bet_amount = NumericProperty(10)
    auto_cashout_enabled = BooleanProperty(False)
    auto_cashout_value = NumericProperty(2.0)
    
    def __init__(self, game_instance, **kwargs):
        self.update_event = None
        self.game_manager = GameManager()
        self.game = game_instance
        super().__init__(**kwargs)
    
    def on_enter(self):
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_loop, 1/60)
            self.update_balance_display()
            self.update_bets_display()
    
    def on_leave(self):
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_loop, 1/60)
            self.update_balance_display()
            self.update_bets_display()
            self.update_loop(0)
    
    @abstractmethod
    def update_game_display(self):
        pass
    
    def decrease_bet_amount(self):
        if self.bet_amount > 1:
            self.bet_amount -= 1
    
    def increase_bet_amount(self):
        if self.bet_amount < self.game_manager.get_balance():
            self.bet_amount += 1
    
    def set_bet_amount(self, value):
        if value == 'all':
            self.bet_amount = self.game_manager.get_balance()
        else:
            max_bet = self.game_manager.get_balance()
            self.bet_amount = min(float(value), max_bet)
        
        if hasattr(self.ids, 'bet_amount_input'):
            self.ids.bet_amount_input.text = str(int(self.bet_amount))
    
    def on_bet_amount_validate(self):
        try:
            value = float(self.ids.bet_amount_input.text)
            if value > 0 and value <= self.game_manager.get_balance():
                self.bet_amount = value
                show_snackbar(f'Valor da aposta definido para R$ {value:.2f}')
            else:
                show_snackbar('Valor inválido! Use um valor entre R$ 0,01 e seu saldo.')
                self.ids.bet_amount_input.text = str(int(self.bet_amount))
        except ValueError:
            show_snackbar('Digite um valor numérico válido!')
            self.ids.bet_amount_input.text = str(int(self.bet_amount))
    
    def on_bet_amount_focus(self, instance, value):
        if not value:
            self.on_bet_amount_validate()
    
    def decrease_auto_cashout(self):
        if self.auto_cashout_value > 1.1:
            self.auto_cashout_value -= 0.1
    
    def increase_auto_cashout(self):
        if self.auto_cashout_value < 100:
            self.auto_cashout_value += 0.1
    
    def toggle_auto_cashout(self):
        self.auto_cashout_enabled = not self.auto_cashout_enabled
    
    def update_checkbox_color(self, instance, value):
        if hasattr(self, 'ids') and 'auto_cashout_checkbox' in self.ids:
            if value:
                self.ids.auto_cashout_checkbox.md_bg_color = [0.2, 0.8, 0.2, 1]
            else:
                self.ids.auto_cashout_checkbox.md_bg_color = [0.4, 0.4, 0.4, 1]
    
    def add_bet(self):
        if self.bet_amount <= 0:
            show_snackbar('Valor deve ser maior que zero!')
            return
        
        if self.bet_amount > self.game_manager.get_balance():
            show_snackbar('Saldo insuficiente!')
            return
        
        auto_cashout_value = None
        if self.auto_cashout_enabled:
            auto_cashout_value = self.auto_cashout_value
            if auto_cashout_value <= 1.0:
                show_snackbar('Auto Cashout deve ser maior que 1.0x!')
                return
        
        if self.game.add_bet(self.bet_amount, auto_cashout=auto_cashout_value):
            self.game_manager.subtract_balance(self.bet_amount)
            self.update_bets_display()
            self.update_balance_display()
            show_snackbar(f'Aposta de R$ {self.bet_amount:.2f} adicionada!')
        else:
            show_snackbar('Não foi possível adicionar a aposta!')
    
    def cashout_all(self):
        total_winnings = self.game.cashout_all()
        if total_winnings > 0:
            self.game_manager.add_balance(total_winnings)
            self.update_bets_display()
            self.update_balance_display()
            show_snackbar(f'Retirada total! Ganho: R$ {total_winnings:.2f}')
        else:
            show_snackbar('Nenhuma aposta ativa para retirar.')
    
    def clear_bets(self):
        total_returned = self.game.clear_bets()
        if total_returned > 0:
            self.game_manager.add_balance(total_returned)
            self.update_bets_display()
            self.update_balance_display()
            show_snackbar('Apostas canceladas!')
        else:
            show_snackbar('Não é possível limpar apostas fora da fase de apostas.')
    
    def update_bets_display(self):
        self.ids.bets_list.clear_widgets()
        total_bets = self.game.get_active_bets_total()
        self.ids.total_bets_label.text = f'Apostas: R$ {total_bets:.2f}'
        
        has_bets = len(self.game.active_bets) > 0
        self.ids.clear_bets_btn.disabled = not has_bets
        
        for i, bet in enumerate(self.game.active_bets):
            item_text = f'Aposta {i+1}: R$ {bet.amount:.2f}'
            if bet.auto_cashout:
                item_text += f' (Auto: {bet.auto_cashout:.2f}x)'
            if bet.cashed_out:
                item_text += f' (Retirado em {bet.cashout_multiplier:.2f}x)'
            
            from kivymd.uix.list import OneLineListItem
            item = OneLineListItem()
            item.text = item_text
            item.theme_text_color = 'Primary'
            self.ids.bets_list.add_widget(item)
    
    def update_balance_display(self):
        self.ids.balance_label.text = f'Saldo: R$ {self.game_manager.get_balance():.2f}'
    
    def update_loop(self, dt):
        self.game.update(dt)
        state = self.game.get_game_state()
        self.update_game_display()
        self.update_bets_display()
        
        can_cashout = state.get('can_cashout', False)
        if hasattr(self.ids, 'cashout_btn'):
            self.ids.cashout_btn.disabled = not can_cashout
