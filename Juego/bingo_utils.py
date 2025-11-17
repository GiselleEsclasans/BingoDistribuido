import random
import unicodedata

def get_letter_for_number(number):
    """Devuelve la letra de Bingo para un número dado."""
    if 1 <= number <= 15: return "B"
    if 16 <= number <= 30: return "I"
    if 31 <= number <= 45: return "N"
    if 46 <= number <= 60: return "G"
    if 61 <= number <= 75: return "O"
    return ""

def generar_carton():
    """
    Genera un cartón de bingo 5x5 estándar (24 números + 1 espacio libre).
    El cartón se devuelve como una lista plana de 25 elementos.
    """
    card = [0] * 25 
    

    col_b = random.sample(range(1, 16), 5)
    col_i = random.sample(range(16, 31), 5)
    col_n = random.sample(range(31, 46), 4) 
    col_g = random.sample(range(46, 61), 5)
    col_o = random.sample(range(61, 76), 5)

    for i in range(5): 
        card[i*5 + 0] = col_b[i] 
        card[i*5 + 1] = col_i[i] 
        
        if i < 2: 
            card[i*5 + 2] = col_n[i]
        elif i == 2:
            card[i*5 + 2] = 0 
        else: 
            card[i*5 + 2] = col_n[i-1] 
            
        card[i*5 + 3] = col_g[i] 
        card[i*5 + 4] = col_o[i] 
            
    return card


def verificar_patron_ganador(carton, numeros_marcados, modo_juego):
    """
    Verifica si un cartón tiene patrón ganador (Lógica del Servidor).
    El espacio libre (0) se considera siempre marcado.
    """
    
    marcados_set = set(numeros_marcados)
    
    try:
        modo_norm = unicodedata.normalize('NFKD', str(modo_juego)).encode('ascii', 'ignore').decode('ascii').lower()
    except Exception:
        modo_norm = str(modo_juego).lower()

    carton_marcado = [carton[i] == 0 or carton[i] in marcados_set for i in range(25)]

    try:
        print(f"DEBUG verificar_patron_ganador - modo={modo_juego}")
        print(f"  carton: {carton}")
        print(f"  marcados_set: {sorted(list(marcados_set))}")
        print(f"  carton_marcado: {carton_marcado}")
    except Exception:
        pass

    if modo_norm == "rapido":
        lineas = [
            [0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24],
            [0, 5, 10, 15, 20], [1, 6, 11, 16, 21], [2, 7, 12, 17, 22], [3, 8, 13, 18, 23], [4, 9, 14, 19, 24],
            [0, 6, 12, 18, 24], [4, 8, 12, 16, 20]
        ]
    
        for linea in lineas:
            vals = [carton_marcado[i] for i in linea]
            print(f"  comprobando linea {linea}: {vals} -> {all(vals)}")
        return any(all(carton_marcado[i] for i in linea) for linea in lineas)
        
    elif modo_norm == "regular":
        patron_regular = [0, 4, 12, 20, 24]
        return all(carton_marcado[i] for i in patron_regular)
        
    elif modo_norm == "blackout":
        return all(carton_marcado)
    
    return False