import pygame
import settings as cfg
from screens.game_screen import run as game_screen

def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()
    
    game_screen(screen, clock, level=1)
    pygame.quit()

if __name__ == "__main__":
    main()
