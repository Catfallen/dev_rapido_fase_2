from kivy.animation import Animation
from kivy.clock import Clock
from screens.base_game_screen import BaseGameScreen
from game.games.crash import CrashGame, GameState
from game.core.game_manager import GameManager
from game.ui.components import HistorySquare, WinnerItem
import random


class CrashGameScreen(BaseGameScreen):
    
    def __init__(self, **kwargs):
        crash_game = CrashGame()
        game_manager = GameManager()
        game_manager.register_game('crash', crash_game)
        game_manager.set_current_game('crash')
        
        self.game_area = None
        super().__init__(crash_game, **kwargs)
        
        self.game.on_round_start = self.on_round_start
        self.game.on_multiplier_update = self.on_multiplier_update
        self.game.on_crash = self.on_crash
        self.game.on_auto_cashout = self.on_auto_cashout
        self.game.on_state_change = self.on_game_state_change
        
        self.names = [
            "An***ymous", "Pl***er", "Ga***r", "Lu***y", "Wi***r",
            "Cr***h", "Be***r", "Fa***t", "Bi***n", "Ac***e",
            "Ph***x", "Sh***w", "Vo***x", "Bl***e", "Ti***n",
            "Sp***e", "Ro***e", "Ze***h", "No***a", "St***r",
            "An***us", "Us***r", "Pl***r", "Ga***r", "Wi***r"
        ]
        
        self.start_new_round(0)
        Clock.schedule_interval(self.update_winners_display, 3)
    
    def on_kv_post(self, base_widget):
        self.game_area = self.ids.get('game_area')
        super().on_kv_post(base_widget)

    def _get_game_area_ids(self):
        if self.game_area and hasattr(self.game_area, 'ids'):
            return self.game_area.ids
        return {}

    def update_game_display(self):
        state = self.game.get_game_state()
        area_ids = self._get_game_area_ids()
        
        multiplier_display = area_ids.get('multiplier_display')
        if multiplier_display:
            multiplier_display.text = f"{state['multiplier']:.2f}x"
        
        round_status = area_ids.get('round_status')
        if round_status:
            round_status.text = state['round_status']
        
        countdown_label = area_ids.get('countdown')
        if countdown_label:
            countdown_text = ''
            if state['state'] == GameState.BETTING:
                countdown = int(state.get('countdown', 0))
                if countdown > 0:
                    countdown_text = f'Iniciando em {countdown}s'
            countdown_label.text = countdown_text
        
        self.update_history_display()
    
    def update_history_display(self):
        area_ids = self._get_game_area_ids()
        history_container = area_ids.get('history_container')
        if not history_container:
            return
        
        if not self.game.last_results:
            return
        
        current_count = len(history_container.children)
        results_count = len(self.game.last_results)
        
        if results_count > current_count:
            new_result = self.game.last_results[-1]
            history_square = HistorySquare()
            history_square.text = f'{new_result:.2f}'
            
            if new_result >= 10.0:
                history_square.md_bg_color = [0.2, 0.8, 0.4, 0.8]
            elif new_result >= 5.0:
                history_square.md_bg_color = [1.0, 0.6, 0.2, 0.8]
            elif new_result >= 2.0:
                history_square.md_bg_color = [0.3, 0.3, 0.3, 0.8]
            else:
                history_square.md_bg_color = [0.8, 0.2, 0.2, 0.8]
            
            history_container.add_widget(history_square, index=0)
            
            history_scroll = area_ids.get('history_scroll')
            if history_scroll:
                Clock.schedule_once(lambda dt: setattr(history_scroll, 'scroll_x', 0), 0.1)
    
    def on_round_start(self):
        self.animate_countdown()
    
    def on_multiplier_update(self, multiplier):
        pass
    
    def on_crash(self, crash_point):
        self.animate_plane_crash()
        Clock.schedule_once(self.start_new_round, 2)
    
    def on_auto_cashout(self, amount):
        self.game_manager.add_balance(amount)
        self.update_bets_display()
        self.update_balance_display()
    
    def on_game_state_change(self, state, countdown):
        if state == GameState.BETTING:
            if hasattr(self.ids, 'cashout_btn'):
                self.ids.cashout_btn.disabled = True
            if hasattr(self.ids, 'bet_button'):
                self.ids.bet_button.disabled = False
        elif state == GameState.FLYING:
            if hasattr(self.ids, 'bet_button'):
                self.ids.bet_button.disabled = True
        elif state == GameState.CRASHED:
            if hasattr(self.ids, 'cashout_btn'):
                self.ids.cashout_btn.disabled = True
            if hasattr(self.ids, 'bet_button'):
                self.ids.bet_button.disabled = True
    
    def start_new_round(self, dt):
        self.game.start_new_round()
        self.update_balance_display()
    
    def update_winners_display(self, dt):
        if not hasattr(self.ids, 'winners_bar'):
            return
        
        self.ids.winners_bar.clear_widgets()
        
        for i in range(5):
            name = random.choice(self.names)
            
            rand = random.random()
            if rand < 0.70:
                amount = random.uniform(50, 2000)
                multiplier = random.uniform(1.5, 8.0)
            elif rand < 0.95:
                amount = random.uniform(2000, 15000)
                multiplier = random.uniform(3.0, 25.0)
            else:
                amount = random.uniform(15000, 100000)
                multiplier = random.uniform(10.0, 50.0)
            
            winner_widget = WinnerItem(name=name, amount=amount, multiplier=multiplier)
            winner_widget.size_hint_x = 0.2
            self.ids.winners_bar.add_widget(winner_widget)
    
    def animate_plane_exit(self):
        multiplier_display = self._get_game_area_ids().get('multiplier_display')
        if not multiplier_display:
            return
        
        anim = Animation(text_color=[0, 1, 1, 1], duration=1)
        anim.start(multiplier_display)
        Clock.schedule_once(
            lambda dt: setattr(multiplier_display, 'text_color', [0, 1, 0, 1]),
            1.1
        )
    
    def animate_plane_crash(self):
        multiplier_display = self._get_game_area_ids().get('multiplier_display')
        if not multiplier_display:
            return
        
        anim = Animation(text_color=[1, 0, 0, 1], duration=0.5)
        anim.start(multiplier_display)
        Clock.schedule_once(lambda dt: self.restore_plane(), 2.0)
    
    def restore_plane(self):
        multiplier_display = self._get_game_area_ids().get('multiplier_display')
        if multiplier_display:
            multiplier_display.text_color = [0, 1, 0, 1]
    
    def animate_countdown(self):
        round_status = self._get_game_area_ids().get('round_status')
        if not round_status:
            return
        
        anim_status = Animation(
            text_color=[1.0, 0.8, 0.2, 1],
            duration=0.3
        ) + Animation(
            text_color=[0.9, 0.9, 0.9, 1],
            duration=0.3
        )
        anim_status.start(round_status)
    
    def cashout_all(self):
        super().cashout_all()
        self.animate_plane_exit()
