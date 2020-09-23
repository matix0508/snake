import string
from random import randint
from time import sleep

import pygame

from database import Database

pygame.font.init()


def text_objects(text, font, color=None):
    if not color:
        color = (0, 0, 0)
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


class Player:
    def __init__(self, nick: str, snake=None):
        self.nick = nick
        self.games = None
        self.best_score = None
        self.snake = snake
        self.score = 0

    def average_score(self):
        if self.games and self.best_score:
            return self.best_score / self.games

    def __eq__(self, other):
        if self.nick == other.nick:
            return True
        else:
            return False


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Position: [{self.x}, {self.y}]"

    def __add__(self, other):
        return Position(
            self.x + other.x,
            self.y + other.y
        )

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False


class Food:
    def __init__(self, game):
        self.position = Position(
            randint(0, game.SIDE - 1),
            randint(0, game.SIDE - 1)
        )

    def draw(self, game):
        pygame.draw.rect(
            game.win,
            (0, 255, 0),
            (
                self.position.x * game.TILE_WIDTH,
                self.position.y * game.TILE_HEIGHT,
                game.TILE_WIDTH - game.TILE_BORDER,
                game.TILE_HEIGHT - game.TILE_BORDER
            )
        )

    def respawn(self, game):
        self.position = Position(
            randint(0, game.SIDE - 1),
            randint(0, game.SIDE - 1)
        )
        for snake in game.snakes:
            while self.position in snake.body:
                self.position = Position(
                    randint(0, game.SIDE - 1),
                    randint(0, game.SIDE - 1)
                )

        # print(f"food: {self.position}")


