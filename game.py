# Pygame template

import pygame
import random
import time
import neat
import os
import math

GAMES_WIDE = 10
GAMES_TALL = 10
SPACES_WIDE = 16
SPACES_TALL = 9
SIZE = 10
HEADER = 75
WIDTH = SPACES_WIDE * SIZE * GAMES_WIDE
HEIGHT = SPACES_TALL * SIZE * GAMES_TALL + HEADER
GEN = 1
LONGEST_SNAKE = 0
FPS = 30

TIME_PER_MOVE = 2

HIGHEST_SCORE = 0

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

DIRECTION = { 'up': 1, 'down': 2, 'left': 3, 'right': 4 }

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
BG_COLORS = [BLUE, WHITE, orange, yellow, marroon, lime, pink, purple, gray, magenta, brown, navy_blue, rust, dandilion_yellow, highlighter, sky_blue, light_gray, dark_gray, tan, coffee_brown, moon_glow]
pygame.font.init() # you have to call this at the start, 
comicFont = pygame.font.SysFont('Comic Sans MS', 30)


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
        self.size = size
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def draw(self, win):
        win.blit(self.image, self.position)

    def has_collided(self, sprite):
        return self.rect.center[0] == sprite.rect.center[0] and self.rect.center[1] == sprite.rect.center[1]


class Game:

    def __init__(self, width, height, tile_size, offset_x, offset_y, background_color, net, genome):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.background_color = background_color
        self.genome = genome
        self.net = net
        self.snake_size = 0
        self.moves = 0
        self.previous_direction = 'right'
        self.snake = Snake(self.tile_size, self.offset_x, self.offset_y)
        self.food = Food(self.tile_size, self.offset_x, self.offset_y)
        self.previous_distance_till_food = self.distance_till_food()

    def set_direction(self, direction):
        self.snake.set_direction(direction)

    def restart(self):
        self.food.set_new_position()

    def game_over(self):
        head = self.snake.get_head()
        head_position = head.position
        if head_position[0] < self.offset_x or head_position[0] > (self.width - 1) * self.tile_size + self.offset_x:
            return 1
        if head_position[1] < self.offset_y or head_position[1] > (self.height - 1) * self.tile_size + self.offset_y:
            return 1
        if self.snake.collide_with_self():
            return 2
        
        return 0

    def distance_till_food(self):
        head = self.snake.get_head()
        return math.hypot(head.rect.left - self.food.rect.left, head.rect.top - self.food.rect.top)


    def move(self):
        head = self.snake.get_head()
        space_list = []
        for space in range(SPACES_WIDE * SPACES_TALL):
            x = space % SPACES_WIDE
            y = math.floor(space / SPACES_TALL)
            head_top = abs(head.rect.top / head.size)
            head_left = abs(head.rect.left / head.size)
            if x == head_top and y == head_left:
                space_list.append(1)
                continue

            if x == (self.food.rect.left / self.food.size) and y == (self.food.rect.top / self.food.size):
                space_list.append(3)
                continue
            added_space = False
            for body in self.snake.snake_bodies:
                fake_snake_body = SnakeBody((x * head.size, y * head.size), head.size)
                if body.has_collided(fake_snake_body):
                    space_list.append(2)
                    added_space = True
                    break
            
            if added_space:
                continue
            else:
                space_list.append(0)

        outputs = self.net.activate((
                *space_list,
                (head.rect.top / head.size),
                (head.rect.top / head.size),
                DIRECTION[self.snake.direction],
                self.moves               
            )
        )
        self.moves += 1
        if outputs[0] == max(outputs):
            self.set_direction('up')
        elif outputs[1] == max(outputs):
            self.set_direction('down')
        elif outputs[2] == max(outputs):
            self.set_direction('left')
        elif outputs[3] == max(outputs):
            self.set_direction('right')

        self.snake.move()

        ## Valuing Life
        self.genome.fitness += 2

        # Change Direction every 3 moves we reward you
        if self.previous_direction != self.snake.direction and self.moves % 3 == 0:
            self.genome.fitness += 5


        head = self.snake.get_head()
        game_over_how = self.game_over()
        if game_over_how > 0:

            ## Punish the snake for hitting a wall
            if game_over_how == 1:
                self.genome.fitness -= 5
            ## Valuing Death
            self.genome.fitness -= 7
            self.snake.reset()
            self.food.set_new_position()
            return False

        if head.has_collided(self.food):
            ## Valuing Food
            self.genome.fitness += 15
            self.snake.grow()
            self.snake_size += 1
            self.food.set_new_position()

        return True

    def draw(self, win):
        background = pygame.Surface((self.width * self.tile_size, self.height * self.tile_size))
        background.fill(self.background_color)
        rect = background.get_rect()
        rect.topleft = (self.offset_x, self.offset_y)
        win.blit(background, rect.topleft)
        genText = comicFont.render('GEN: ' + str(GEN), False, WHITE)
        longSnakeText = comicFont.render('Longest Snake: ' + str(LONGEST_SNAKE), False, WHITE)
        win.blit(genText, (450, 10))
        win.blit(longSnakeText, (900, 10))
        self.snake.draw(win)
        self.food.draw(win)



class Snake:
    
    direction = 'down'
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
            left = 10 * self.size + self.size * self.length - (i * self.size) + self.offset_x
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



def main(genomes, config):
    global GEN
    global LONGEST_SNAKE
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake Game @ 100')
    clock = pygame.time.Clock()

    games = []
    for w in range(0, GAMES_WIDE):
        for h in range(0, GAMES_TALL):
            if len(genomes) > w * GAMES_WIDE + h:
                genome = genomes[w * GAMES_WIDE + h][1]
                net = neat.nn.FeedForwardNetwork.create(genome, config)
                genome.fitness = 0
                game = Game(SPACES_WIDE, SPACES_TALL, SIZE, SPACES_WIDE * SIZE * w, SPACES_TALL * SIZE * h + HEADER, random.choice(BG_COLORS), net, genome)
                games.append(game)
            

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
                run = False
                pygame.quit()
                quit()        

        if current_time - previous_time > 200:
            for game in games:
                if game.move() == False:
                    if game.snake_size > LONGEST_SNAKE:
                        LONGEST_SNAKE = game.snake_size
                    games.remove(game)
            previous_time = int(round(time.time() * 1000))

        if len(games) == 0:
            GEN += 1
            running = False
        # Draw / Render
        draw(win, games)
        pygame.display.update()



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    # stats reporter
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    max_fitness_points = 1500
    p.run(main, max_fitness_points) 


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)



