import pygame
import random
import sys
from pygame.math import Vector2

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 40
GRID_SIZE = 20
SCREEN_SIZE = CELL_SIZE * GRID_SIZE
SCREEN = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption('Snake Breakout')
CLOCK = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FLASH_COLOR = (50, 50, 50)
BLOCK_COLORS = [(255, 165, 0), (0, 255, 255), (255, 192, 203)]  # Orange, Cyan, Pink

class Snake:
    def __init__(self):
        # Starting position
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(1, 0)
        self.grow = False

    def draw(self):
        for segment in self.body:
            segment_rect = pygame.Rect(segment.x * CELL_SIZE, segment.y * CELL_SIZE, 
                                     CELL_SIZE - 1, CELL_SIZE - 1)
            pygame.draw.rect(SCREEN, GREEN, segment_rect)

    def move(self):
        if self.grow:
            body_copy = self.body[:]
            new_head = body_copy[0] + self.direction
            # Wrap around screen
            new_head.x = new_head.x % GRID_SIZE
            new_head.y = new_head.y % GRID_SIZE
            body_copy.insert(0, new_head)
            self.body = body_copy
            self.grow = False
        else:
            body_copy = self.body[:-1]
            new_head = body_copy[0] + self.direction
            # Wrap around screen
            new_head.x = new_head.x % GRID_SIZE
            new_head.y = new_head.y % GRID_SIZE
            body_copy.insert(0, new_head)
            self.body = body_copy

    def check_collision(self):
        head = self.body[0]
        if head in self.body[1:]:
            return True
        return False

class Food:
    def __init__(self):
        self.pos = Vector2(GRID_SIZE // 2, GRID_SIZE // 2)
        self.velocity = Vector2(0.2, 0.2)  # Initial velocity for bouncing

    def draw(self):
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), 
                               CELL_SIZE - 1, CELL_SIZE - 1)
        pygame.draw.rect(SCREEN, RED, food_rect)

    def move(self):
        # Update position
        self.pos += self.velocity
        
        # Bounce off walls
        if self.pos.x <= 0 or self.pos.x >= GRID_SIZE - 1:
            self.velocity.x *= -1
        if self.pos.y <= 0 or self.pos.y >= GRID_SIZE - 1:
            self.velocity.y *= -1
            
        # Keep within bounds
        self.pos.x = max(0, min(self.pos.x, GRID_SIZE - 1))
        self.pos.y = max(0, min(self.pos.y, GRID_SIZE - 1))

class Block:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.health = 3  # Number of hits needed to destroy
        self.hit_cooldown = 0  # Prevent multiple hits at once

    def draw(self):
        block_rect = pygame.Rect(self.pos.x * CELL_SIZE, self.pos.y * CELL_SIZE,
                                CELL_SIZE * 2 - 1, CELL_SIZE - 1)  # Make blocks wider
        # Calculate faded color based on health
        faded_color = [int(c * (self.health/3)) for c in self.color]
        pygame.draw.rect(SCREEN, faded_color, block_rect)
        
        # Draw health indicator
        if self.hit_cooldown > 0:
            pygame.draw.rect(SCREEN, (255, 255, 255), block_rect, 2)  # White border when hit

def create_blocks():
    blocks = []
    block_width = 2  # Each block is 2 cells wide
    start_x = 1  # Start position
    
    for row in range(3):  # 3 rows of blocks
        for col in range(8):  # 8 blocks per row
            pos = Vector2(start_x + col * block_width, row * 2 + 1)
            blocks.append(Block(pos, BLOCK_COLORS[row]))
    return blocks

def main():
    snake = Snake()
    food = Food()
    blocks = create_blocks()
    game_over = False
    score = 0
    flash_frames = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_UP and snake.direction.y != 1:
                    snake.direction = Vector2(0, -1)
                if event.key == pygame.K_DOWN and snake.direction.y != -1:
                    snake.direction = Vector2(0, 1)
                if event.key == pygame.K_LEFT and snake.direction.x != 1:
                    snake.direction = Vector2(-1, 0)
                if event.key == pygame.K_RIGHT and snake.direction.x != -1:
                    snake.direction = Vector2(1, 0)
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    snake = Snake()
                    food = Food()
                    blocks = create_blocks()
                    game_over = False
                    score = 0
                    flash_frames = 0

        if not game_over:
            if flash_frames > 0:
                SCREEN.fill(FLASH_COLOR)
                flash_frames -= 1
            else:
                SCREEN.fill(BLACK)
            
            # Move snake and food
            snake.move()
            food.move()
            
            # Update block cooldowns
            for block in blocks:
                if block.hit_cooldown > 0:
                    block.hit_cooldown -= 1
            
            # Check collision with food
            snake_head_rect = pygame.Rect(snake.body[0].x * CELL_SIZE, snake.body[0].y * CELL_SIZE, 
                                        CELL_SIZE, CELL_SIZE)
            food_rect = pygame.Rect(int(food.pos.x * CELL_SIZE), int(food.pos.y * CELL_SIZE), 
                                  CELL_SIZE, CELL_SIZE)
            
            if snake_head_rect.colliderect(food_rect):
                food.velocity *= 1.1  # Increase food speed
                snake.grow = True
                score += 10
                flash_frames = 3
            
            # Check collision between food and blocks
            food_hit_block = False
            for block in blocks[:]:  # Use slice copy to safely remove blocks
                block_rect = pygame.Rect(block.pos.x * CELL_SIZE, block.pos.y * CELL_SIZE,
                                       CELL_SIZE * 2 - 1, CELL_SIZE - 1)
                
                if block.hit_cooldown == 0 and food_rect.colliderect(block_rect):
                    block.health -= 1
                    block.hit_cooldown = 5
                    food_hit_block = True
                    flash_frames = 2
                    
                    # Bounce the food off the block
                    if abs(food.pos.x - block.pos.x) < abs(food.pos.y - block.pos.y):
                        food.velocity.y *= -1
                    else:
                        food.velocity.x *= -1
                    
                    if block.health <= 0:
                        blocks.remove(block)
                        score += 50
                        flash_frames = 3

            # Check game over conditions
            if snake.check_collision():
                game_over = True

            # Draw everything
            for block in blocks:
                block.draw()
            snake.draw()
            food.draw()

            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {score}', True, (255, 255, 255))
            blocks_left = font.render(f'Blocks: {len(blocks)}', True, (255, 255, 255))
            SCREEN.blit(score_text, (10, 10))
            SCREEN.blit(blocks_left, (10, 50))
        else:
            font = pygame.font.Font(None, 48)
            game_over_text = font.render('Game Over!', True, (255, 255, 255))
            score_text = font.render(f'Final Score: {score}', True, (255, 255, 255))
            restart_text = font.render('Press SPACE to restart', True, (255, 255, 255))
            
            SCREEN.blit(game_over_text, 
                       (SCREEN_SIZE//2 - game_over_text.get_width()//2, 
                        SCREEN_SIZE//2 - 60))
            SCREEN.blit(score_text, 
                       (SCREEN_SIZE//2 - score_text.get_width()//2, 
                        SCREEN_SIZE//2))
            SCREEN.blit(restart_text, 
                       (SCREEN_SIZE//2 - restart_text.get_width()//2, 
                        SCREEN_SIZE//2 + 60))

        pygame.display.flip()
        CLOCK.tick(10)  # Control game speed

if __name__ == '__main__':
    main() 