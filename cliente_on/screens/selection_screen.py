# bet/screens/selection_screen.py
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.app import App
class SelectionScreen(Screen):
    def on_enter(self):
        # Define o título da janela quando esta tela é aberta
        app = MDApp.get_running_app()
        app2 = App.get_running_app()
        
        token = app.token
        app.title = f'Casino - Seleção de Jogos {token}'

    def go_to_game(self, game_name):
        # Esta função será chamada pelos botões no .kv
        # 'app.root' será o nosso ScreenManager
        app = MDApp.get_running_app()
        
        # Pega o gerenciador central de saldo
        game_manager = app.game_manager 
        
        # Define o jogo atual no gerenciador antes de trocar de tela
        game_manager.set_current_game(game_name)
        
        # Troca a tela
        app.root.current = game_name