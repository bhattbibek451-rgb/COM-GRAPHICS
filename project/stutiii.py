import pygame, math, sys, random, os

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Haunted House Ultimate Edition")
clock = pygame.time.Clock()

# --- Sounds ---
pygame.mixer.init()
ghost_sound = None
jump_scare_sound = None

if os.path.exists("ghost.mp3"):
    try:
        ghost_sound = pygame.mixer.Sound("ghost.mp3")
        ghost_sound.set_volume(0.3)
    except:
        pass

if os.path.exists("jumpscare.mp3"):
    try:
        jump_scare_sound = pygame.mixer.Sound("jumpscare.mp3")
        jump_scare_sound.set_volume(0.7)
    except:
        pass

# --- Map & floors ---
FLOORS = [
    [   # First floor
        [1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,1],
        [1,0,1,0,1,0,1,0,1],
        [1,0,1,0,1,0,1,0,1],
        [1,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1]
    ],
    [   # Second floor
        [1,1,1,1,1,1,1,1,1],
        [1,0,1,0,0,0,1,0,1],
        [1,0,1,0,1,0,1,0,1],
        [1,0,0,0,1,0,0,0,1],
        [1,1,1,0,0,0,1,1,1],
        [1,1,1,1,1,1,1,1,1]
    ]
]

# --- Ladder positions: (x_tile, y_tile, floor_from, floor_to) ---
LADDERS = [
    (1,1,0,1),(7,4,1,0),(3,1,0,1),(5,4,1,0)
]

MAP_WIDTH = len(FLOORS[0][0])
MAP_HEIGHT = len(FLOORS[0])
TILE = 64
NUM_FLOORS = len(FLOORS)

# --- Player ---
player_x = TILE*1.5
player_y = TILE*1.5
player_angle = 0
player_speed = 2
player_floor = 0

# --- Colors ---
BLACKISH_GREY = (40,40,40)
CEILING_COLOR = (20,20,20)
WALL_COLOR = BLACKISH_GREY
FLOOR_COLOR = BLACKISH_GREY
MAP_BG_COLOR = (30,30,30)
MAP_PLAYER_COLOR = (255,0,0)
MAP_GHOST_COLOR = (200,200,255)
LADDER_COLOR = (200,150,50)

# --- Raycasting ---
FOV = math.pi/3
NUM_RAYS = 120
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
DIST_PROJ_PLANE = (WIDTH/2)/math.tan(FOV/2)
SCALE = WIDTH//NUM_RAYS

# --- Load ghost wall textures & paintings ---
GHOST_WALL_TEXTURES = []
if os.path.exists("ghost"):
    GHOST_WALL_TEXTURES = [pygame.image.load(os.path.join("ghost",f)).convert_alpha()
                           for f in sorted(os.listdir("ghost")) if f.endswith(".png")]
if not GHOST_WALL_TEXTURES:
    surf = pygame.Surface((TILE,TILE),pygame.SRCALPHA)
    pygame.draw.rect(surf,(200,200,255,100),(0,0,TILE,TILE))
    GHOST_WALL_TEXTURES = [surf]

GHOST_PAINTINGS = []
if os.path.exists("paintings"):
    GHOST_PAINTINGS = [pygame.image.load(os.path.join("paintings",f)).convert_alpha()
                       for f in sorted(os.listdir("paintings")) if f.endswith(".png")]
if not GHOST_PAINTINGS:
    surf = pygame.Surface((TILE,TILE),pygame.SRCALPHA)
    pygame.draw.rect(surf,(255,100,100,100),(0,0,TILE,TILE))
    GHOST_PAINTINGS = [surf]

DECORATIONS = {}
if os.path.exists("skull"):
    for f in os.listdir("skull"):
        if f.endswith(".png"):
            DECORATIONS[f.split(".")[0]] = pygame.image.load(os.path.join("skull",f)).convert_alpha()
