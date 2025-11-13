# 🎮 Plataforma de Jogos de Apostas

Uma plataforma de jogos de apostas modular desenvolvida com Kivy e KivyMD, com arquitetura preparada para múltiplos jogos.

**Projeto Acadêmico** - Desenvolvimento Rápido em Python  
Curso: Análise e Desenvolvimento de Sistemas (ADS) e Sistemas de Informação (SI)  
Instituição: UNIFACIMP

## � Jogos Disponíveis

### ✈️ Crash (Aviãozinho)
- **Multiplicadores em tempo real**: Acompanhe o multiplicador subindo
- **Auto-cashout**: Configure para sacar automaticamente em um multiplicador específico
- **Histórico infinito**: Veja todos os resultados anteriores com scroll
- **Barra de vencedores**: Veja outros jogadores ganhando em tempo real
- **Múltiplas apostas**: Faça várias apostas simultâneas com diferentes configurações

## 🚀 Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o jogo:
```bash
python main.py
```

## � Como Jogar - Crash

1. **Configure sua aposta**: Use os botões +/- ou digite o valor
2. **Defina auto-cashout (opcional)**: Ative e configure o multiplicador para saque automático
3. **Faça a aposta**: Clique em "JOGAR" durante a fase de apostas
4. **Acompanhe o voo**: Veja o multiplicador subindo
5. **Cashout manual**: Clique em "RETIRAR TUDO" antes do crash
6. **Resultado**: Ganhe ou perca baseado no crash point

## 📁 Arquitetura do Projeto

```
bet/
├── game/
│   ├── core/
│   │   ├── base_game.py          # Classe base abstrata para jogos
│   │   └── game_manager.py       # Gerenciador de jogos e saldo
│   ├── games/
│   │   └── crash.py              # Lógica do jogo Crash
│   └── ui/
│       └── components.py         # Componentes reutilizáveis
├── screens/
│   ├── base_game_screen.py       # Tela base com sistema de apostas
│   └── crash_game_screen.py      # Tela específica do Crash
├── layouts/
│   ├── base_game.kv             # Layout base reutilizável
│   └── games/
│       └── crash_game_area.kv   # Área específica do Crash
└── main.py                       # App principal
```

## � Funcionalidades

### Sistema de Apostas
- ✅ Saldo persistente entre rodadas
- ✅ Múltiplas apostas simultâneas
- ✅ Auto-cashout configurável
- ✅ Valores rápidos (10, 15, 100, ALL)
- ✅ Histórico de apostas ativas

### Interface
- ✅ Design moderno Material Design
- ✅ Fullscreen por padrão (1920x1080)
- ✅ Animações suaves
- ✅ Feedback visual em tempo real
- ✅ Histórico com scroll infinito
- ✅ Barra de vencedores animada

### Crash Game
- ✅ Sistema de estados (WAITING → BETTING → FLYING → CRASHED)
- ✅ Countdown para início da rodada
- ✅ Multiplicador em tempo real
- ✅ Algoritmo de crash realista
- ✅ Auto-cashout por aposta
- ✅ Histórico com cores por faixa de multiplicador

## 🔧 Tecnologias

- **Python 3.12+**
- **Kivy 2.3.1**: Framework de UI
- **KivyMD 1.2.0**: Material Design components
- **Arquitetura Modular**: Fácil adicionar novos jogos

## 📊 Probabilidades - Crash

| Multiplicador | Probabilidade |
|---------------|---------------|
| 1.0x - 2.0x   | ~50%         |
| 2.0x - 5.0x   | ~30%         |
| 5.0x - 10.0x  | ~15%         |
| 10.0x+        | ~5%          |

## 🎨 Cores do Histórico

- 🟢 **Verde** (≥10.0x): Vitória grande
- 🟠 **Laranja** (≥5.0x): Vitória média
- ⚪ **Cinza** (≥2.0x): Vitória pequena
- 🔴 **Vermelho** (<2.0x): Crash baixo

## 🚀 Adicionar Novos Jogos

O sistema foi projetado para facilitar a adição de novos jogos. Veja o guia completo em [COMO_ADICIONAR_JOGOS.md](COMO_ADICIONAR_JOGOS.md).

**Resumo:**
1. Criar classe do jogo herdando de `BaseGame`
2. Criar tela herdando de `BaseGameScreen`
3. Criar layouts KV específicos
4. Registrar no `main.py`

**Tempo estimado:** 1-2 horas para um jogo simples! 🎯

## 📱 Compatibilidade

- ✅ Linux
- ✅ Windows
- ✅ macOS
- 🔄 Android (com Buildozer)
- 🔄 iOS (com Buildozer)

## ⚠️ Aviso Legal

Este é um projeto educacional e de demonstração. Não incentivamos jogos de azar com dinheiro real. Use com responsabilidade!