import pygame
from math import sqrt
from random import randint
from database import Database
from time import sleep
import string
pygame.font.init()



def text_objects(text, font, color=None):
    if not color:
        color = (0, 0, 0)
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

class Player:
    def __init__(self, nick: str):
        self.nick = nick
        self.games = None
        self.best_score = None

    def average_score(self):
        if self.games and self.best_score:
            return self.best_score / self.games

    def __eq__(self, other):
        if self.nick == other.nick:
            True
        else:
            False


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

    SMALL_FONT = pygame.font.SysFont("comicsans", 35)
    STAT_FONT = pygame.font.SysFont("comicsans", 50)
    MID_FONT = pygame.font.SysFont("comicsans", 75)
    LARGE_FONT = pygame.font.SysFont("comicsans", 100)

    def __init__(self, side):
        self.mainloop = False
        self.menu_loop = False
        self.change_player_loop = False

        self.win = None
        self.clock = None

        self.TILE_WIDTH = self.WIDTH / side
        self.TILE_HEIGHT = self.HEIGHT / side

        self.SIDE = side

        self.snake = None
        self.food = None
        self.score = 0

        self.counter = 0

        self.db = None

        self.players = [Player("guest")]
        self.player = None
        self.player_index = 0

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
                        self.exit()

            self.win.fill((0, 0, 0))
            TextSurf, TextRect = text_objects("Snake", self.LARGE_FONT, (255, 255, 255))
            TextRect.center = (self.WIDTH / 2, 100)
            self.win.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(f"Best score: {self.player.best_score}", self.SMALL_FONT, (255, 255, 255))
            TextRect.center = (self.WIDTH - 100 , 50)
            self.win.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(f"{self.player.nick}", self.SMALL_FONT, (255, 255, 0))
            TextRect.center = (100 , 50)
            self.win.blit(TextSurf, TextRect)

            self.button("Play a Game", 100, 150, 220, 50, (0, 250, 0), (0, 200, 0), self.main)
            self.button("Change player", 100, 200, 260, 50, (255, 255, 0), (200, 200, 0), self.change_player)
            self.button("Exit", 100, 250, 140, 50, (255, 0, 0), (200, 0, 0), self.exit)


            pygame.display.update()
            self.clock.tick(15)


    def change_player(self):
        self.setup()
        self.change_player_loop = True
        while self.change_player_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        self.exit()

            self.win.fill((0, 0, 0))

            for i, player in enumerate(self.players):
                self.button(player.nick,
                            100, 150 + 50*i, # coordinates
                            220, 50, # size
                            (0, 250, 0), (0, 200, 0), # colors
                            lambda: self.switch_player(i)) # action
                if i != 0:
                    self.button("-", 50, 150 + 50*i, 50, 50, (250, 0, 0), (200, 0, 0), lambda: self.delete_player(i))

            self.button("+", self.WIDTH - 100, 50, 50, 50, (0, 250, 0), (0, 200, 0), self.add_player)


            pygame.display.update()
            self.clock.tick(15)

    def add_player(self):
        self.setup()
        self.add_player_loop = True
        name = ""
        while self.add_player_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                if event.type == pygame.KEYDOWN:
                    key = pygame.key.name(event.key)
                    if key in string.ascii_lowercase or key in string.digits:
                        name += key
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    if event.key == pygame.K_RETURN:
                        self.players.append(Player(name))
                        self.change_player()


            self.win.fill((0, 0, 0))

            TextSurf, TextRect = text_objects("type your nick:", self.STAT_FONT, (255, 255, 0))
            TextRect.center = (self.WIDTH // 2 , self.HEIGHT // 4)
            self.win.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(f"{name}", self.STAT_FONT, (255, 255, 0))
            TextRect.center = (self.WIDTH // 2 , self.HEIGHT // 2)
            self.win.blit(TextSurf, TextRect)


            pygame.display.update()
            self.clock.tick(60)




    def setup(self):
        self.mainloop = False
        self.menu_loop = False
        self.change_player_loop = False

        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()

        self.snake = Snake(self)
        self.food = Food(self)

        gameIcon = pygame.image.load('snake.png')
        pygame.display.set_icon(gameIcon)

        self.counter = 0
        self.score = 0


        self.db = Database("snake.db")
        if not self.db.table_exists('players'):
            self.db.create_table('players',
                            ('id integer PRIMARY KEY',
                            'nick text NOT NULL',
                            'best_score integer',
                            'games integer'
                            ))
            # for nick in ('matix0508', 'guest'):
            #     self.db.insert('players', (('nick', nick), ('best_score', '0'), ('games', '0')))
        self.db.create_connection()
        self.db.cursor.execute("SELECT * FROM players")
        data = self.db.cursor.fetchall()
        for player in data:
            _, nick, _, _ = player
            nicks = []
            for player in self.players:
                nicks.append(player.nick)
            if nick not in nicks:
                self.players.append(Player(nick))

        for player in self.players:
            if not self.db.row_exists('players', 'nick', player.nick):
                if not player.best_score:
                    player.best_score = 0
                if not player.games:
                    player.games = 0
                self.db.insert('players', (('nick', player.nick), ('best_score', player.best_score), ('games', player.games)))
            player.best_score = self.db.select('players', 'best_score', ('nick', player.nick))
            player.games = self.db.select('players', 'games', ('nick', player.nick))

        self.player = self.players[self.player_index]

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.exit()
            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
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

        TextSurf, TextRect = text_objects(f"score: {self.score}", self.SMALL_FONT, (255, 255, 255))
        TextRect.center = (self.WIDTH - 70 , 25)
        self.win.blit(TextSurf, TextRect)

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
        sleep(1)
        self.mainloop = False
        self.player.games += 1
        if self.score > self.player.best_score:
            self.player.best_score = self.score
            self.db.update('players', ('best_score', str(self.player.best_score)), ('nick', self.player.nick))

        self.db.update('players', ('games', str(self.player.games)), ('nick', self.player.nick))
        self.menu()
        # pygame.quit()
        # quit()


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

    def exit(self):
        pygame.quit()
        quit()

    def switch_player(self, i):
        self.player_index = i
        self.menu()

    def delete_player(self, i):
        nick = self.players[i]
        self.db.delete("players")
        self.db.create_connection()
        self.db.cursor.execute("SELECT * FROM players")
        data = self.db.cursor.fetchall()
        self.db.save()
        print(data)
        self.players.pop(i)

Game(13).menu()
