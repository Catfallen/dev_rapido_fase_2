# bet/game/games/over_under.py
import random
from game.core.base_game import BaseGame
from game.core.game_manager import GameManager
from game.ui.components import show_snackbar

class OverUnderGame(BaseGame):
    def __init__(self, name, game_manager):
        super().__init__(name) # Passa o nome para a classe base
        
        # Recebe o gerenciador central, não cria um novo
        self.game_manager = game_manager 
        self.last_results = []

    def place_bet(self, bet_type, amount):
        if amount <= 0 or amount > self.game_manager.get_balance():
            return {'error': 'Valor de aposta inválido ou saldo insuficiente.'}
        
        self.game_manager.subtract_balance(amount)
        
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        result = dice1 + dice2
        
        self.last_results.append(result)
        if len(self.last_results) > 20:
            self.last_results.pop(0)
            
        winnings = 0
        is_win = False
        
        if bet_type == 'under' and result < 7:
            winnings = amount * 2
            is_win = True
        elif bet_type == 'over' and result > 7:
            winnings = amount * 2
            is_win = True
        elif bet_type == 'seven' and result == 7:
            winnings = amount * 5
            is_win = True
            
        if is_win:
            self.game_manager.add_balance(winnings)
            
        return {
            'error': None,
            'is_win': is_win,
            'winnings': winnings,
            'dice': [dice1, dice2],
            'result': result,
            'bet_type': bet_type
        }

    # --- CUMPRINDO O CONTRATO DA BASEGAME ---
    def can_bet(self):
        return False # Usamos nossos próprios botões

    def start_new_round(self):
        pass # Jogo instantâneo

    def cleanup(self):
        pass # Jogo instantâneo
    
    def clear_bets(self):
        return 0 # Jogo instantâneo

    def update(self, dt):
        pass # Jogo instantâneo

    def get_game_state(self):
        return {'state': 'IDLE'}
    
    def add_bet(self, amount, auto_cashout=None):
        # Bloqueia o botão "JOGAR" principal
        show_snackbar('Por favor, escolha MENOR, IGUAL ou MAIOR para apostar.')
        return False 

    def cashout_all(self):
        return 0