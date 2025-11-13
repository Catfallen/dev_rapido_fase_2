# Arquivo: main.py
# Versão ajustada: adiciona suporte ao evento "history_update" e usa Clock.schedule_once
# para garantir atualizações de UI na thread principal.

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
import socketio

# Configurações da janela
Window.size = (500, 600)
Window.title = "Crash Game"

class CrashGameApp(App):
    def build(self):
        self.socket = socketio.Client()
        self.setup_socket_events()
        
        # Conecta automaticamente ao servidor, como no código original
        try:
            self.socket.connect("http://localhost:3000")  # Ajuste a URL se necessário
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Parte superior: multiplicador e status
        top_layout = BoxLayout(orientation='vertical', spacing=20, size_hint_y=0.7)

        # Multiplicador
        self.multiplier_label = Label(
            text="1.00x",
            font_size=80,
            color=(0, 1, 0, 1),  # Verde
            bold=True,
            size_hint_y=0.6
        )
        top_layout.add_widget(self.multiplier_label)

        # Status e Contagem
        status_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        self.round_status_label = Label(
            text="Aguardando...",
            font_size=18,
            color=(0.8, 0.8, 0.8, 1),
            halign='center'
        )
        self.countdown_label = Label(
            text="",
            font_size=20,
            color=(1, 0.5, 0, 1),  # Laranja
            bold=True,
            halign='center'
        )
        status_layout.add_widget(self.round_status_label)
        status_layout.add_widget(self.countdown_label)
        top_layout.add_widget(status_layout)

        main_layout.add_widget(top_layout)

        # Histórico
        history_scroll = ScrollView(size_hint_y=0.2, do_scroll_x=True, do_scroll_y=False)
        self.history_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=500, spacing=10, padding=10)
        self.history_layout.bind(minimum_width=self.history_layout.setter('width'))
        history_scroll.add_widget(self.history_layout)
        main_layout.add_widget(history_scroll)

        # Autenticação
        auth_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.1)
        self.token_input = TextInput(
            hint_text="Digite seu token JWT",
            multiline=False,
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1)
        )
        auth_layout.add_widget(self.token_input)

        self.auth_button = Button(
            text="Conectar",
            background_color=(0, 0.6, 0, 1),
            size_hint_y=0.5
        )
        self.auth_button.bind(on_press=self.authenticate)
        auth_layout.add_widget(self.auth_button)

        main_layout.add_widget(auth_layout)

        # Removi a simulação automática de histórico (vamos receber via websocket)
        # Clock.schedule_interval(self.add_random_history, 5)

        return main_layout

    def setup_socket_events(self):
        @self.socket.event
        def connect():
            print("Conectado ao servidor")

        @self.socket.event
        def disconnect():
            print("Desconectado do servidor")

        @self.socket.on("autenticado")
        def on_autenticado(data):
            # atualiza UI na main thread apenas mensagem de debug
            Clock.schedule_once(lambda dt: print(f"Usuário autenticado: {data.get('userId')}"))

        @self.socket.on("erro_autenticacao")
        def on_erro_autenticacao(data):
            Clock.schedule_once(lambda dt: print(f"Erro: {data.get('msg')}"))

        @self.socket.on("state_change")
        def on_state_change(data):
            # Agendar atualização de UI
            Clock.schedule_once(lambda dt: self._handle_state_change(data))

        @self.socket.on("multiplier_update")
        def on_multiplier_update(data):
            Clock.schedule_once(lambda dt: self._handle_multiplier_update(data))

        @self.socket.on("crash")
        def on_crash(data):
            # data pode ter 'at' ou 'crashPoint'
            Clock.schedule_once(lambda dt: self._handle_crash(data))

        @self.socket.on("round_start")
        def on_round_start(data=None):  # Aceita data opcional
            Clock.schedule_once(lambda dt: self._handle_round_start(data))

        @self.socket.on("cashout_all")
        def on_cashout_all(data):
            Clock.schedule_once(lambda dt: print("💸 Cashout recebido:", data))

        @self.socket.on("auto_cashout")
        def on_auto_cashout(data):
            Clock.schedule_once(lambda dt: print("Auto cashout:", data.get('value') or data.get('ganhos')))

        # Novo: history_update
        @self.socket.on("history_update")
        def on_history_update(data):
            Clock.schedule_once(lambda dt: self._handle_history_update(data))

    # -------------------------
    # Handlers que executam na UI thread
    # -------------------------
    def _handle_state_change(self, data):
        state = data.get('state')
        countdown = data.get('countdown')
        if state is not None:
            self.round_status_label.text = state
        if countdown is not None:
            self.countdown_label.text = str(countdown)
        else:
            self.countdown_label.text = ""

    def _handle_multiplier_update(self, data):
        mult = data.get('multiplier')
        try:
            self.multiplier_label.text = f"{float(mult):.2f}x"
        except Exception:
            # caso venha em formato inesperado
            self.multiplier_label.text = "1.00x"

    def _handle_crash(self, data):
        at_value = None
        # compatibilidade com 'at' ou 'crashPoint'
        if isinstance(data, dict):
            at_value = data.get('at') or data.get('crashPoint')
        try:
            at_value = float(at_value) if at_value is not None else None
        except Exception:
            at_value = None

        if at_value is not None:
            self.round_status_label.text = f"💥 Crash em {at_value:.2f}x!"
            self.multiplier_label.text = f"{at_value:.2f}x"
        else:
            print("⚠️ Evento 'crash' recebido sem 'at' nem 'crashPoint':", data)
            self.round_status_label.text = "💥 Crash!"

        # efeito visual temporário
        self.multiplier_label.color = (1, 0, 0, 1)  # vermelho
        Clock.schedule_once(lambda dt: setattr(self.multiplier_label, 'color', (0, 1, 0, 1)), 1)

    def _handle_round_start(self, data):
        self.round_status_label.text = "Rodada iniciada!"
        self.multiplier_label.text = "1.00x"
        self.countdown_label.text = str(data.get('countdown')) if isinstance(data, dict) and data.get('countdown') is not None else ""

    def _handle_history_update(self, data):
        # espera um dict { "history": [valores...] } (se vier apenas lista, tenta usar ela)
        hist = []
        if isinstance(data, dict):
            hist = data.get('history') or data.get('lastCrashes') or []
        elif isinstance(data, list):
            hist = data
        # valida e transforma em floats
        cleaned = []
        for v in hist:
            try:
                cleaned.append(float(v))
            except Exception:
                pass
        # limpa e preenche UI (mostrando do mais recente para o mais antigo, conforme HTML)
        self.history_layout.clear_widgets()
        for value in reversed(cleaned):
            self.add_history_item(value)

    def authenticate(self, instance):
        token = self.token_input.text.strip()
        if not token:
            print("Digite um token!")
            return
        if self.socket.connected:
            self.socket.emit("autenticar", token)
        else:
            print("Socket não conectado. Tente novamente.")

    # -------------------------
    # Histórico UI
    # -------------------------
    def add_history_item(self, value):
        # Usa Button desabilitado para suportar background_color
        button = Button(
            text=f"{value:.2f}x",
            size_hint_x=None,
            width=80,
            font_size=14,
            bold=True,
            color=(1, 1, 1, 1),
            background_color=(0, 0.6, 0, 1) if value >= 2 else (0.6, 0, 0, 1),
            disabled=True  # Desabilita para não agir como botão
        )
        self.history_layout.add_widget(button)

    # (opcional) utilitário de debug
    def add_random_history(self, dt):
        import random
        value = random.uniform(0, 5)
        self.add_history_item(value)

if __name__ == "__main__":
    CrashGameApp().run()
