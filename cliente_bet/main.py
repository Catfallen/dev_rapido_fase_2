from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from screens.crash_game_screen import CrashGameScreen


class CasinoApp(MDApp):
    
    def build(self):
        self.title = 'Casino - Crash Game'
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        Window.size = (1920, 1080)
        Builder.load_file('layouts/base_game.kv')
        return CrashGameScreen(name='crash')


if __name__ == '__main__':
    CasinoApp().run()
