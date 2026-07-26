import pygame
import random
import settings as cfg
from game.entities import Paddle, Brick, Ball, Bonus
from game.level import load_level

def _bounce_off_rect(ball: Ball, rect: pygame.Rect):
    """ Checks if the Ball collides with the given rect. """

    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(
        overlap_bottom,
        overlap_left,
        overlap_right,
        overlap_top)
    
    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vx < 0:
        ball.rect.left = rect.right
        ball.vx *= -1

def _handle_ball_vs_bricks(
    ball: Ball,
    bricks: list[Brick],
    bonuses: list[Bonus],
) -> int:

    scored = 0
    for brick in bricks[:]:  
        if not ball.rect.colliderect(brick.rect):
            continue
        _bounce_off_rect(ball, brick.rect)
        if brick.hp == -1: 
            continue
        brick.hit()

        if brick.hp <= 0:
            bricks.remove(brick)
            scored += 10
            
            if random.random() < cfg.BONUS_PROBABILITY:
                bonus_type = random.choice(cfg.BONUS_TYPES)
                bonus = Bonus(
                    brick.rect.centerx - 10,
                    brick.rect.centery,
                    bonus_type
                )
                bonuses.append(bonus)
    return scored

def _handle_ball_vs_paddle(ball: Ball, paddle: Paddle) -> None:
    """ Handles Ball bounce over the Paddle. """
    _bounce_off_rect(ball, paddle.rect)
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    max_vx = cfg.MAX_BALL_SPEED_X
    ball.vx = max(-max_vx, min(max_vx, offset * max_vx))

def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid with Power-Ups")
    clock = pygame.time.Clock()

    running = True
    paddle = Paddle()

    bricks, rows, cols = load_level(1)
    ball = Ball(cfg.WIDTH // 2, cfg.HEIGHT - 100)
    
    bonuses = []

    while running:
        screen.fill(cfg.BLACK)

        keys = pygame.key.get_pressed()
        paddle.move(keys)

        _handle_ball_vs_bricks(ball, bricks, bonuses)

        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            _handle_ball_vs_paddle(ball, paddle)

        if ball.rect.left < cfg.FIELD_LEFT or ball.rect.right > cfg.FIELD_RIGHT:
            ball.vx = -ball.vx
        if ball.rect.top < cfg.TOP_OFFSET:
            ball.vy = -ball.vy
        if ball.rect.top > cfg.HEIGHT:
            ball.rect.center = (cfg.WIDTH // 2, cfg.HEIGHT - 100)
            ball.vx = cfg.BALL_SPEED_X
            ball.vy = -abs(cfg.BALL_SPEED_Y)

        for bonus in bonuses[:]:
            bonus.update()
            
            if bonus.rect.colliderect(paddle.rect):
                message = bonus.apply(paddle, ball)
                print(f"Bonus: {message}")
                bonuses.remove(bonus)
            elif bonus.rect.top > cfg.HEIGHT:
                bonuses.remove(bonus)

        ball.update()

        paddle.draw(screen)
        ball.draw(screen)
        
        for brick in bricks:
            brick.draw(screen)
        
        for bonus in bonuses:
            bonus.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(cfg.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
