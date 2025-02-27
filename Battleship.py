import pygame
import random
import sys

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

GRID_SIZE = 10
PADDING = 50
CELL_SIZE = min((WIDTH - 2 * PADDING) // (GRID_SIZE * 2), (HEIGHT - 2 * PADDING) // GRID_SIZE)
FPS = 30

background_image = pygame.image.load(r"sea.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

win_image = pygame.image.load(r"win.jpg")
win_image = pygame.transform.scale(win_image, (WIDTH, HEIGHT))

miss_image = pygame.image.load(r"miss.jpg")
miss_image.set_colorkey((0, 0, 0))
miss_image = pygame.transform.scale(miss_image, (CELL_SIZE, CELL_SIZE))

hit_image = pygame.image.load(r"hit1.jpg")
hit_image.set_colorkey((255, 255, 255))
hit_image = pygame.transform.scale(hit_image, (CELL_SIZE, CELL_SIZE))

hit_sound = pygame.mixer.Sound('hit.wav')
miss_sound = pygame.mixer.Sound('miss.wav')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SHIP_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

def start_screen(screen):
    intro_text = ["Добро пожаловать в игру 'Морской бой'"]

    font = pygame.font.Font(None, 40)
    button_start = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
    button_rules = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)

    while True:
        screen.fill(WHITE)
        for line in intro_text:
            string_rendered = font.render(line, True, (0, 0, 0))
            intro_rect = string_rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + intro_text.index(line) * 50))
            screen.blit(string_rendered, intro_rect)

        pygame.draw.rect(screen, BLACK, button_start)
        pygame.draw.rect(screen, BLACK, button_rules)

        start_text = font.render("Начать", True, WHITE)
        rules_text = font.render("Правила", True, WHITE)
        screen.blit(start_text, (button_start.x + 50, button_start.y + 10))
        screen.blit(rules_text, (button_rules.x + 50, button_rules.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_start.collidepoint(event.pos):
                        return
                    elif button_rules.collidepoint(event.pos):
                        show_rules(screen)

def show_rules(screen):
    rules_text = [
        "Правила игры:",
        "1. Игроки по очереди стреляют по клеткам противника.",
        "2. Если игрок попадает в корабль, он продолжает стрелять.",
        "3. Если игрок промахивается, ход переходит к противнику.",
        "4. Игра заканчивается, когда все корабли одного из игроков потоплены.",
        "5. На ход дается 30 секунд, после истечения таймера ход переходит противнику",
        "",
        "Нажмите любую клавишу, чтобы вернуться на заставку."
    ]

    font = pygame.font.Font(None, 40)
    text_coord = 50

    while True:
        screen.fill(WHITE)
        text_coord = 50
        for line in rules_text:
            string_rendered = font.render(line, True, (0, 0, 0))
            intro_rect = string_rendered.get_rect(center=(WIDTH // 2, text_coord))
            screen.blit(string_rendered, intro_rect)
            text_coord += 50

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                return

class Battleship:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Морской бой")
        self.clock = pygame.time.Clock()
        self.grid1 = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.grid2 = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.current_player = 1
        self.running = True
        self.time_limit = 30
        self.start_time = pygame.time.get_ticks()
        self.place_ships(self.grid1)
        self.place_ships(self.grid2)
        self.ships_remaining1 = len(SHIP_SIZES)
        self.ships_remaining2 = len(SHIP_SIZES)
        self.active_filed = 2

    def is_valid_location(self, grid, x, y, size, direction):
        if direction == "horizontal":
            if x + size > GRID_SIZE:
                return False
            for i in range(-1, size + 1):
                for j in range(-1, 2):
                    if 0 <= y + j < GRID_SIZE and 0 <= x + i < GRID_SIZE:
                        if grid[y + j][x + i] == 1:
                            return False
        else:
            if y + size > GRID_SIZE:
                return False
            for i in range(-1, size + 1):
                for j in range(-1, 2):
                    if 0 <= y + i < GRID_SIZE and 0 <= x + j < GRID_SIZE:
                        if grid[y + i][x + j] == 1:
                            return False
        return True

    def place_ships(self, grid):
        for size in SHIP_SIZES:
            while True:
                direction = random.choice(["horizontal", "vertical"])
                if direction == "horizontal":
                    x = random.randint(0, GRID_SIZE - size)
                    y = random.randint(0, GRID_SIZE - 1)
                    if self.is_valid_location(grid, x, y, size, direction):
                        for i in range(size):
                            grid[y][x + i] = 1
                        break
                else:
                    x = random.randint(0, GRID_SIZE - 1)
                    y = random.randint(0, GRID_SIZE - size)
                    if self.is_valid_location(grid, x, y, size, direction):
                        for i in range(size):
                            grid[y + i][x] = 1
                        break

    def draw_grid(self, grid, offset_x, hide_ships=True):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(offset_x + x * CELL_SIZE, (HEIGHT - GRID_SIZE * CELL_SIZE) // 2 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if grid[y][x] == -1:
                    self.screen.blit(hit_image, rect.topleft)
                elif grid[y][x] == -2:
                    self.screen.blit(miss_image, rect.topleft)
                else:
                    if not hide_ships and grid[y][x] == 1:
                        pygame.draw.rect(self.screen, BLACK, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

    def check_win(self, grid):
        return all(cell != 1 for row in grid for cell in row)

    def draw_win(self, text, color):
        font = pygame.font.Font(None, 50)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)

    def show_win_screen(self, winner):
        self.screen.blit(win_image, (0, 0))
        self.draw_win(f"Игрок {winner} победил!", BLACK)
        pygame.display.flip()
        pygame.time.delay(3000)
        self.running = False

    def draw_time(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        font = pygame.font.Font(None, 36)
        time_surface = font.render(f"Осталось времени: {self.time_limit - elapsed_time} секунд", True, BLACK)
        self.screen.blit(time_surface, (10, 10))

    def find_ship_cells(self, grid, x, y, visited=None):
        if visited is None:
            visited = set()
        if (x, y) in visited or not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return visited
        if grid[y][x] != 1 and grid[y][x] != -1:
            return visited
        visited.add((x, y))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.find_ship_cells(grid, x + dx, y + dy, visited)
        return visited

    def check_sunk_ship(self, grid, x, y):
        if grid[y][x] == -1:
            ship_cells = self.find_ship_cells(grid, x, y)
            sunk = all(grid[cell_y][cell_x] == -1 for cell_x, cell_y in ship_cells)
            if sunk:
                for cell_x, cell_y in ship_cells:
                    self.reveal_surrounding_cells(grid, cell_x, cell_y)
                if grid is self.grid1:
                    self.ships_remaining2 -= 1
                else:
                    self.ships_remaining1 -= 1
            return sunk
        return False

    def reveal_surrounding_cells(self, grid, x, y):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= x + i < GRID_SIZE and 0 <= y + j < GRID_SIZE:
                    if grid[y + j][x + i] == 0:
                        grid[y + j][x + i] = -2

    def draw_ships_remaining(self):
        font = pygame.font.Font(None, 40)

        text1 = font.render(f"Корабли игрока {self.ships_remaining2}", True, BLACK)
        self.screen.blit(text1, (10,  HEIGHT - 50))

        text2 = font.render(f"Корабли игрока {self.ships_remaining1}", True, BLACK)
        self.screen.blit(text2, (WIDTH - 300,  HEIGHT - 50))

    def highlight_active_field(self):
        darken_surface = pygame.Surface((WIDTH // 2, HEIGHT), pygame.SRCALPHA)
        darken_surface.fill((0, 0, 0, 128))

        if self.active_filed == 2:
            self.screen.blit(darken_surface, (WIDTH // 2, 0))
        else:
            self.screen.blit(darken_surface, (0, 0))


    def run(self):
        start_screen(self.screen)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = event.pos
                        if self.current_player == 1:
                            grid_x, grid_y = (x - WIDTH // 2) // CELL_SIZE, (
                                    y - (HEIGHT - GRID_SIZE * CELL_SIZE) // 2) // CELL_SIZE
                            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                                if self.grid2[grid_y][grid_x] not in (-1, -2):
                                    if self.grid2[grid_y][grid_x] == 1:
                                        self.grid2[grid_y][grid_x] = -1
                                        hit_sound.play()
                                        self.check_sunk_ship(self.grid2, grid_x, grid_y)
                                    else:
                                        self.grid2[grid_y][grid_x] = -2
                                        miss_sound.play()
                                        self.start_time = pygame.time.get_ticks()
                                        self.current_player = 2
                                        self.active_filed = 2
                        else:
                            grid_x, grid_y = (x - (WIDTH // 2 - GRID_SIZE * CELL_SIZE) // 2) // CELL_SIZE, (
                                    y - (HEIGHT - GRID_SIZE * CELL_SIZE) // 2) // CELL_SIZE
                            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                                if self.grid1[grid_y][grid_x] not in (-1, -2):
                                    if self.grid1[grid_y][grid_x] == 1:
                                        self.grid1[grid_y][grid_x] = -1
                                        hit_sound.play()
                                        self.check_sunk_ship(self.grid1, grid_x, grid_y)
                                    else:
                                        self.grid1[grid_y][grid_x] = -2
                                        miss_sound.play()
                                        self.start_time = pygame.time.get_ticks()
                                        self.current_player = 1
                                        self.active_filed = 1

            elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
            if elapsed_time >= self.time_limit:
                self.current_player = 2 if self.current_player == 1 else 1
                self.active_filed = 1 if self.active_filed == 2 else 2
                self.start_time = pygame.time.get_ticks()

            if self.check_win(self.grid1):
                self.show_win_screen(2)
            elif self.check_win(self.grid2):
                self.show_win_screen(1)

            self.screen.blit(background_image, (0, 0))
            self.draw_grid(self.grid1, (WIDTH // 2 - GRID_SIZE * CELL_SIZE) // 2)
            self.draw_grid(self.grid2, WIDTH // 2 + (WIDTH // 2 - GRID_SIZE * CELL_SIZE) // 2)
            self.draw_time()
            self.draw_ships_remaining()
            self.highlight_active_field()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Battleship()
    game.run()
