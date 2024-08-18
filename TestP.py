import os
import pygame
from pytmx.util_pygame import load_pygame
import sys

# Zjistěte aktuální pracovní adresář
print("Aktuální pracovní adresář:", os.getcwd())

# Zadejte cestu k mapovému souboru
map_file = 'C:/Users/vojta/OneDrive/Documents/skolni-chat-flet/games/bezjmena.tmx'  # nebo použijte absolutní cestu


# Načtení mapy
def load_map(filename):
    try:
        tmx_data = load_pygame(filename)
        print(f"Mapa {filename} úspěšně načtena")
        return tmx_data
    except Exception as e:
        print(f"Chyba při načítání mapy {filename}: {e}")
        sys.exit()


# Spuštění kódu
pygame.init()
screen = pygame.display.set_mode((800, 600))
tmx_data = load_map(map_file)
