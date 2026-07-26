import pygame
import settings as cfg
from game.entities import Paddle, Brick, Ball, Bonus
from game.level import load_level
import random


def bounce_off_rect(ball: Ball, rect: pygame.Rect):
    """ Checks if the Ball collides with the given rect. """

    # Calculate ball's overlaps and find the smallest one
    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(
        overlap_bottom,
        overlap_left,
        overlap_right,
        overlap_top)
    
    # Calculate the Ball's final velocities
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


def handle_ball_vs_bricks(ball: Ball, bricks: list[Brick], bonuses: list[Bonus]) -> int:
    scored = 0
    for brick in bricks[:]:
        if not ball.rect.colliderect(brick.rect):
            continue
        bounce_off_rect(ball, brick.rect)
        if brick.hp == -1:
            continue
        brick.hit()

        if brick.hp <= 0:
            bricks.remove(brick)
            scored += 10
            # Chance to drop a bonus
            if random.random() < cfg.BONUS_PROBABILITY:
                bonus_type = random.choice(list(cfg.BONUS_TYPES.keys()))
                bonuses.append(Bonus(brick.rect.centerx, brick.rect.centery, bonus_type))
    return scored


def handle_ball_vs_paddle(ball: Ball, paddle: Paddle) -> None:
    """ Handles Ball bounce over the Paddle. """
    bounce_off_rect(ball, paddle.rect)
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    max_vx = cfg.MAX_BALL_SPEED_X
    ball.vx = max(-max_vx, min(max_vx, offset * max_vx))


def apply_bonus(paddle: Paddle, ball: Ball, bonus_type: str) -> None:
    """ Applies the bonus effect. """
    if bonus_type == 'S':  # Paddle Shrink
        paddle.rect.width = max(40, paddle.rect.width * 0.7)
        
    elif bonus_type == 'U':  # Ball Speed Up
        ball.vx *= 1.3
        ball.vy *= 1.3
        
    elif bonus_type == 'D':  # Ball Speed Down
        ball.vx *= 0.7
        ball.vy *= 0.7


def run(screen: pygame.Surface, clock: pygame.time.Clock, level: int) -> None:
    paddle = Paddle()
    bricks, rows, cols = load_level(level)
    ball = Ball(cfg.WIDTH // 2, cfg.HEIGHT - 50)
    bonuses: list[Bonus] = []
    running = True
    
    while running:
        screen.fill(cfg.BLACK)
        
        # Handle input
        keys = pygame.key.get_pressed()
        paddle.move(keys)
        
        # Ball collisions with bricks
        handle_ball_vs_bricks(ball, bricks, bonuses)
        
        # Ball collision with paddle
        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            handle_ball_vs_paddle(ball, paddle)
        
        # Update ball
        ball.update()
        
        # Ball wall collisions
        if ball.rect.left < cfg.FIELD_LEFT or ball.rect.right > cfg.FIELD_RIGHT:
            ball.vx *= -1
        if ball.rect.top < cfg.TOP_OFFSET:
            ball.vy *= -1
        if ball.rect.bottom > cfg.HEIGHT:
            # Ball lost - restart
            ball.rect.center = (cfg.WIDTH // 2, cfg.HEIGHT - 50)
            ball.vx = cfg.BALL_SPEED_X
            ball.vy = cfg.BALL_SPEED_Y
        
        # Update bonuses
        for bonus in bonuses[:]:
            if not bonus.update():
                bonuses.remove(bonus)
            elif bonus.rect.colliderect(paddle.rect):
                apply_bonus(paddle, ball, bonus.type)
                bonuses.remove(bonus)
        
        # Draw everything
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)
        for bonus in bonuses:
            bonus.draw(screen)
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame.display.flip()
        clock.tick(cfg.FPS)
