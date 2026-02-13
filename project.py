import pygame
import math

# --- Configuration & Colors ---
WIDTH, HEIGHT = 1000, 700
MCLAREN_ORANGE = (255, 135, 0)
ASPHALT_GREY = (40, 40, 40)
WHITE = (255, 255, 255)

class McLarenCar:
    def __init__(self, x, y):
        # 1. Load the actual image file
        # Make sure 'mclaren.png' is in the same folder as your script!
        try:
            self.original_surface = pygame.image.load("mclaren.png").convert_alpha()
            # 2. Scale it to fit the simulation (Width, Height)
            self.original_surface = pygame.transform.scale(self.original_surface, (40, 80))
        except:
            # Fallback if image is missing: Create a realistic orange gradient block
            print("Image not found! Using a placeholder.")
            self.original_surface = pygame.Surface((40, 80), pygame.SRCALPHA)
            pygame.draw.rect(self.original_surface, (255, 135, 0), (0, 0, 40, 80), border_radius=8)
            pygame.draw.rect(self.original_surface, (50, 50, 50), (5, 15, 30, 20)) # Windshield

        self.surface = self.original_surface
        self.rect = self.surface.get_rect(center=(x, y))
        
        # Physics Variables (Adjusted for the new size)
        self.angle = 0
        self.speed = 0
        self.acceleration = 0.15
        self.friction = 0.04
        self.max_speed = 10
        self.steering = 3.5
        self.x, self.y = float(x), float(y)

    def drive(self):
        keys = pygame.key.get_pressed()

        # Acceleration / Braking
        if keys[pygame.K_UP]:
            self.speed += self.acceleration
        elif keys[pygame.K_DOWN]:
            self.speed -= self.acceleration
        else:
            # Apply friction when no key is pressed
            if self.speed > 0: self.speed -= self.friction
            elif self.speed < 0: self.speed += self.friction

        # Limit speed
        self.speed = max(-self.max_speed / 2, min(self.speed, self.max_speed))

        # Steering (Only steer if the car is moving)
        if abs(self.speed) > 0.1:
            direction = 1 if self.speed > 0 else -1
            if keys[pygame.K_LEFT]:
                self.angle += self.steering * direction
            if keys[pygame.K_RIGHT]:
                self.angle -= self.steering * direction

    def move(self):
        # Convert angle to radians for trigonometry
        radians = math.radians(self.angle)
        # Computer Graphics Math: Calculating new X and Y based on angle
        # We use -90 degrees offset because the car surface is drawn vertically
        self.x += self.speed * math.sin(radians)
        self.y -= self.speed * math.cos(radians)
        
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # Rotate the car based on its current angle
        rotated_car = pygame.transform.rotate(self.original_surface, self.angle)
        new_rect = rotated_car.get_rect(center=self.rect.center)
        screen.blit(rotated_car, new_rect.topleft)

# --- Main Game Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("McLaren F1 Simulation - Computer Graphics Project")
clock = pygame.time.Clock()

mclaren = McLarenCar(WIDTH // 2, HEIGHT // 2)

running = True
while running:
    screen.fill(ASPHALT_GREY) # Road Background

    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Logic / Physics
    mclaren.drive()
    mclaren.move()

    # 3. Drawing
    # Draw simple track lines
    pygame.draw.rect(screen, WHITE, (50, 50, WIDTH-100, HEIGHT-100), 5) 
    mclaren.draw(screen)

    # UI Info
    font = pygame.font.SysFont("Arial", 20)
    speed_text = font.render(f"Speed: {abs(int(mclaren.speed * 20))} km/h", True, WHITE)
    screen.blit(speed_text, (20, 20))

    pygame.display.flip()
    clock.tick(60) # 60 FPS

pygame.quit()