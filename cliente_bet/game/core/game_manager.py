from typing import Dict, Optional
from game.core.base_game import BaseGame


class GameManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._balance = 1000.0
        self._games: Dict[str, BaseGame] = {}
        self._current_game: Optional[BaseGame] = None
        self._initialized = True
    
    def get_balance(self) -> float:
        return self._balance
    
    def add_balance(self, amount: float):
        self._balance += amount
    
    def subtract_balance(self, amount: float) -> bool:
        if amount > self._balance:
            return False
        self._balance -= amount
        return True
    
    def register_game(self, name: str, game: BaseGame):
        self._games[name] = game
    
    def set_current_game(self, name: str) -> Optional[BaseGame]:
        if name in self._games:
            self._current_game = self._games[name]
            return self._current_game
        return None
    
    def get_current_game(self) -> Optional[BaseGame]:
        return self._current_game
