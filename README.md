# dev_rapido_fase_2
**Fase 2 do projeto Casa de apostas da disciplina _Desenvolvimento Rápido de Aplicações em Python_**

A primeira fase do projeto consistia na criação de uma **casa de apostas** em um curto período de uma semana.  
Nesta segunda fase, o objetivo foi **refatorar e aprimorar** o código desenvolvido por outro grupo.

---

## Tecnologias Utilizadas
- **Front-end:** Python (Kivy)  
- **Back-end:** Node.js (Express)  

---

## Melhorias Implementadas

### 🔌 Conexão em Tempo Real (WebSocket)
Foi criada uma conexão em tempo real utilizando WebSocket.  
O cliente original foi usado para **emitir eventos para o servidor**, permitindo que outros clientes — como a versão em HTML — visualizassem as atualizações do jogo **em tempo real**.

### 🔐 Tela de Login e Autenticação
Implementamos uma tela de login responsável pela **geração de tokens**.  
Com o token, é possível diferenciar os jogadores tanto pelo **ID do socket** quanto pelo **ID real** contido no token JWT.

---

