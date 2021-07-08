import pygame
import random, time
import os

# constants
W, H = 288, 512
FPS = 30

# setup
pygame.init()
SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption("My Flappy Bird Game")
CLOCK = pygame.time.Clock()

# images
# bird = pygame.image.load('assets/sprites/redbird-midflap.png')
# background = pygame.image.load('assets/sprites/background-day.png')
# guide = pygame.image.load('assets/sprites/message.png')
# floor = pygame.image.load('assets/sprites/base.png')
# pipe = pygame.image.load('assets/sprites/pipe-green.png')
# gameover = pygame.image.load('assets/sprites/gameover.png')

# Use IMAGES dictionary instead of load one by one
IMAGES = {}
for image in os.listdir('assets/sprites'):
    name, extension = os.path.splitext(image)
    path = os.path.join('assets/sprites', image)
    IMAGES[name] = pygame.image.load(path)


FLOOR_Y = H-IMAGES['base'].get_height()
wing_sound = pygame.mixer.Sound('assets/audio/wing.wav')
die_sound = pygame.mixer.Sound('assets/audio/die.wav')
hit_sound = pygame.mixer.Sound('assets/audio/hit.wav')
point_sound = pygame.mixer.Sound('assets/audio/point.wav')
swoosh_sound = pygame.mixer.Sound('assets/audio/swoosh.wav')

def main():
    while True:
        swoosh_sound.play()
        # random choose background, bird, and pipe color each time
        IMAGES['background'] = IMAGES[random.choice(['background-day', 'background-night'])]
        color = random.choice(['redbird', 'yellowbird', 'bluebird'])
        IMAGES['bird_fly'] = [IMAGES[color+'-upflap'], IMAGES[color+'-midflap'], IMAGES[color+'-downflap']]
        pipe = IMAGES[random.choice(['pipe-green', 'pipe-red'])]
        IMAGES['pipes'] = [pipe, pygame.transform.flip(pipe, False, True)]
        start_window()
        result = play_window()
        gameover_window(result)


def start_window():

    # move floor
    floor_gap = IMAGES['base'].get_width() - W
    floor_x_move = 0
    
    guide_x, guide_y = (W-IMAGES['message'].get_width())/2, (FLOOR_Y-IMAGES['message'].get_height())/2
    bird_x, bird_y = (W-IMAGES['bird_fly'][0].get_width())/2, (H-IMAGES['bird_fly'][0].get_height())/2*0.96

    # flying bird
    bird_y_v = 1 # bird's y dirction velocity (1 px)
    bird_y_range = [bird_y - 8, bird_y + 8]   # bird's y direction moving range
    wing_idx = 0
    repeat = 5
    frames = [0] * repeat + [1] * repeat + [2] * repeat + [1] * repeat


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

        floor_x_move -= 4
        if floor_x_move <= -floor_gap:
            floor_x_move = 0

        bird_y += bird_y_v
        if bird_y < bird_y_range[0] or bird_y > bird_y_range[1]:
            bird_y_v *= -1   # change velocity direction when hit the range
        wing_idx += 1
        wing_idx %= len(frames)

        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['base'], (floor_x_move, FLOOR_Y))
        SCREEN.blit(IMAGES['message'], (guide_x, guide_y))
        SCREEN.blit(IMAGES['bird_fly'][frames[wing_idx]], (bird_x, bird_y))

        pygame.display.update()
        CLOCK.tick(FPS)

