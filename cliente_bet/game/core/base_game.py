from abc import ABC, abstractmethod
from typing import List, Optional


class BetItem:
    
    def __init__(self, amount: float, auto_cashout: Optional[float] = None):
        self.amount = amount
        self.auto_cashout = auto_cashout
        self.cashed_out = False
        self.cashout_multiplier = 0.0


class BaseGame(ABC):
    
    def __init__(self, name: str):
        self.name = name
        self.active_bets: List[BetItem] = []
    
    @abstractmethod
    def start_new_round(self):
        pass
    
    @abstractmethod
    def can_bet(self) -> bool:
        pass
    
    @abstractmethod
    def add_bet(self, amount: float, auto_cashout: Optional[float] = None) -> bool:
        pass
    
    @abstractmethod
    def cashout_all(self) -> float:
        pass
    
    @abstractmethod
    def clear_bets(self) -> float:
        pass
    
    @abstractmethod
    def get_game_state(self) -> dict:
        pass
    
    @abstractmethod
    def update(self, dt: float):
        pass
    
    @abstractmethod
    def cleanup(self):
        pass
    
    def get_active_bets_total(self) -> float:
        return sum(bet.amount for bet in self.active_bets if not bet.cashed_out)
