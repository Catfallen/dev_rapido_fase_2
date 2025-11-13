# bet/screens/over_under_screen.py
from kivy.animation import Animation
from kivy.clock import Clock
from screens.base_game_screen import BaseGameScreen
from game.ui.components import show_snackbar, HistorySquare

class OverUnderScreen(BaseGameScreen):
    
    def __init__(self, game_instance, game_manager, **kwargs):
        self.game_area = None
        super().__init__(game_instance=game_instance, game_manager=game_manager, **kwargs)
        
    
    # --- AQUI ESTÁ A CORREÇÃO ---
    def on_kv_post(self, base_widget):
        # 1. Chame o super() PRIMEIRO. Isso preenche o self.ids
        super().on_kv_post(base_widget) 
        
        # 2. AGORA você pode pegar os IDs com segurança
        self.game_area = self.ids.get('game_area')
        
        # Esconde o painel de auto-cashout que não usamos
        if hasattr(self.ids, 'auto_cashout_box'):
            self.ids.auto_cashout_box.size_hint_y = None
            self.ids.auto_cashout_box.height = 0
            self.ids.auto_cashout_box.opacity = 0
    # --- FIM DA CORREÇÃO ---
            
    def add_bet(self):
        # Sobrescreve a função add_bet da BaseGameScreen
        # para mostrar o aviso correto
        show_snackbar('Aposte usando os botões MENOR, IGUAL ou MAIOR.')

    def place_bet(self, bet_type):
        """ Chamada pelos 3 botões (Menor, Igual, Maior) """
        bet_amount = self.bet_amount # Pega o valor da BaseGameScreen
        
        # Chama a lógica do jogo
        result = self.game.place_bet(bet_type, bet_amount)
        
        if result.get('error'):
            show_snackbar(result['error'])
            return
            
        self.update_balance_display() # Atualiza o saldo (função da Base)
        show_snackbar(f"Resultado: {result['result']}! Você ganhou R$ {result['winnings']:.2f}")
        self.update_game_display(result) # Atualiza os dados e histórico

    # --- VERSÃO LIMPA SEM DEBUG ---
    def update_game_display(self, last_result=None):
        """ Atualiza os dados e o histórico """
        
        # Se formos chamados sem um resultado (pelo update_loop), não fazemos NADA.
        # O código abaixo só vai rodar UMA VEZ por aposta.
        if not last_result:
            return 

        if not self.game_area:
            return # Segurança
            
        area_ids = self.game_area.ids
        
        # 1. Atualiza as imagens dos dados
        dice1_img = f"assets/dice_{last_result['dice'][0]}.png"
        dice2_img = f"assets/dice_{last_result['dice'][1]}.png"
        
        dice_widget_1 = area_ids.get('dice_1')
        dice_widget_2 = area_ids.get('dice_2')
        
        if dice_widget_1:
            dice_widget_1.source = dice1_img
            dice_widget_1.reload()
            self.animate_dice(dice_widget_1)
        
        if dice_widget_2:
            dice_widget_2.source = dice2_img
            dice_widget_2.reload()
            self.animate_dice(dice_widget_2)
        
        # 2. Atualiza o histórico
        history_container = area_ids.get('history_container')
        if not history_container: return
        
        new_result_val = last_result['result'] # Pega o número do dict
        is_win = last_result['is_win']         # Pega o status da vitória
        
        history_square = HistorySquare()
        history_square.text = str(new_result_val)
        
        # --- LÓGICA DE COR CORRIGIDA ---
        if is_win:
            # Se você ganhou, a cor é VERDE
            history_square.md_bg_color = [0.2, 0.8, 0.4, 0.8] # Verde
        else:
            # Se você perdeu...
            if new_result_val == 7:
                # ... mas o resultado foi 7, a cor é DOURADA
                history_square.md_bg_color = [1.0, 0.6, 0.2, 0.8] # Dourado
            else:
                # ... e o resultado não foi 7, a cor é VERMELHA
                history_square.md_bg_color = [0.8, 0.2, 0.2, 0.8] # Vermelho
        
        history_container.add_widget(history_square, index=0)

    def animate_dice(self, widget):
        # Nova animação: pisca o dado (opacidade)
        anim = (
            Animation(opacity=0.5, duration=0.1) +
            Animation(opacity=1.0, duration=0.1)
        )
        anim.start(widget)