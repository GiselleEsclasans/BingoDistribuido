import random

def generar_carton():
    """Generar un cartón de bingo 5x5 con números únicos"""
    carton = []
    while len(carton) < 25: 
        num = random.randint(1, 75)
        if num not in carton:
            carton.append(num)
    return carton

def verificar_patron_ganador(carton, numeros_marcados, modo_juego):
    """Verificar si un cartón tiene patrón ganador"""
    
    marcados_set = set(numeros_marcados)
    carton_marcado = [carton[i] in marcados_set for i in range(25)]

    if modo_juego == "rapido":
        lineas = [
            [0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24],
            [0, 5, 10, 15, 20], [1, 6, 11, 16, 21], [2, 7, 12, 17, 22], [3, 8, 13, 18, 23], [4, 9, 14, 19, 24],
            [0, 6, 12, 18, 24], [4, 8, 12, 16, 20]
        ]
        return any(all(carton_marcado[i] for i in linea) for linea in lineas)
        
    elif modo_juego == "regular":
        patron_regular = [0, 4, 12, 20, 24]
        return all(carton_marcado[i] for i in patron_regular)
        
    elif modo_juego == "blackout":
        return all(carton_marcado)
    
    return False