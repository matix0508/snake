import pygame
from math import sqrt

class Snake:
    

class Game:
    WIDTH = 400
    HEIGHT = 400

    TILES = 269 # This better be a nice square xd
    SIDE = int(sqrt(TILES))

    TILE_WIDTH = WIDTH / SIDE
    TILE_HEIGHT = HEIGHT / SIDE
    TILE_BORDER = 1


    TICK = 30

    TITLE = "Snake"

    def __init__(self):
        self.mainloop = False

        self.win = None
        self.clock = None

    def main(self):
        self.setup()
        self.mainloop = True

        while self.mainloop:
            self.clock.tick(self.TICK)
            self.check_events()

            self.draw_window()


    def setup(self):
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.run_loop = False
                    pygame.quit()
                    quit()

    def draw_window(self):

        self.win.fill((0, 0, 0)) # Black background

        for i in range(self.SIDE):
            for j in range(self.SIDE):
                pygame.draw.rect(self.win, (255, 255, 255),(i*self.TILE_WIDTH,j*self.TILE_HEIGHT,self.TILE_WIDTH,self.TILE_HEIGHT), self.TILE_BORDER)

        pygame.display.update()

Game().main()
