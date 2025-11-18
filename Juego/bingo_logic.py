import random
from typing import List, Dict, Set, Optional

class BingoGame:
    """
    Clase de lógica del cliente para verificar el cartón (versión 5x5 BINGO).
    """
    
    def __init__(self, player_name: str, game_mode: str, players_count: int = 2):
        self.player_name = player_name
        self.game_mode = game_mode.lower()
        self.players_count = players_count
        self.card: List[int] = [] 
        
        self.marked_numbers: Set[int] = {0} 
        
        self.is_winner = False
        self.winning_pattern_name = ""
        
    def mark_number(self, number: int) -> bool:
        """Marca un número en el set local de números marcados."""
        if number in self.card and number not in self.marked_numbers:
            self.marked_numbers.add(number)
            return True
        return False
    
    def check_winning_condition(self) -> bool:
        """Verifica si el jugador cumple con alguna condición ganadora."""
        
        if not self.card or len(self.card) != 25:
             print("Error: check_winning_condition se llamó antes de asignar un cartón 5x5.")
             return False

        carton_marcado = [self.card[i] in self.marked_numbers for i in range(25)]

        if self.game_mode == "regular":
            return self._check_line(carton_marcado)
        elif self.game_mode == "doble_diagonal" or self.game_mode == "doble diagonal":
            return self._check_doble_diagonal(carton_marcado)
        elif self.game_mode == "blackout":
            return self._check_blackout(carton_marcado)
        return False
    
    def _check_line(self, carton_marcado: List[bool]) -> bool:
        """Verifica patrones para modo rápido (cualquier línea)"""
        lineas = [
            # Horizontales
            [0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24],
            # Verticales
            [0, 5, 10, 15, 20], [1, 6, 11, 16, 21], [2, 7, 12, 17, 22], [3, 8, 13, 18, 23], [4, 9, 14, 19, 24],
            # Diagonales
            [0, 6, 12, 18, 24], [4, 8, 12, 16, 20]
        ]
        if any(all(carton_marcado[i] for i in linea) for linea in lineas):
            self.winning_pattern_name = "linea"
            self.is_winner = True
            return True
        return False
    
    def _check_doble_diagonal(self, carton_marcado: List[bool]) -> bool:
        """Verifica ambas diagonales (patrón en X)"""
        diagonal_principal = [0, 6, 12, 18, 24]
        diagonal_secundaria = [4, 8, 12, 16, 20]
        
        if all(carton_marcado[i] for i in diagonal_principal) and all(carton_marcado[i] for i in diagonal_secundaria):
            self.winning_pattern_name = "doble_diagonal"
            self.is_winner = True
            return True
        return False
    
    def _check_blackout(self, carton_marcado: List[bool]) -> bool:
        """Verifica cartón lleno"""
        if all(carton_marcado):
            self.winning_pattern_name = "carton_lleno"
            self.is_winner = True
            return True
        return False

def get_pattern_description(pattern_name: str, game_mode: str) -> str:
    """Retorna una descripción legible del patrón ganador (versión 5x5)"""
    descriptions = {
        "regular": {
            "linea": "Línea completa",
        },
        "doble_diagonal": {
            "doble_diagonal": "Doble Diagonal (X)"
        },
        "doble diagonal": {
            "doble_diagonal": "Doble Diagonal (X)"
        },
        "blackout": {
            "carton_lleno": "Cartón Lleno (Blackout)"
        }
    }
    return descriptions.get(game_mode, {}).get(pattern_name, pattern_name.replace("_", " ").capitalize())