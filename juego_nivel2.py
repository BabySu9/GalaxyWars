from ursina import *
from random import uniform
import math

app = Ursina()

window.title = "Jedino Level 2"
window.borderless = False
window.fullscreen = False

# =====================================================
# FONDO
# =====================================================

background = Entity(
    model='quad',
    texture='backg.jpeg',
    scale=(250, 170),
    position=(0, 0, 300),
    double_sided=True,
    unlit=True
)

Sky(color=color.black)

for i in range(300):
    Entity(
        model='sphere',
        color=color.white,
        scale=0.08,
        position=(
            uniform(-500, 500),
            uniform(-500, 500),
            uniform(-500, 500)
        )
    )

# =====================================================
# VARIABLES
# =====================================================

score = 0
hp = 100
game_over = False

forward_speed = 40
move_speed = 20

player_lasers = []
enemy_lasers = []

enemies = []
asteroids = []

MAX_ENEMIES = 6
MAX_ASTEROIDS = 7

# =====================================================
# JUGADOR
# =====================================================

player = Entity(
    model='ship_jedi',
    scale=0.009,
    position=(0, -8, 0)
)

player.rotation_y = 180

# =====================================================
# CAMARA
# =====================================================

camera.parent = scene
camera.position = (0, 6, -18)
camera.rotation_x = 10

# =====================================================
# UI
# =====================================================

score_text = Text(
    text="Score: 0",
    position=(-0.85, 0.45),
    scale=2
)

hp_text = Text(
    text="HP: 100",
    position=(-0.85, 0.40),
    scale=2
)

game_over_text = Text(
    text="",
    origin=(0, 0),
    scale=4,
    color=color.red
)

# =====================================================
# DISPARO JUGADOR
# =====================================================

def fire_laser():

    laser = Entity(
        model='cube',
        color=color.cyan,
        scale=(0.15, 0.15, 2),
        position=player.position + Vec3(0, 0, 2),
        unlit=True
    )

    player_lasers.append(laser)

# =====================================================
# DISPARO ENEMIGO
# =====================================================

def enemy_fire(enemy):

    laser = Entity(
        model='cube',
        color=color.red,
        scale=(0.2, 0.2, 4),
        position=enemy.position + Vec3(0, 0, -2),
        unlit=True
    )

    enemy_lasers.append(laser)

# =====================================================
# ENEMIGOS
# =====================================================

def spawn_enemy():

    enemy = Entity(
        model='ship_sith2.glb',
        scale=0.8,
        position=(
            player.x + uniform(-25, 25),
            player.y + uniform(-10, 10),
            player.z + uniform(150, 300)
        )
    )

    enemy.rotation_y = 180
    enemy.life = 1
    enemy.fire_timer = uniform(1, 3)

    enemies.append(enemy)

def reset_enemy(enemy):

    enemy.position = (
        player.x + uniform(-25, 25),
        player.y + uniform(-10, 10),
        player.z + uniform(180, 320)
    )

    enemy.fire_timer = uniform(1, 3)

# =====================================================
# ASTEROIDES
# =====================================================

def spawn_asteroid():

    asteroid = Entity(
        model='meteorito.glb',
        scale=uniform(0.25, 0.9),
        position=(
            player.x + uniform(-30, 30),
            player.y + uniform(-15, 15),
            player.z + uniform(180, 350)
        )
    )

    asteroids.append(asteroid)

def reset_asteroid(asteroid):

    asteroid.position = (
        player.x + uniform(-30, 30),
        player.y + uniform(-15, 15),
        player.z + uniform(180, 350)
    )

# =====================================================
# POBLACION INICIAL
# =====================================================

for i in range(MAX_ENEMIES):
    spawn_enemy()

for i in range(MAX_ASTEROIDS):
    spawn_asteroid()

# =====================================================
# UPDATE
# =====================================================

def update():

    global score
    global hp
    global game_over

    if game_over:
        return

    # -----------------------------------------
    # MOVIMIENTO JUGADOR
    # -----------------------------------------

    player.z += forward_speed * time.dt

    player.x += (held_keys['d'] - held_keys['a']) * move_speed * time.dt
    player.y += (held_keys['w'] - held_keys['s']) * move_speed * time.dt

    player.x = clamp(player.x, -25, 25)
    player.y = clamp(player.y, -12, 12)

    player.rotation_z = lerp(
        player.rotation_z,
        -(held_keys['d'] - held_keys['a']) * 25,
        5 * time.dt
    )

    # -----------------------------------------
    # CAMARA
    # -----------------------------------------

    camera.position = lerp(
        camera.position,
        player.position + Vec3(0, 6, -18),
        4 * time.dt
    )

    camera.look_at(player.position + Vec3(0, 0, 30))

    # -----------------------------------------
    # FONDO
    # -----------------------------------------

    background.position = player.position + Vec3(0, 0, 200)

    # -----------------------------------------
    # LASERS DEL JUGADOR
    # -----------------------------------------

    for laser in player_lasers[:]:

        laser.z += 120 * time.dt
        laser.scale_z *= 0.998

        hit = False

        for enemy in enemies:

            if distance(laser.position, enemy.position) < 1.5:

                score += 10

                reset_enemy(enemy)

                destroy(laser)
                player_lasers.remove(laser)

                hit = True
                break

        if hit:
            continue

        if laser.z > player.z + 300:

            destroy(laser)

            if laser in player_lasers:
                player_lasers.remove(laser)

    # -----------------------------------------
    # ENEMIGOS
    # -----------------------------------------

    for enemy in enemies:

        enemy.z -= 55 * time.dt

        enemy.fire_timer -= time.dt

        if enemy.fire_timer <= 0:

            enemy_fire(enemy)

            enemy.fire_timer = uniform(1.0, 2.5)

        if distance(enemy.position, player.position) < 2:

            hp -= 20

            reset_enemy(enemy)

        if enemy.z < player.z - 20:

            reset_enemy(enemy)

    # -----------------------------------------
    # LASERS ENEMIGOS
    # -----------------------------------------

    for laser in enemy_lasers[:]:

        laser.z -= 100 * time.dt

        if distance(laser.position, player.position) < 2:

            hp -= 10

            destroy(laser)

            if laser in enemy_lasers:
                enemy_lasers.remove(laser)

            continue

        if laser.z < player.z - 50:

            destroy(laser)

            if laser in enemy_lasers:
                enemy_lasers.remove(laser)

    # -----------------------------------------
    # ASTEROIDES
    # -----------------------------------------

    for asteroid in asteroids:

        asteroid.z -= 35 * time.dt

        asteroid.rotation_x += 80 * time.dt
        asteroid.rotation_y += 120 * time.dt

        if distance(asteroid.position, player.position) < 3:

            hp -= 10

            reset_asteroid(asteroid)

        if asteroid.z < player.z - 30:

            reset_asteroid(asteroid)

    # -----------------------------------------
    # MANTENER CANTIDAD DE OBJETOS
    # -----------------------------------------

    while len(enemies) < MAX_ENEMIES:
        spawn_enemy()

    while len(asteroids) < MAX_ASTEROIDS:
        spawn_asteroid()

    # -----------------------------------------
    # GAME OVER
    # -----------------------------------------

    if hp <= 0:

        hp = 0
        game_over = True

        game_over_text.text = "GAME OVER"

    score_text.text = f"Score: {score}"
    hp_text.text = f"HP: {hp}"

# =====================================================
# INPUT
# =====================================================

def input(key):

    if game_over:
        return

    if key == 'space':
        fire_laser()

    if key == 'left mouse down':
        fire_laser()

app.run()