class Snake:
    def __init__(self, game):
        self.body = [
            Position(
                randint(3, game.SIDE - 3),
                randint(3, game.SIDE - 3)
            )
        ]
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
        if self.head().y < self.side - 1:
            self.move(0, 1)
        else:
            self.game.game_over()

    def go_right(self):
        if self.head().x < self.side - 1:
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
        if new not in self.body:
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
                (
                    tile.x * game.TILE_WIDTH,
                    tile.y * game.TILE_HEIGHT,
                    game.TILE_WIDTH - game.TILE_BORDER,
                    game.TILE_HEIGHT - game.TILE_BORDER
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

        self.multiplayer = False

        self.mainloop = False
        self.menu_loop = False
        self.change_player_loop = False
        self.add_player_loop = False

        self.win = None
        self.clock = None

        self.TILE_WIDTH = self.WIDTH / side
        self.TILE_HEIGHT = self.HEIGHT / side

        self.SIDE = side

        self.snakes = []
        self.food = None
        self.score = 0

        self.counter = 0

        self.db = None

        self.players = [Player("guest")]
        self.player = None
        self.player2 = None
        self.player_index = 0
        self.player2_index = 1

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
            self.check_exit()

            self.win.fill((0, 0, 0))
            self.label(
                text="Snake",
                font=self.LARGE_FONT,
                color=(255, 255, 255),
                x=self.WIDTH / 2,
                y=100
            )

            self.label(
                text=f"Best score: {self.player.best_score}",
                font=self.SMALL_FONT,
                color=(255, 255, 255),
                x=self.WIDTH - 100,
                y=50
            )

            self.label(
                text=f"{self.player.nick}",
                font=self.SMALL_FONT,
                color=(255, 255, 0),
                x=100,
                y=50
            )

            self.button(
                text="Play a Game",
                x=100, y=150,
                width=220, height=50,
                main_color=(0, 250, 0),
                mouse_color=(0, 200, 0),
                action=self.main
            )
            self.button(
                text="Change player",
                x=100, y=200,
                width=260, height=50,
                main_color=(255, 255, 0),
                mouse_color=(200, 200, 0),
                action=self.change_player
            )
            if len(self.players) > 1:
                self.button(
                    text="Multiplier",
                    x=100, y=250,
                    width=180, height=50,
                    main_color=(255, 0, 255),
                    mouse_color=(200, 0, 200),
                    action=self.choose_players()
                )
            self.button(
                text="Exit",
                x=100, y=300,
                width=140, height=50,
                main_color=(255, 0, 0),
                mouse_color=(200, 0, 0),
                action=self.exit
            )

            pygame.display.update()
            self.clock.tick(15)

    def change_player(self):
        self.setup()
        self.change_player_loop = True
        while self.change_player_loop:
            self.check_exit()

            self.win.fill((0, 0, 0))

            for i, player in enumerate(self.players):
                self.button(
                    text=player.nick,
                    x=100,
                    y=150 + 50 * i,
                    width=220,
                    height=50,
                    main_color=(0, 250, 0),
                    mouse_color=(0, 200, 0),
                    action=lambda: self.switch_player(i)
                )
                if i != 0:
                    self.button(
                        text="-",
                        x=50,
                        y=150 + 50 * i,
                        width=50,
                        height=50,
                        main_color=(250, 0, 0),
                        mouse_color=(200, 0, 0),
                        action=lambda: self.delete_player(i)
                    )

            self.button(
                text="+",
                x=self.WIDTH - 100,
                y=50,
                width=50,
                height=50,
                main_color=(0, 250, 0),
                mouse_color=(0, 200, 0),
                action=self.add_player
            )

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

            self.label(
                text="type your nick:",
                font=self.STAT_FONT,
                color=(255, 255, 0),
                x=self.WIDTH // 2,
                y=self.HEIGHT // 4
            )

            self.label(
                text=f"{name}",
                font=self.STAT_FONT,
                color=(255, 255, 0),
                x=self.WIDTH // 2,
                y=self.HEIGHT // 2
            )

            pygame.display.update()
            self.clock.tick(60)

    def setup(self):
        self.mainloop = False
        self.menu_loop = False
        self.change_player_loop = False

        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()

        self.snakes = [Snake(self)]
        if self.multiplayer:
            self.snakes.append(Snake(self))
        self.food = Food(self)

        gameIcon = pygame.image.load('snake.png')
        pygame.display.set_icon(gameIcon)

        self.counter = 0
        self.score = 0

        self.db = Database("snake.db")
        if not self.db.table_exists('players'):
            self.db.create_table(
                'players',
                (
                    'id integer PRIMARY KEY',
                    'nick text NOT NULL',
                    'best_score integer',
                    'games integer'
                )
            )
            # for nick in ('matix0508', 'guest'):
            #     self.db.insert('players', (('nick', nick), ('best_score', '0'), ('games', '0')))
        self.db.create_connection()
        self.db.cursor.execute("SELECT * FROM players")
        data = self.db.cursor.fetchall()
        for player_data in data:
            _, nick, _, _ = player_data
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
                self.db.insert(
                    'players',
                    (
                        ('nick', player.nick),
                        ('best_score', player.best_score),
                        ('games', player.games)
                    )
                )

            player.best_score = self.db.select(
                'players',
                'best_score',
                ('nick', player.nick)
            )
            player.games = self.db.select(
                'players',
                'games',
                ('nick', player.nick)
            )

        self.player = self.players[self.player_index]
        self.player.snake = self.snakes[0]
        if self.multiplayer:
            self.player2 = self.players[self.player2_index]

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snakes[0].move_reset()
                    self.snakes[0].up = True
                if event.key == pygame.K_DOWN:
                    self.snakes[0].move_reset()
                    self.snakes[0].down = True
                if event.key == pygame.K_RIGHT:
                    self.snakes[0].move_reset()
                    self.snakes[0].right = True
                if event.key == pygame.K_LEFT:
                    self.snakes[0].move_reset()
                    self.snakes[0].left = True

                if self.multiplayer:
                    if event.key == pygame.K_w:
                        self.snakes[1].move_reset()
                        self.snakes[1].up = True
                    if event.key == pygame.K_s:
                        self.snakes[1].move_reset()
                        self.snakes[1].down = True
                    if event.key == pygame.K_d:
                        self.snakes[1].move_reset()
                        self.snakes[1].right = True
                    if event.key == pygame.K_a:
                        self.snakes[1].move_reset()
                        self.snakes[1].left = True

    def draw_window(self):

        self.win.fill((0, 0, 0))  # Black background

        for i in range(self.SIDE):
            for j in range(self.SIDE):
                pygame.draw.rect(
                    self.win,
                    (255, 255, 255),
                    (
                        i * self.TILE_WIDTH,
                        j * self.TILE_HEIGHT,
                        self.TILE_WIDTH,
                        self.TILE_HEIGHT
                    ),
                    self.TILE_BORDER
                )

        self.food.draw(self)
        for snake in self.snakes:
            snake.draw(self)

        self.label(
            f"score: {self.player.score}",
            self.SMALL_FONT,
            (255, 255, 255),
            self.WIDTH - 70, 25
        )

        pygame.display.update()

    def update(self):
        self.counter += 1
        for snake in self.snakes:

            if self.counter % 5 == 0:
                if snake.up:
                    snake.go_up()
                if snake.down:
                    snake.go_down()
                if snake.right:
                    snake.go_right()
                if snake.left:
                    snake.go_left()

        if self.multiplayer:
            for pl in (self.player, self.player2):
                self.check_food(pl)
        else:
            self.check_food(self.player)

    def check_food(self, player):
        if player.snake.head() == self.food.position:
            player.score += 1
            player.snake.add = True
            self.food.respawn(self)

    def game_over(self):
        sleep(1)
        self.mainloop = False
        self.player.games += 1
        if self.multiplayer:
            lst = [self.player, self.player2]
        else:
            lst = [self.player]
        for player in lst:
            if player.score > player.best_score:
                player.best_score = player.score
                self.db.update(
                    'players',
                    ('best_score', str(player.best_score)),
                    ('nick', player.nick)
                )

        self.db.update(
            'players',
            ('games', str(self.player.games)),
            ('nick', self.player.nick)
        )
        self.menu()
        # pygame.quit()
        # quit()

    def button(self, text, x, y, width, height, main_color, mouse_color, action=None):
        """
        helps to create buttons on the screen
        """
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x + width > mouse[0] > x and y + height > mouse[1] > y:
            pygame.draw.rect(self.win, mouse_color, (x, y, width, height))
            if click[0] == 1 and action:
                action()

        else:
            pygame.draw.rect(self.win, main_color, (x, y, width, height))

        self.label(
            text=text,
            font=self.STAT_FONT,
            color=(0, 0, 0),
            x=x + (width / 2),
            y=y + (height / 2)
        )

    def label(self, text: str, font, color, x, y):
        TextSurf, TextRect = text_objects(
            text,
            font,
            color
        )
        TextRect.center = (x, y)
        self.win.blit(TextSurf, TextRect)

    @staticmethod
    def exit():
        pygame.quit()
        quit()

    def switch_player(self, i):
        self.player_index = i
        self.menu()

    def delete_player(self, i):
        self.db.delete("players")
        self.db.create_connection()
        self.db.cursor.execute("SELECT * FROM players")
        data = self.db.cursor.fetchall()
        self.db.save()
        print(data)
        self.players.pop(i)

    def choose_players(self):
        pass

    def check_exit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()


Game(13).menu()
