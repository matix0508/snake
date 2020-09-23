import pygame
pygame.font.init()


class View:
    def __init__(self, function):
        self.function = function

    def __call__(self, game):
        game.setup()
        while True:
            self.function(game)


class Game:

    SMALL_FONT = pygame.font.SysFont("comicsans", 35)
    STAT_FONT = pygame.font.SysFont("comicsans", 50)
    MID_FONT = pygame.font.SysFont("comicsans", 75)
    LARGE_FONT = pygame.font.SysFont("comicsans", 100)

    def __init__(self, width, height, title):
        self.WIDTH = width
        self.HEIGHT = height
        self.TITLE = title
        self.TICK = 30

        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()

        self.mainloop = False
        self.count = 0

    @View
    def main(self):
        self.clock.tick(self.TICK)
        self.update()
        self.check_events()

        self.draw_window()

    def setup(self):
        self.mainloop = False

    def update(self):
        self.count += 1

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()

    def draw_window(self):
        self.win.fill((0, 0, 0))

        self.label(
            text=f"Welcome to {self.TITLE} game",
            font=self.STAT_FONT,
            color=(255, 255, 255),
            x=self.WIDTH / 2,
            y=self.HEIGHT / 2
        )
        self.label(str(self.count), self.SMALL_FONT, (255, 0, 0), 100, 100)

        pygame.display.update()

    @staticmethod
    def exit():
        pygame.quit()
        quit()

    def check_exit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()

    def label(self, text: str, font, color, x, y):
        TextSurf, TextRect = self.text_objects(
            text,
            font,
            color
        )
        TextRect.center = (x, y)
        self.win.blit(TextSurf, TextRect)

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

    @staticmethod
    def text_objects(text, font, color=None):
        if not color:
            color = (0, 0, 0)
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()