def play_window():

    score = 0


    # move floor
    floor_gap = IMAGES['base'].get_width() - W
    floor_x_move = 0

    bird_x, bird_y = (W-IMAGES['bird_fly'][0].get_width())/2, (H-IMAGES['bird_fly'][0].get_height())/2*1.14
    bird = Bird(bird_x, bird_y)

    pipe_dis = random.randint(150, 170)
    n_pairs = 4
    pipe_gap = 100
    pipes = []
    for i in range(n_pairs):
        pipe_y = random.randint(int(H*0.3), int(H*0.7))
        pipe_up = Pipe(W + i*pipe_dis, pipe_y, True)
        pipe_dowm = Pipe(W + i*pipe_dis, pipe_y - pipe_gap, False)
        pipes.append(pipe_up)
        pipes.append(pipe_dowm)


    while True:

        flap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    flap = True
                    wing_sound.play()

        floor_x_move -= 4
        if floor_x_move <= -floor_gap:
            floor_x_move = 0

        bird.update(flap)

        first_pipe_up = pipes[0]
        first_pipe_down = pipes[1]
        if first_pipe_up.rect.right < 0: # when the first pipe move out of the screen, generate a new one
            pipes.remove(first_pipe_up)
            pipes.remove(first_pipe_down)
            pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
            new_pipe_up = Pipe(first_pipe_up.rect.x + n_pairs*pipe_dis, pipe_y, True)
            new_pipe_down = Pipe(first_pipe_down.rect.x + n_pairs * pipe_dis, pipe_y - pipe_gap, False)
            pipes.append(new_pipe_up)
            pipes.append(new_pipe_down)
            del first_pipe_up, first_pipe_down

        for pipe in pipes:
            pipe.update()

        # bird hit upper and floor limit
        if bird.rect.y > FLOOR_Y or bird .rect.y < 0:
            bird.dying = True
            hit_sound.play()
            die_sound.play()
            die_info = {'bird': bird, 'pipes': pipes, 'score': score}
            return die_info

        # bird hit pipe
        for pipe in pipes:
            bird.dying = True
            right_to_left = max(bird.rect.right, pipe.rect.right) - min(bird.rect.left, pipe.rect.left)
            bottom_to_top = max(bird.rect.bottom, pipe.rect.bottom) - min(bird.rect.top, pipe.rect.top)
            if right_to_left < bird.rect.width + pipe.rect.width and bottom_to_top < bird.rect.height + pipe.rect.height:
                hit_sound.play()
                die_sound.play()
                die_info = {'bird': bird, 'pipes': pipes, 'score': score}
                return die_info

        # score
        if (bird.rect.left + pipes[0].x_v) < pipes[0].rect.centerx < bird.rect.left:
            point_sound.play()
            score += 1

        SCREEN.blit(IMAGES['background'], (0, 0))
        #SCREEN.blit(IMAGES['pipes'][0], (pipe_x, pipe_y))
        for pipe in pipes:
            SCREEN.blit(pipe.image, pipe.rect)
        SCREEN.blit(IMAGES['base'], (floor_x_move, FLOOR_Y))
        show_score(score )
        SCREEN.blit(bird.image, bird.rect)


        pygame.display.update()
        CLOCK.tick(FPS)

def gameover_window(result):
    #die_sound.play()
    #bird_x, bird_y = (W-IMAGES['bird_fly'][0].get_width())/2, (H-IMAGES['bird_fly'][0].get_height())/2*1.14
    gameover_x, gameover_y = (W-IMAGES['gameover'].get_width())/2, (FLOOR_Y-IMAGES['gameover'].get_height())/2

    bird = result['bird']
    pipes_r = result['pipes']
    score = result['score']
    while True:
        if bird.dying:
            bird.died()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return

        SCREEN.blit(IMAGES['background'], (0, 0))
        for pipe in pipes_r:
            SCREEN.blit(pipe.image, pipe.rect)
        SCREEN.blit(IMAGES['base'], (0, FLOOR_Y))
        SCREEN.blit(bird.image, bird.rect)
        SCREEN.blit(IMAGES['gameover'], (gameover_x, gameover_y))
        show_score(score)
        pygame.display.update()
        CLOCK.tick(FPS)
    
def show_score(score):
    score_str = str(score)
    n = len(score_str)
    w = IMAGES['0'].get_width() * 1.1
    x = (W - n * w) / 2
    y = H * 0.1
    for num in score_str:
        SCREEN.blit(IMAGES[num], (x, y))
        x += w

class Bird:
    def __init__(self, x, y):
        self.repeat = 5
        self.frames = [0] * self.repeat + [1] * self.repeat + [2] * self.repeat + [1] * self.repeat
        self.wing_idx = 0
        self.images = IMAGES['bird_fly']
        self.image = self.images[self.frames[self.wing_idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_v = -10  # initial y direction velocity
        self.max_y_v = 10
        self.gravity = 1  # y acc
        self.rotate = 45
        self.max_rotate = -20
        self.rotate_v = -3
        self.y_v_after_flap = -10
        self.rotate_after_flap = 45
        self.dying = False    # check if bird is died

    def update(self, flap=False):

        if flap:
            self.y_v = self.y_v_after_flap
            self.rotate = self.rotate_after_flap
        self.y_v = min(self.y_v + self.gravity, self.max_y_v)
        self.rect.y += self.y_v
        self.rotate = max(self.rotate + self.rotate_v, self.max_rotate)
        self.wing_idx += 1
        self.wing_idx %= len(self.frames)
        self.image = self.images[self.frames[self.wing_idx]]  #update bird image
        self.image = pygame.transform.rotate(self.image, self.rotate)

    def died(self):
        if self.rect.y < FLOOR_Y:
            self.rect.y += self.max_y_v
            self.rotate = -90
            self.image = self.images[self.frames[self.wing_idx]]
            self.image = pygame.transform.rotate(self.image, self.rotate)

        else:
            self.dying = False

class Pipe:
    def __init__(self, x, y, upwards=True):
        if upwards:
            self.image = IMAGES['pipes'][0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = IMAGES['pipes'][1]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_v = -4

    def update(self):
        self.rect.x += self.x_v


main()