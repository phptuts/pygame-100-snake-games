# Pygame template

import pygame
import random
import time
GAMES_WIDE = 10
GAMES_TALL = 10
SPACES_WIDE = 16
SPACES_TALL = 9
SIZE = 10
WIDTH = SPACES_WIDE * SIZE * GAMES_WIDE
HEIGHT = SPACES_TALL * SIZE * GAMES_TALL

FPS = 30

TIME_PER_MOVE = 200

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

orange = (255,100,10)
yellow = (255,255,0)
marroon = (115,0,0)
lime = (180,255,100)
pink = (255,100,180)
purple = (240,0,255)
gray = (127,127,127)
magenta = (255,0,230)
brown = (100,40,0)
navy_blue = (0,0,100)
rust = (210,150,75)
dandilion_yellow = (255,200,0)
highlighter = (255,255,100)
sky_blue = (0,255,255)
light_gray = (200,200,200)
dark_gray = (50,50,50)
tan = (230,220,170)
coffee_brown =(200,190,140)
moon_glow = (235, 245, 255)
BG_COLORS = [BLACK, BLUE, WHITE, orange, yellow, marroon, lime, pink, purple, gray, magenta, brown, navy_blue, rust, dandilion_yellow, highlighter, sky_blue, light_gray, dark_gray, tan, coffee_brown, moon_glow]


class Food(pygame.sprite.Sprite):
    def __init__(self, size, offset_x, offset_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.size = size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.rect = self.image.get_rect()
        self.rect.topleft = self.get_new_position()

    def get_new_position(self):
        x = random.randint(0, 15) 
        y = random.randint(0, 8) 
        return (x * self.size + self.offset_x, y * self.size + self.offset_y)
        
    def set_new_position(self):
        self.rect.topleft = self.get_new_position()

    def draw(self, win):
        win.blit(self.image, self.rect.topleft)


class SnakeBody(pygame.sprite.Sprite):

    def __init__(self, position, size):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.image = pygame.Surface((size, size))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def draw(self, win):
        win.blit(self.image, self.position)

    def has_collided(self, sprite):
        return self.rect.center[0] == sprite.rect.center[0] and self.rect.center[1] == sprite.rect.center[1]


class Game:

    def __init__(self, width, height, tile_size, offset_x, offset_y, background_color):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.background_color = background_color

        self.snake = Snake(self.tile_size, self.offset_x, self.offset_y)
        self.food = Food(self.tile_size, self.offset_x, self.offset_y)

    def set_direction(self, direction):
        self.snake.set_direction(direction)

    def restart(self):
        self.food.set_new_position()

    def game_over(self):
        head = self.snake.get_head()
        head_position = head.position
        if head_position[0] < self.offset_x or head_position[0] > self.width * self.tile_size + self.offset_x:
            return True
        if head_position[1] < self.offset_y or head_position[1] > self.height * self.tile_size + self.offset_y:
            return True
        if self.snake.collide_with_self():
            return True
        
        return False


    def move(self):
        self.snake.move()
        head = self.snake.get_head()

        if self.game_over():
            self.snake.reset()
            self.food.set_new_position()
            self.set_direction('right')

        if head.has_collided(self.food):
            self.snake.grow()
            self.food.set_new_position()

    def draw(self, win):
        background = pygame.Surface((self.width * self.tile_size, self.height * self.tile_size))
        background.fill(self.background_color)
        rect = background.get_rect()
        rect.topleft = (self.offset_x, self.offset_y)
        win.blit(background, rect.topleft)
        self.snake.draw(win)
        self.food.draw(win)



class Snake:
    
    direction = 'right'
    length = 3
    snake_bodies = []

    def __init__(self, size, offset_x, offset_y):
        self.size = size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.reset()

    def set_direction(self, direction):
        self.direction = direction

    def reset(self):
        self.snake_bodies = []
        for i in range(self.length):
            left = self.size * self.length - (i * self.size) + self.offset_x
            top = self.size * 3 + self.offset_y
            self.snake_bodies.append(SnakeBody((left, top), self.size))

    def move(self):
        self.snake_bodies.pop()
        previos_head = self.snake_bodies[0]
        left = previos_head.position[0]
        top = previos_head.position[1] 

        if self.direction == 'right':
            left += self.size
        if self.direction == 'left':
            left -= self.size
        if self.direction == 'up':
            top -= self.size
        if self.direction == 'down':
            top += self.size

        self.snake_bodies.insert(0, SnakeBody((left, top), self.size))

    def draw(self, win):
        for snake_body in self.snake_bodies:
            snake_body.draw(win)

    def get_head(self):
        return self.snake_bodies[0]

    def grow(self):
        self.snake_bodies.append(self.snake_bodies[len(self.snake_bodies) - 1])

    def collide_with_self(self):
        for index, snake_body in enumerate(self.snake_bodies):
            for test_index, test_snake_body in enumerate(self.snake_bodies):
                if index != test_index and test_snake_body.has_collided(snake_body):
                    return True
        
        return False
                    


def draw(win, games):
    win.fill(BLACK)
    for game in games:
        game.draw(win)

# initialize pygame and create window
pygame.init()


win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('My Game')
clock = pygame.time.Clock()

games = []

for w in range(0, GAMES_WIDE):
    for h in range(0, GAMES_TALL):
        games.append(Game(SPACES_WIDE, SPACES_TALL, SIZE, SPACES_WIDE * SIZE * w, SPACES_TALL * SIZE * h, random.choice(BG_COLORS)))

running = True
previous_time = int(round(time.time() * 1000))
while running:

    current_time = int(round(time.time() * 1000))
    # keep loop running at the right speed
    clock.tick(FPS)
    # Events
    for event in pygame.event.get():
        # check for closing the window
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            for game in games:
                if event.key == pygame.K_LEFT:
                    game.set_direction('left')
                if event.key == pygame.K_RIGHT:
                    game.set_direction('right')
                if event.key == pygame.K_UP:
                    game.set_direction('up')
                if event.key == pygame.K_DOWN:
                    game.set_direction('down')
    

    if current_time - previous_time > 200:
        for game in games:
            game.move()
        previous_time = int(round(time.time() * 1000))

    # Draw / Render
    draw(win, games)
    pygame.display.update()

pygame.quit()
quit()