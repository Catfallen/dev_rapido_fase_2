from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
import json
import os

# carrega o arquivo .kv no mesmo diretório deste script
#Builder.load_file(os.path.join(os.path.dirname(__file__), 'login_screen.kv'))

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        # Define o título da janela quando esta tela é aberta
        self.app.title = 'Casino - Login'

    def login(self):
        # Pega os valores dos campos
        email = self.ids.email.text.strip()
        senha = self.ids.senha.text.strip()
        
        # Validação básica
        if not email or not senha:
            Snackbar(text="Preencha email e senha!").open()
            return
        
        # Body para login (nome não é necessário, mas incluído como vazio)
        body = json.dumps({"nome": "", "email": email, "senha": senha})
        
        # Faz a requisição POST para login
        UrlRequest(
            'http://localhost:3000/auth/login',
            method='POST',
            req_body=body,
            req_headers={'Content-Type': 'application/json'},
            on_success=self.on_login_success,
            on_failure=self.on_request_failure,
            on_error=self.on_request_error
        )

    def register(self):
        # Pega os valores dos campos
        nome = self.ids.nome.text.strip()
        email = self.ids.email.text.strip()
        senha = self.ids.senha.text.strip()
        
        # Validação básica
        if not nome or not email or not senha:
            Snackbar(text="Preencha nome, email e senha!").open()
            return
        
        # Body para registro
        body = json.dumps({"nome": nome, "email": email, "senha": senha})
        
        # Faz a requisição POST para registro
        UrlRequest(
            'http://localhost:3000/auth/register',
            method='POST',
            req_body=body,
            req_headers={'Content-Type': 'application/json'},
            on_success=self.on_register_success,
            on_failure=self.on_request_failure,
            on_error=self.on_request_error
        )

    def on_login_success(self, req, result):
        try:
            token = result.get('token')
            user = result.get('user')
            if token:
                self.app.token = token
                Snackbar(text=f"Bem-vindo, {user.get('email', 'Usuário')}!").open()
            # troca para tela principal
                self.manager.current = 'selection'
            else:
                Snackbar(text="Erro: Token não recebido.").open()
        except Exception as e:
            Snackbar(text=f"Erro ao processar resposta: {str(e)}").open()

    def on_register_success(self, req, result):
        try:
            token = result.get('token')
            user = result.get('user')
            if token:
                self.app.token = token
                Snackbar(text=f"Registro bem-sucedido! Bem-vindo, {user.get('email', 'Usuário')}!").open()
                self.manager.current = 'selection'
            else:
                Snackbar(text="Erro: Token não recebido.").open()
        except Exception as e:
            Snackbar(text=f"Erro ao processar resposta: {str(e)}").open()

    def on_request_failure(self, req, result):
        Snackbar(text="Falha na requisição. Verifique a conexão.").open()

    def on_request_error(self, req, error):
        Snackbar(text=f"Erro na requisição: {str(error)}").open()