import random
from typing import List, Dict, Set, Optional

class BingoGame:
    """
    Clase principal para manejar la lógica del juego Bingo
    Soporta múltiples modos de juego y verificación de patrones
    """
    
    def __init__(self, player_name: str, game_mode: str, players_count: int = 2):
        self.player_name = player_name
        self.game_mode = game_mode
        self.players_count = players_count
        self.card = self._generate_card()
        self.marked_numbers: Set[int] = set()
        self.drawn_numbers: List[int] = []
        self.is_winner = False
        self.winning_patterns = self._initialize_winning_patterns()
        self.winning_pattern_name = ""
        
    def _generate_card(self) -> List[int]:
        """Genera un cartón de Bingo único de 3x5 números"""
        card = []
        while len(card) < 15:
            num = random.randint(1, 75)
            if num not in card:
                card.append(num)
        return card
    
    def _initialize_winning_patterns(self) -> Dict[str, List[int]]:
        """Inicializa los patrones ganadores según el modo de juego"""
        patterns = {}
        
        if self.game_mode == "rapido":
            patterns = {
                'linea_1': [0, 1, 2, 3, 4],
                'linea_2': [5, 6, 7, 8, 9],
                'linea_3': [10, 11, 12, 13, 14],
                'columna_1': [0, 5, 10],
                'columna_2': [1, 6, 11],
                'columna_3': [2, 7, 12],
                'columna_4': [3, 8, 13],
                'columna_5': [4, 9, 14],
                'diagonal_principal': [0, 6, 12, 8, 4],
                'diagonal_secundaria': [2, 6, 10]
            }
        elif self.game_mode == "regular":
            patterns = {
                'carton_completo': list(range(15))
            }
        elif self.game_mode == "blackout":
            patterns = {
                'esquinas': [0, 4, 10, 14],
                'cruz_central': [1, 6, 7, 8, 11, 12, 13],
                'marco_completo': [0, 1, 2, 3, 4, 5, 9, 10, 14]
            }
        
        return patterns
    
    def mark_number(self, number: int) -> bool:
        """
        Marca un número en el cartón si está presente
        Retorna True si el número estaba en el cartón y fue marcado
        """
        if number in self.card and number not in self.marked_numbers:
            self.marked_numbers.add(number)
            if number not in self.drawn_numbers:
                self.drawn_numbers.append(number)
            return True
        return False
    
    def check_winning_condition(self) -> bool:
        """Verifica si el jugador cumple con alguna condición ganadora"""
        if self.game_mode == "rapido":
            return self._check_quick_mode()
        elif self.game_mode == "regular":
            return self._check_regular_mode()
        elif self.game_mode == "blackout":
            return self._check_blackout_mode()
        return False
    
    def _check_quick_mode(self) -> bool:
        """Verifica patrones para modo rápido"""
        for pattern_name, pattern in self.winning_patterns.items():
            if all(self.card[idx] in self.marked_numbers for idx in pattern):
                self.winning_pattern_name = pattern_name
                self.is_winner = True
                return True
        return False
    
    def _check_regular_mode(self) -> bool:
        """Verifica si el cartón está completo"""
        if len(self.marked_numbers) == len(self.card):
            self.winning_pattern_name = "carton_completo"
            self.is_winner = True
            return True
        return False
    
    def _check_blackout_mode(self) -> bool:
        """Verifica patrones para modo blackout"""
        for pattern_name, pattern in self.winning_patterns.items():
            if all(self.card[idx] in self.marked_numbers for idx in pattern):
                self.winning_pattern_name = pattern_name
                self.is_winner = True
                return True
        return False
    
    def get_card_display(self) -> List[List[int]]:
        """Retorna el cartón en formato 3x5 para visualización"""
        card_2d = []
        for i in range(3):
            row = self.card[i*5:(i+1)*5]
            card_2d.append(row)
        return card_2d
    
    def get_marked_card_display(self) -> List[List[bool]]:
        """Retorna una matriz 3x5 indicando qué números están marcados"""
        marked_2d = []
        for i in range(3):
            row = []
            for j in range(5):
                idx = i * 5 + j
                row.append(self.card[idx] in self.marked_numbers)
            marked_2d.append(row)
        return marked_2d
    
    def get_progress(self) -> Dict[str, float]:
        """Retorna el progreso del juego en porcentaje"""
        total_numbers = len(self.card)
        marked_count = len(self.marked_numbers)
        
        progress_data = {
            'total_numbers': total_numbers,
            'marked_numbers': marked_count,
            'percentage': (marked_count / total_numbers) * 100 if total_numbers > 0 else 0,
            'remaining_numbers': total_numbers - marked_count
        }
        
        return progress_data
    
    def get_game_stats(self) -> Dict[str, any]:
        """Retorna estadísticas del juego"""
        return {
            'player_name': self.player_name,
            'game_mode': self.game_mode,
            'total_players': self.players_count,
            'is_winner': self.is_winner,
            'winning_pattern': self.winning_pattern_name,
            'numbers_drawn': len(self.drawn_numbers),
            'numbers_marked': len(self.marked_numbers),
            'card_numbers': self.card,
            'marked_numbers': list(self.marked_numbers),
            'drawn_numbers': self.drawn_numbers
        }
    
    def reset_game(self):
        """Reinicia el juego manteniendo el mismo cartón"""
        self.marked_numbers.clear()
        self.drawn_numbers.clear()
        self.is_winner = False
        self.winning_pattern_name = ""

def get_pattern_description(pattern_name: str, game_mode: str) -> str:
    """Retorna una descripción legible del patrón ganador"""
    descriptions = {
        "rapido": {
            "linea_1": "Línea superior completa",
            "linea_2": "Línea central completa", 
            "linea_3": "Línea inferior completa",
            "columna_1": "Columna izquierda completa",
            "columna_5": "Columna derecha completa",
            "diagonal_principal": "Diagonal principal completa",
            "diagonal_secundaria": "Diagonal secundaria completa"
        },
        "regular": {
            "carton_completo": "Cartón completo"
        },
        "blackout": {
            "esquinas": "Cuatro esquinas",
            "cruz_central": "Cruz central", 
            "marco_completo": "Marco completo"
        }
    }
    
    return descriptions.get(game_mode, {}).get(pattern_name, pattern_name)