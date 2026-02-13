import pygame
import math

# --- Configuration ---
WIDTH, HEIGHT = 1200, 650
FPS = 60

# Colors
PORSCHE_RED = (186, 12, 47)
ASPHALT = (45, 45, 48)
GRASS = (34, 139, 34)
WHITE = (255, 255, 255)
KERB_RED = (200, 0, 0)

# --- The Track Logic ---
# Optimized points to utilize the 1200x650 widescreen area
TRACK_POINTS = [
    (150, 325), (200, 150), (600, 80), (1000, 150), 
    (1050, 325), (950, 500), (600, 570), (250, 500)
]

class Porsche911:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.angle = 0
        self.speed = 0
        self.max_speed = 8.0
        
        # Create Porsche 911 Body
        self.image = pygame.Surface((32, 60), pygame.SRCALPHA)
        # Main chassis
        pygame.draw.rect(self.image, PORSCHE_RED, (0, 0, 32, 60), border_radius=10)
        # Windshield/Cockpit
        pygame.draw.rect(self.image, (25, 25, 25), (5, 15, 22, 18), border_radius=4) 
        # Iconic 911 Rear wide-body look
        pygame.draw.rect(self.image, PORSCHE_RED, (0, 35, 32, 20), border_radius=5)
        # Headlights
        pygame.draw.circle(self.image, (245, 245, 245), (7, 6), 5)
        pygame.draw.circle(self.image, (245, 245, 245), (25, 6), 5)

    def update(self, on_track):
        keys = pygame.key.get_pressed()
        
        # Terrain Physics: 75% speed reduction on grass
        current_limit = self.max_speed if on_track else 2.0
        
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + 0.12, current_limit)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - 0.25, -2.5)
        else:
            self.speed *= 0.97 # Friction/Drag

        if abs(self.speed) > 0.1:
            steer_dir = 1 if self.speed > 0 else -1
            if keys[pygame.K_LEFT]: self.angle += 4.5 * steer_dir
            if keys[pygame.K_RIGHT]: self.angle -= 4.5 * steer_dir

        # Movement Vector (Trigonometry-based displacement)
        velocity = pygame.Vector2(0, -self.speed).rotate(-self.angle)
        self.pos += velocity

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.pos.x, self.pos.y))
        screen.blit(rotated, rect.topleft)

# --- Main Engine ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Porsche 911 Carrera Circuit - Computer Graphics Project")
clock = pygame.time.Clock()
porsche = Porsche911(150, 325)

while True:
    # Layer 0: Environment
    screen.fill(GRASS)

    # Layer 1: Track Construction
    # We draw the track slightly larger first to create 'Kerbs'
    pygame.draw.polygon(screen, KERB_RED, TRACK_POINTS, 120)
    pygame.draw.polygon(screen, WHITE, TRACK_POINTS, 110) # Checker pattern effect
    pygame.draw.polygon(screen, ASPHALT, TRACK_POINTS, 100) # Racing surface

    # Layer 2: Logic & Collision
    is_on_track = False
    try:
        # Color-sampled collision detection
        # This checks the pixel directly under the car's center
        pixel_color = screen.get_at((int(porsche.pos.x), int(porsche.pos.y)))
        if pixel_color == ASPHALT:
            is_on_track = True
    except: is_on_track = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); exit()

    porsche.update(is_on_track)

    # Layer 3: Start/Finish Line
    pygame.draw.line(screen, (255, 255, 255), (80, 325), (220, 325), 8)
    
    # Layer 4: Actor (The Car)
    porsche.draw(screen)

    # Layer 5: HUD (Dashboard)
    pygame.draw.rect(screen, (0, 0, 0), (20, 20, 350, 50), border_radius=5)
    font = pygame.font.SysFont("Verdana", 18, bold=True)
    status_txt = "ON TRACK" if is_on_track else "OFF TRACK - TRACTION LOST"
    status_color = (0, 255, 0) if is_on_track else (255, 50, 50)
    
    info = font.render(f"PORSCHE 911 | {status_txt}", True, status_color)
    screen.blit(info, (35, 33))

    pygame.display.flip()
    clock.tick(FPS)