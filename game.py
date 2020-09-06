import pygame
from math import sqrt
from random import randint


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Position: [{self.x}, {self.y}]"

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

class Food:
    def __init__(self, game):
        self.position = Position(randint(0, game.SIDE-1), randint(0, game.SIDE-1))


    def draw(self, game):
        pygame.draw.rect(
                        game.win,
                        (0, 255, 0),
                            (self.position.x*game.TILE_WIDTH,
                            self.position.y*game.TILE_HEIGHT,
                            game.TILE_WIDTH-game.TILE_BORDER,
                            game.TILE_HEIGHT- game.TILE_BORDER
                            )
                        )
    def respawn(self, game):
        self.position = Position(randint(0, game.SIDE-1), randint(0, game.SIDE-1))
        while self.position in game.snake.body:
            self.position = Position(randint(0, game.SIDE-1), randint(0, game.SIDE-1))

        print(f"food: {self.position}")


class Snake:
    def __init__(self):
        self.body = [Position(5, 5)]
        self.add = False


    def up(self):
        new = self.body[-1] + Position(0, -1)
        self.move(new)

    def down(self):
        new = self.body[-1] + Position(0, 1)
        self.move(new)

    def right(self):
        new = self.body[-1] + Position(1, 0)
        self.move(new)

    def left(self):
        new = self.body[-1] + Position(-1, 0)
        self.move(new)

    def move(self, new):
        self.body.append(new)
        if not self.add:
            self.body.pop(0)
        self.add = False

    def draw(self, game):
        #
        for tile in self.body:
            # print(tile)
            pygame.draw.rect(
                            game.win,
                            (255, 0, 0),
                                (tile.x*game.TILE_WIDTH,
                                tile.y*game.TILE_HEIGHT,
                                game.TILE_WIDTH-game.TILE_BORDER,
                                game.TILE_HEIGHT- game.TILE_BORDER
                                )
                            )


    def head(self):
        return self.body[-1]


class Game:
    WIDTH = 400
    HEIGHT = 400

    SIDE = 13

    TILE_WIDTH = WIDTH / SIDE
    TILE_HEIGHT = HEIGHT / SIDE
    TILE_BORDER = 1


    TICK = 30

    TITLE = "Snake"

    def __init__(self):
        self.mainloop = False

        self.win = None
        self.clock = None

        self.snake = None
        self.food = None

    def main(self):
        self.setup()
        self.mainloop = True

        while self.mainloop:
            self.clock.tick(self.TICK)
            self.update()
            self.check_events()

            self.draw_window()


    def setup(self):
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()

        self.snake = Snake()
        self.food = Food(self)

        gameIcon = pygame.image.load('snake.png')
        pygame.display.set_icon(gameIcon)


    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.run_loop = False
                    pygame.quit()
                    quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.up()
                if event.key == pygame.K_DOWN:
                    self.snake.down()
                if event.key == pygame.K_RIGHT:
                    self.snake.right()
                if event.key == pygame.K_LEFT:
                    self.snake.left()



    def draw_window(self):

        self.win.fill((0, 0, 0)) # Black background

        for i in range(self.SIDE):
            for j in range(self.SIDE):
                pygame.draw.rect(self.win,
                                (255, 255, 255),
                                    (i*self.TILE_WIDTH,
                                    j*self.TILE_HEIGHT,
                                    self.TILE_WIDTH,
                                    self.TILE_HEIGHT),
                                self.TILE_BORDER)

        self.food.draw(self)
        self.snake.draw(self)
        pygame.display.update()

    def update(self):
        if self.snake.head() == self.food.position:
            self.snake.add = True
            self.food.respawn(self)

Game().main()