if not DECORATIONS:
    # Create placeholder decorations
    for name in ["crack", "skeleton", "chair", "mirror"]:
        surf = pygame.Surface((TILE,TILE),pygame.SRCALPHA)
        pygame.draw.rect(surf,(100,100,100,150),(0,0,TILE,TILE))
        DECORATIONS[name] = surf

# --- Wall elements (ghosts, paintings, cracks, skeletons, chairs, mirrors) ---
WALL_ELEMENTS = [
    (2,1,"ghost",0),(4,2,"painting",0),(5,3,"ghost",1),
    (1,3,"crack","crack"),(3,2,"skeleton","skeleton"),(6,2,"chair","chair"),
    (7,1,"mirror","mirror")
]

# --- Ghost class ---
class Ghost:
    def __init__(self, x, y, floor, sprite_folder=None):
        self.x = x
        self.y = y
        self.floor = floor
        self.jump_triggered = False
        self.dir_x = random.choice([-1,1])
        self.dir_y = random.choice([-1,1])
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = []
        if sprite_folder and os.path.exists(sprite_folder):
            files = sorted(os.listdir(sprite_folder))
            for f in files:
                if f.endswith(".png"):
                    self.frames.append(pygame.image.load(os.path.join(sprite_folder,f)).convert_alpha())
        if not self.frames:
            surf = pygame.Surface((TILE,TILE),pygame.SRCALPHA)
            pygame.draw.circle(surf,(255,255,255,180),(TILE//2,TILE//2),TILE//2)
            self.frames.append(surf)
    def move(self):
        speed=0.5
        new_x = self.x + self.dir_x*speed
        new_y = self.y + self.dir_y*speed
        if FLOORS[self.floor][int(new_y//TILE)][int(new_x//TILE)]==0:
            self.x=new_x
            self.y=new_y
        else:
            self.dir_x*=-1
            self.dir_y*=-1
    def get_current_frame(self):
        self.frame_index+=self.animation_speed
        if self.frame_index>=len(self.frames):
            self.frame_index=0
        return self.frames[int(self.frame_index)]

# --- Create ghosts ---
ghosts = [
    Ghost(TILE*3.5,TILE*2.5,0,"ghost1"),
    Ghost(TILE*5.5,TILE*1.5,0,"ghost2"),
    Ghost(TILE*2.5,TILE*3.5,1,"ghost3"),
    Ghost(TILE*4.5,TILE*2.5,1,"ghost4")
]

# --- Raycasting ---
def ray_casting():
    start_angle = player_angle - FOV/2
    for ray in range(NUM_RAYS):
        angle = start_angle + ray*DELTA_ANGLE
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        for depth in range(MAX_DEPTH):
            x = player_x + depth*cos_a
            y = player_y + depth*sin_a
            i = int(x//TILE)
            j = int(y//TILE)
            if 0<=i<MAP_WIDTH and 0<=j<MAP_HEIGHT:
                if FLOORS[player_floor][j][i]==1:
                    color_intensity = 255/(1+depth*0.02)
                    color = (
                        max(WALL_COLOR[0],min(255,color_intensity)),
                        max(WALL_COLOR[1],min(255,color_intensity)),
                        max(WALL_COLOR[2],min(255,color_intensity))
                    )
                    proj_height = min(int(DIST_PROJ_PLANE*TILE/(depth+0.0001)),HEIGHT)
                    pygame.draw.rect(window,color,(ray*SCALE,HEIGHT/2 - proj_height/2,SCALE,proj_height))

                    # Draw wall decorations
                    for ex,ey,etype,idx in WALL_ELEMENTS:
                        if ex==i and ey==j:
                            if etype=="ghost":
                                img = GHOST_WALL_TEXTURES[idx]
                            elif etype=="painting":
                                img = GHOST_PAINTINGS[idx]
                            else: # crack, skeleton, chair, mirror
                                img = DECORATIONS.get(idx)
                            if img:
                                img_scaled = pygame.transform.scale(img,(SCALE,proj_height))
                                window.blit(img_scaled,(ray*SCALE,HEIGHT/2 - proj_height/2))
                    break

# --- Mini-map ---
def draw_map():
    map_scale=8
    map_surface = pygame.Surface((MAP_WIDTH*map_scale,MAP_HEIGHT*map_scale))
    map_surface.fill(MAP_BG_COLOR)
    floor_map=FLOORS[player_floor]
    for j,row in enumerate(floor_map):
        for i,val in enumerate(row):
            if val==1:
                pygame.draw.rect(map_surface,(100,100,100),(i*map_scale,j*map_scale,map_scale,map_scale))
    for lx,ly,f_from,f_to in LADDERS:
        if player_floor==f_from or player_floor==f_to:
            pygame.draw.rect(map_surface,LADDER_COLOR,(lx*map_scale,ly*map_scale,map_scale,map_scale))
    pygame.draw.circle(map_surface,MAP_PLAYER_COLOR,(int(player_x/TILE*map_scale),int(player_y/TILE*map_scale)),3)
    for g in ghosts:
        if g.floor==player_floor:
            pygame.draw.circle(map_surface,MAP_GHOST_COLOR,(int(g.x/TILE*map_scale),int(g.y/TILE*map_scale)),2)
    window.blit(map_surface,(5,5))

# --- Main loop ---
running=True
while running:
    window.fill(FLOOR_COLOR)
    pygame.draw.rect(window,CEILING_COLOR,(0,0,WIDTH,HEIGHT//2))
    pygame.draw.rect(window,FLOOR_COLOR,(0,HEIGHT//2,WIDTH,HEIGHT//2))

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player_angle-=0.03
    if keys[pygame.K_RIGHT]: player_angle+=0.03
    if keys[pygame.K_UP]:
        new_x = player_x + player_speed*math.cos(player_angle)
        new_y = player_y + player_speed*math.sin(player_angle)
        if FLOORS[player_floor][int(new_y//TILE)][int(new_x//TILE)]==0:
            player_x, player_y = new_x, new_y
        # ladder access
        for lx,ly,f_from,f_to in LADDERS:
            if int(player_x//TILE)==lx and int(player_y//TILE)==ly and player_floor==f_from:
                player_floor=f_to
                player_x = lx*TILE + TILE/2
                player_y = ly*TILE + TILE/2
    if keys[pygame.K_DOWN]:
        new_x = player_x - player_speed*math.cos(player_angle)
        new_y = player_y - player_speed*math.sin(player_angle)
        if FLOORS[player_floor][int(new_y//TILE)][int(new_x//TILE)]==0:
            player_x, player_y = new_x, new_y
        for lx,ly,f_from,f_to in LADDERS:
            if int(player_x//TILE)==lx and int(player_y//TILE)==ly and player_floor==f_from:
                player_floor=f_to
                player_x = lx*TILE + TILE/2
                player_y = ly*TILE + TILE/2

    ray_casting()

    for g in ghosts:
        g.move()
        if g.floor != player_floor: continue
        dx = g.x - player_x
        dy = g.y - player_y
        distance = math.hypot(dx,dy)
        theta = math.atan2(dy,dx)
        gamma = theta - player_angle
        if -FOV/2 < gamma < FOV/2:
            proj_height = min(int(DIST_PROJ_PLANE*TILE/(distance+0.0001)),HEIGHT)
            sprite_x = int((WIDTH/2)*(1+math.tan(gamma)/math.tan(FOV/2)))-proj_height//2
            frame = g.get_current_frame()
            window.blit(pygame.transform.scale(frame,(proj_height,proj_height)),(sprite_x,HEIGHT//2 - proj_height//2))
            if ghost_sound and distance<120 and not pygame.mixer.get_busy(): ghost_sound.play()
            if jump_scare_sound and distance<50 and not g.jump_triggered: jump_scare_sound.play(); g.jump_triggered=True
        else: g.jump_triggered=False

    draw_map()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
