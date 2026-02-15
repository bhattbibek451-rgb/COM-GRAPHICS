import pygame, math, sys, random, os

pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Haunted House Stickman Edition")
clock = pygame.time.Clock()

# --- Sounds ---
pygame.mixer.init()
ghost_sound = None
jump_scare_sound = None

if os.path.exists("ghost.mp3"):
    ghost_sound = pygame.mixer.Sound("ghost.mp3")
    ghost_sound.set_volume(100)

if os.path.exists("jumpscare.mp3"):
    jump_scare_sound = pygame.mixer.Sound("jumpscare.mp3")
    jump_scare_sound.set_volume(100)

# --- Map ---
FLOOR = [
    [1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1]
]

MAP_WIDTH = len(FLOOR[0])
MAP_HEIGHT = len(FLOOR)
TILE = 64

# Player
player_x = TILE*1.5
player_y = TILE*1.5
player_angle = 0
player_speed = 2

# Colors
WHITE = (255,255,255)
WALL_COLOR = (40,40,40)
CEILING_COLOR = (20,20,20)
FLOOR_COLOR = (40,40,40)

FOV = math.pi/3
NUM_RAYS = 120
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
DIST_PROJ_PLANE = (WIDTH/2)/math.tan(FOV/2)
SCALE = WIDTH // NUM_RAYS

# ------------- STICKMAN GENERATOR --------------
def make_stickman(size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size//2, size//2

    pygame.draw.circle(surf, WHITE, (cx, cy-size//4), size//8, 3)
    pygame.draw.line(surf, WHITE, (cx, cy-size//8), (cx, cy+size//6), 3)
    pygame.draw.line(surf, WHITE, (cx, cy), (cx-size//6, cy-size//10), 3)
    pygame.draw.line(surf, WHITE, (cx, cy), (cx+size//6, cy-size//10), 3)
    pygame.draw.line(surf, WHITE, (cx, cy+size//6), (cx-size//8, cy+size//3), 3)
    pygame.draw.line(surf, WHITE, (cx, cy+size//6), (cx+size//8, cy+size//3), 3)
    return surf

# Scale stickmen to 75% of previous TILE//1.5 size
STICKMAN = make_stickman(int(TILE//1.5 * 0.75))

# ------------- STICKMAN CLASS ---------------
class StickmanMove:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = STICKMAN
        self.dx = random.choice([-1,1])
        self.dy = random.choice([-1,1])
        self.jump_triggered = False

    def move(self):
        nx = self.x + self.dx*0.4
        ny = self.y + self.dy*0.4
        if FLOOR[int(ny//TILE)][int(nx//TILE)] == 0:
            self.x, self.y = nx, ny
        else:
            self.dx *= -1
            self.dy *= -1

# Create moving stickmen
stickmen = [
    StickmanMove(TILE*3.5, TILE*2.5),
    StickmanMove(TILE*5.5, TILE*1.5),
    StickmanMove(TILE*2.5, TILE*3.5),
    StickmanMove(TILE*4.5, TILE*4.0)
]

# ---------------- RAYCAST --------------------
def raycast():
    start_angle = player_angle - FOV/2

    for ray in range(NUM_RAYS):
        angle = start_angle + ray*DELTA_ANGLE
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        for depth in range(MAX_DEPTH):
            x = player_x + cos_a * depth
            y = player_y + sin_a * depth

            i = int(x//TILE)
            j = int(y//TILE)

            if FLOOR[j][i] == 1:
                h = min(int(DIST_PROJ_PLANE*TILE/(depth+0.01)), HEIGHT)
                pygame.draw.rect(window, (80,80,80), (ray*SCALE, HEIGHT/2 - h/2, SCALE, h))
                break

# ---------------- SPRITE PROJECTION ----------------
def draw_sprite(x, y, sprite):
    dx, dy = x - player_x, y - player_y
    dist = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    gamma = ang - player_angle

    if -FOV/2 < gamma < FOV/2:
        h = min(int(DIST_PROJ_PLANE*TILE/(dist+0.01)), HEIGHT)
        screen_x = int((WIDTH/2)*(1 + math.tan(gamma)/math.tan(FOV/2))) - h//2
        sp = pygame.transform.scale(sprite, (h, h))
        window.blit(sp, (screen_x, HEIGHT//2 - h//2))
        return dist
    return None

# ---------------- MAIN LOOP ----------------
running = True
while running:
    window.fill(FLOOR_COLOR)
    pygame.draw.rect(window, CEILING_COLOR, (0,0,WIDTH,HEIGHT//2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player_angle -= 0.03
    if keys[pygame.K_RIGHT]: player_angle += 0.03

    if keys[pygame.K_UP]:
        nx = player_x + player_speed*math.cos(player_angle)
        ny = player_y + player_speed*math.sin(player_angle)
        if FLOOR[int(ny//TILE)][int(nx//TILE)] == 0:
            player_x, player_y = nx, ny

    if keys[pygame.K_DOWN]:
        nx = player_x - player_speed*math.cos(player_angle)
        ny = player_y - player_speed*math.sin(player_angle)
        if FLOOR[int(ny//TILE)][int(nx//TILE)] == 0:
            player_x, player_y = nx, ny

    raycast()

    # stickmen
    for s in stickmen:
        s.move()
        dist = draw_sprite(s.x, s.y, s.sprite)

        if dist and ghost_sound and dist < 120:
            ghost_sound.play()

        if dist and jump_scare_sound and dist < 50 and not s.jump_triggered:
            jump_scare_sound.play()
            s.jump_triggered = True
        else:
            s.jump_triggered = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
