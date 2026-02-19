import pygame
import random
import math

# --- Configuration ---
WIDTH, HEIGHT = 1200, 650
FPS = 120

# Colors
SAND = (194, 178, 128)
WHITE = (135, 206, 235)
BUOY_RED = (220, 40, 40)
ROCK_GRAY = (110, 110, 110)
LOG_BROWN = (140, 90, 40)
WATER_COLOR = (135, 206, 235)  # Sky Blue

pygame.init()

# --- Track waypoints ---
TRACK_POINTS = [
    (150, 325), (200, 150), (600, 80), (1000, 150),
    (1050, 325), (950, 500), (600, 570), (250, 500)
]
FINISH_LINE = ((80, 325), (220, 325))

# ---------------------------------------------------------
# Wake particles
# ---------------------------------------------------------
class WakeParticle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.alpha = 255
        self.size = random.randint(5, 10)

    def update(self):
        self.alpha -= 4
        return self.alpha > 0

    def draw(self, screen):
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, self.alpha),
                           (self.size//2, self.size//2), self.size//2)
        screen.blit(surf, (self.pos.x - self.size//2, self.pos.y - self.size//2))

# ---------------------------------------------------------
# Obstacles
# ---------------------------------------------------------
class Obstacle:
    def __init__(self, x, y, type):
        self.pos = pygame.Vector2(x, y)
        self.type = type
        self.offset = 0
        if type == "rock": self.size = random.randint(25, 40)
        elif type == "log": self.size = random.randint(50, 80)
        else: self.size = 25

    def draw(self, screen):
        if self.type == "rock":
            pygame.draw.circle(screen, ROCK_GRAY, (int(self.pos.x), int(self.pos.y)), self.size)
        elif self.type == "log":
            pygame.draw.rect(screen, LOG_BROWN,
                             (self.pos.x - self.size//2, self.pos.y - 10, self.size, 20),
                             border_radius=5)
        else:
            pygame.draw.circle(screen, BUOY_RED, (int(self.pos.x), int(self.pos.y)), self.size//2)

        # bobbing animation
        self.offset += 0.03
        self.pos.y += math.sin(self.offset) * 0.3

# ---------------------------------------------------------
# Boat class
# ---------------------------------------------------------
class SpeedBoat:
    def __init__(self, x, y, color, controls=None):
        self.pos = pygame.Vector2(x, y)
        self.angle = 0
        self.speed = 0
        self.max_speed = 6.0
        self.boost_power = 4.0
        self.color = color
        self.controls = controls
        self.laps = 0
        self.prev_pos = self.pos.copy()
        self.wake_particles = []

        self.image = pygame.Surface((28,70), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, color, [(14,0),(0,20),(0,60),(28,60),(28,20)])
        pygame.draw.rect(self.image, WHITE, (6,25,16,25), border_radius=4)
        pygame.draw.rect(self.image, (10,10,10), (6,15,16,10), border_radius=3)

    # Lap detection
    def update_laps(self):
        (x1,y1),(x2,y2) = FINISH_LINE
        crossed = (self.prev_pos.y > y1 and self.pos.y <= y1 and x1 <= self.pos.x <= x2)
        if crossed: self.laps += 1
        self.prev_pos = self.pos.copy()

    # Player-controlled update
    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        boosting = keys[self.controls['boost']]
        limit = self.max_speed + (self.boost_power if boosting else 0)
        if keys[self.controls['up']]: self.speed = min(self.speed + 0.10, limit)
        elif keys[self.controls['down']]: self.speed = max(self.speed - 0.15, -2)
        else: self.speed *= 0.98
        if abs(self.speed) > 0.2:
            steer = 1 if self.speed > 0 else -1
            if keys[self.controls['left']]: self.angle += 3*steer
            if keys[self.controls['right']]: self.angle -= 3*steer

        vel = pygame.Vector2(0,-self.speed).rotate(-self.angle)
        self.pos += vel

        # Wake particles
        back = pygame.Vector2(0,25).rotate(-self.angle)
        self.wake_particles.append(WakeParticle(self.pos.x+back.x, self.pos.y+back.y))
        self.wake_particles = [p for p in self.wake_particles if p.update()]

        # Collision with obstacles
        for obs in obstacles:
            if obs.type == "rock" or obs.type == "buoy":
                radius = obs.size if obs.type=="rock" else obs.size//2
                if self.pos.distance_to(obs.pos) < radius + 14:
                    self.speed *= -0.1
            elif obs.type == "log":
                if abs(self.pos.x - obs.pos.x) < obs.size/2 + 14 and abs(self.pos.y - obs.pos.y) < 20 + 35:
                    self.speed *= -0.1

        self.update_laps()

    def draw(self, screen):
        for p in self.wake_particles: p.draw(screen)
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.pos.x,self.pos.y))
        screen.blit(rotated, rect.topleft)

# ---------------------------------------------------------
# Minimap
# ---------------------------------------------------------
def draw_minimap(screen, boats):
    mini_width, mini_height = 120, 120
    margin = 20
    pygame.draw.rect(screen, (20,20,20), (WIDTH - mini_width - margin, margin, mini_width, mini_height), border_radius=6)

    scale_x = mini_width / WIDTH
    scale_y = mini_height / HEIGHT

    # Track points
    for p in TRACK_POINTS:
        mx = int((WIDTH - mini_width - margin) + p[0]*scale_x)
        my = int(margin + p[1]*scale_y)
        pygame.draw.circle(screen, (150,150,150), (mx,my), 2)

    # Boats
    for b in boats:
        mx = int((WIDTH - mini_width - margin) + b.pos.x*scale_x)
        my = int(margin + b.pos.y*scale_y)
        pygame.draw.circle(screen, b.color, (mx,my), 3)

# ---------------------------------------------------------
# Main Loop
# ---------------------------------------------------------
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Boat Racing - 2 Player Multiplayer")
clock = pygame.time.Clock()

# Track polygon mask for obstacle placement
track_mask_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.draw.polygon(track_mask_surface, (255,255,255), TRACK_POINTS)
track_mask = pygame.mask.from_surface(track_mask_surface)

# Generate obstacles only on water
obstacles = []
while len(obstacles) < 12:
    ox = random.randint(0, WIDTH-1)
    oy = random.randint(0, HEIGHT-1)
    if track_mask.get_at((ox, oy)):
        t = random.choice(["rock","log","buoy"])
        obstacles.append(Obstacle(ox, oy, t))

# Define controls for both players
player1_controls = {'up':pygame.K_UP,'down':pygame.K_DOWN,'left':pygame.K_LEFT,'right':pygame.K_RIGHT,'boost':pygame.K_RSHIFT}
player2_controls = {'up':pygame.K_w,'down':pygame.K_s,'left':pygame.K_a,'right':pygame.K_d,'boost':pygame.K_LSHIFT}

player1 = SpeedBoat(150,325,(255,0,0),controls=player1_controls)
player2 = SpeedBoat(170,325,(0,0,255),controls=player2_controls)
boats = [player1, player2]

wave_offset = 0
winner = None

while True:
    screen.fill(SAND)

    # Water
    pygame.draw.polygon(screen, WATER_COLOR, TRACK_POINTS, 100)
    pygame.draw.polygon(screen, BUOY_RED, TRACK_POINTS, 120)
    pygame.draw.polygon(screen, WHITE, TRACK_POINTS, 110)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Update boats
    if winner is None:
        for b in boats: b.update(obstacles)
        for b in boats:
            if b.laps >= 3:
                winner = b
                break

    # Draw obstacles
    for obs in obstacles: obs.draw(screen)

    # Finish line
    pygame.draw.line(screen,WHITE,FINISH_LINE[0],FINISH_LINE[1],6)

    # Draw boats
    for b in boats: b.draw(screen)

    # Minimap
    draw_minimap(screen, boats)

    # HUD
    pygame.draw.rect(screen,(0,0,0),(20,20,500,50),border_radius=5)
    font = pygame.font.SysFont("Verdana",18,bold=True)
    laps_text = font.render(
        f"RED: {player1.laps} | BLUE: {player2.laps}",
        True,WHITE
    )
    screen.blit(laps_text,(35,33))

    # Winner
    if winner:
        big_font = pygame.font.SysFont("Verdana",72,bold=True)
        win_txt = big_font.render(
            f"{'RED' if winner==player1 else 'BLUE'} WINS!",
            True,(255,255,0)
        )
        screen.blit(win_txt,(WIDTH//2 - win_txt.get_width()//2,
                             HEIGHT//2 - win_txt.get_height()//2))

    pygame.display.flip()
    clock.tick(FPS)
