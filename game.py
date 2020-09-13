import pygame
from math import sqrt
from random import randint
from database import Database
pygame.font.init()


def text_objects(text, font):
    textSurface = font.render(text, True, (0, 0, 0))
    return textSurface, textSurface.get_rect()


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
            game.score += 1

        # print(f"food: {self.position}")


class Snake:
    def __init__(self, game):
        self.body = [Position(randint(3, game.SIDE - 3), randint(3, game.SIDE - 3))]
        self.add = False
        self.side = game.SIDE
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        self.game = game


    def go_up(self):
        if self.head().y > 0:
            self.move(0, -1)
        else:
            self.game.game_over()

    def go_down(self):
        if self.head().y < self.side-1:
            self.move(0, 1)
        else:
            self.game.game_over()

    def go_right(self):
        if self.head().x < self.side-1:
            self.move(1, 0)
        else:
            self.game.game_over()

    def go_left(self):
        if self.head().x > 0:
            self.move(-1, 0)
        else:
            self.game.game_over()

    def move(self, x, y):
        new = self.body[-1] + Position(x, y)
        if not new in self.body:
            self.body.append(new)
            if not self.add:
                self.body.pop(0)
            self.add = False
        else:
            self.game.game_over()


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

    def move_reset(self):
        self.up = False
        self.down = False
        self.right = False
        self.left = False


class Game:
    WIDTH = 400
    HEIGHT = 400

    # SIDE = 7

    TILE_BORDER = 1


    TICK = 30

    TITLE = "Snake"

    STAT_FONT = pygame.font.SysFont("comicsans", 50)
    MID_FONT = pygame.font.SysFont("comicsans", 75)
    LARGE_FONT = pygame.font.SysFont("comicsans", 100)

    def __init__(self, side):
        self.mainloop = False
        self.menu_loop = False

        self.win = None
        self.clock = None

        self.TILE_WIDTH = self.WIDTH / side
        self.TILE_HEIGHT = self.HEIGHT / side

        self.SIDE = side

        self.snake = None
        self.food = None
        self.score = 0

        self.counter = 0

        self.best_score = 0

    def main(self):
        self.setup()
        self.mainloop = True

        while self.mainloop:
            self.clock.tick(self.TICK)
            self.update()
            self.check_events()

            self.draw_window()

    def menu(self):
        self.setup()
        self.menu_loop = True
        while self.menu_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        self.run_loop = False
                        pygame.quit()
                        quit()

            self.win.fill((0, 0, 0))
            TextSurf, TextRect = text_objects("Snake", self.LARGE_FONT)
            TextRect.center = (self.WIDTH / 2, self.HEIGHT / 2)
            self.win.blit(TextSurf, TextRect)

            self.button("Play a Game", 100, 100, 220, 50, (0, 250, 0), (0, 200, 0), self.main)


            pygame.display.update()
            self.clock.tick(15)




    def setup(self):
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()

        self.snake = Snake(self)
        self.food = Food(self)

        gameIcon = pygame.image.load('snake.png')
        pygame.display.set_icon(gameIcon)

        self.counter = 0

        self.db = Database("snake")
        # if self.db.table_exists('score'):
        #     pass
        #     # self.best_score = self.db.select('best_score') # to write function Db.select()


    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.run_loop = False
                    pygame.quit()
                    quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.move_reset()
                    self.snake.up = True
                if event.key == pygame.K_DOWN:
                    self.snake.move_reset()
                    self.snake.down = True
                if event.key == pygame.K_RIGHT:
                    self.snake.move_reset()
                    self.snake.right = True
                if event.key == pygame.K_LEFT:
                    self.snake.move_reset()
                    self.snake.left = True



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
        self.counter += 1
        if self.snake.head() == self.food.position:
            self.snake.add = True
            self.food.respawn(self)

        if self.counter % 5 == 0:
            if self.snake.up:
                self.snake.go_up()
            if self.snake.down:
                self.snake.go_down()
            if self.snake.right:
                self.snake.go_right()
            if self.snake.left:
                self.snake.go_left()

    def game_over(self):
        self.mainloop = False


    def button(self, msg, x, y, w, h, ic, ac, action=None):
        """
        helps to create buttons on the screen
        """
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self.win, ac,(x,y,w,h))
            if click[0] == 1 and action != None:
                action()

        else:
            pygame.draw.rect(self.win, ic,(x,y,w,h))
        textSurf, textRect = text_objects(msg, self.STAT_FONT)
        textRect.center = ( (x+(w/2)), (y+(h/2)) )
        self.win.blit(textSurf, textRect)

Game(13).menu()
