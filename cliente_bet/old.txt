from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
import os

# Importa as lógicas dos jogos
from game.core.game_manager import GameManager
from game.games.crash import CrashGame
from game.games.over_under import OverUnderGame

# Importa as telas
from screens.login_screen import LoginScreen       # Tela de login (nova)
from screens.selection_screen import SelectionScreen
from screens.crash_game_screen import CrashGameScreen
from screens.over_under_screen import OverUnderScreen


class CasinoApp(MDApp):
    game_manager = None
    token = None  # Token JWT armazenado após login

    def build(self):
        self.title = 'Casino'
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        Window.size = (1920, 1080)
        # Window.fullscreen = 'auto'

        # --- CARREGA OS ARQUIVOS KV ---
        kv_files = [
            'layouts/login_screen.kv',
            'layouts/selection_screen.kv',
            'layouts/base_game.kv',
            'layouts/over_under.kv'
        ]

        base_path = os.path.dirname(os.path.abspath(__file__))

        for kv in kv_files:
            path = os.path.join(base_path, kv)
            if os.path.exists(path):
                Builder.load_file(path)
            else:
                print(f"⚠️ Arquivo KV não encontrado: {path}")

        # --- ARQUITETURA CENTRAL ---
        self.game_manager = GameManager()

        crash_game_instance = CrashGame(name='crash', game_manager=self.game_manager)
        over_under_game_instance = OverUnderGame(name='over_under', game_manager=self.game_manager)

        self.game_manager.register_game('crash', crash_game_instance)
        self.game_manager.register_game('over_under', over_under_game_instance)

        # --- GERENCIADOR DE TELAS ---
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))  # Adiciona tela de login
        sm.add_widget(SelectionScreen(name='selection'))
        sm.add_widget(CrashGameScreen(
            name='crash',
            game_instance=crash_game_instance,
            game_manager=self.game_manager
        ))
        sm.add_widget(OverUnderScreen(
            name='over_under',
            game_instance=over_under_game_instance,
            game_manager=self.game_manager
        ))

        # Tela inicial: LOGIN
        sm.current = 'login'

        return sm


if __name__ == '__main__':
    CasinoApp().run()
