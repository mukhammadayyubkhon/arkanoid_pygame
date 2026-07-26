import pygame
import settings as cfg
import random

class Paddle:
    """ Our main player, Paddle, moves only horizontally. """

    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, cfg.PADDLE_WIDTH, cfg.PADDLE_HEIGHT)
        self.rect.midbottom = (cfg.WIDTH // 2, cfg.HEIGHT - 20)
        self.speed = cfg.PADDLE_SPEED
        self.vx = 0
        self.extended = False
        self.laser = False

    def move(self, keys: pygame.key.ScancodeWrapper):
        """ Moves the Paddle if the key is pressed. """
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
        
        self.rect.x += self.vx

        # Restrict the Paddle's movement
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders the Paddle on the screen. """
        pygame.draw.rect(screen, cfg.PADDLE_COLOR, self.rect, border_radius=5)
    
    def shrink(self):
        """Уменьшает ширину платформы"""
        self.rect.width = max(40, self.rect.width * 0.7)


class Brick:
    """
        Class for Game's brick.

        HP = -1: Level Boundary
        HP = 0: Indestructable
        HP = 1, 2: One / Two hit
    """
    
    def __init__(self, col: int, row: int, hp: int) -> None:
        self.hp = hp
        self.color = cfg.BRICK_COLORS[hp]
        self.rect = pygame.Rect(
            cfg.FIELD_LEFT + col * cfg.BRICK_WIDTH,
            cfg.TOP_OFFSET + row * cfg.BRICK_HEIGHT,
            cfg.BRICK_WIDTH,
            cfg.BRICK_HEIGHT,
        )

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders a Brick in a certain row and col. """
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)
    
    def hit(self) -> None:
        """ Handles the Brick Hit. """
        if self.hp > 0:
            self.hp -= 1
            if self.hp > 0:
                self.color = cfg.BRICK_COLORS[self.hp]
                return
        return


class Ball:
    """ Ball Actor class. """

    def __init__(self, x: int, y: int) -> None:
        self.radius = cfg.BALL_RADIUS
        self.rect = pygame.Rect(
            x - self.radius,
            y - self.radius,
            2 * self.radius,
            2 * self.radius,
        )
        self.vx = cfg.BALL_SPEED_X
        self.vy = cfg.BALL_SPEED_Y

    def update(self) -> None:
        """ Updates the Ball's position for the each frame. """
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, screen: pygame.surface) -> None:
        """ Renders the Ball. """
        colour = cfg.BALL_COLOR
        pygame.draw.circle(screen, colour, self.rect.center, self.radius)
    
    def speed_up(self):
        """Увеличиваеть скорость мяча"""
        current_speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
        new_speed = current_speed * 1.3
        if current_speed > 0:
            ratio = new_speed / current_speed
            self.vx *= ratio
            self.vy *= ratio

    def speed_down(self):
        """Уменьшаетб скорость мяча"""
        current_speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
        new_speed = max(2, current_speed * 0.7)
        if current_speed > 0:
            ratio = new_speed / current_speed
            self.vx *= ratio
            self.vy *= ratio


class Bonus:
    """Bonus class that can be caught by paddle."""

    def __init__(self, x: int, y: int, bonus_type: str):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 20, 20)
        self.type = bonus_type
        self.speed = 3
        self.alive = True
        
        self.bonus_data = {
            "extend": {"letter": "E", "color": cfg.GREEN, "name": "Extend"},
            "multiball": {"letter": "M", "color": cfg.MAGENTA, "name": "Multi Ball"},
            "laser": {"letter": "L", "color": cfg.RED, "name": "Laser"},
            "extra_life": {"letter": "+", "color": cfg.YELLOW, "name": "Extra Life"},
            "shrink": {"letter": "S", "color": cfg.ORANGE, "name": "Shrink"},
            "speed_up": {"letter": "U", "color": cfg.CYAN, "name": "Speed Up"},
            "speed_down": {"letter": "D", "color": (100, 100, 255), "name": "Speed Down"},
        }

    def update(self) -> None:
        """Moves bonus down."""
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen: pygame.Surface) -> None:
        """Draws bonus on screen."""
        data = self.bonus_data.get(self.type, {"letter": "?", "color": cfg.WHITE})
        color = data["color"]
        letter = data["letter"]
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, cfg.WHITE, self.rect, 2)
        
        font = pygame.font.Font(None, 24)
        text = font.render(letter, True, cfg.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def apply(self, paddle: Paddle, ball: Ball) -> str:
        """Applies bonus effect"""
        if self.type == "extend":
            paddle.rect.width = min(200, paddle.rect.width * 1.3)
            return "Paddle Extended!"
        elif self.type == "multiball":
            return "Multi Ball!"
        elif self.type == "laser":
            paddle.laser = True
            return "Laser Activated!"
        elif self.type == "extra_life":
            return "Extra Life!"
        elif self.type == "shrink":
            paddle.shrink()
            return "Paddle Shrunk!"
        elif self.type == "speed_up":
            ball.speed_up()
            return "Speed Up!"
        elif self.type == "speed_down":
            ball.speed_down()
            return "Speed Down!"
        return "Bonus applied!"
