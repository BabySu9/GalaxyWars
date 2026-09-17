from ursina import *
from random import uniform, choice
import math


app = Ursina(title='Jedino') 

# =========================
# AUDIO
# =========================
beamshot_sound = Audio('beamshot.mp3', autoplay=False)
fader_sound = Audio('fader.wav', autoplay=False)
lightsaber_sound = Audio('lightsaber.mp3', autoplay=False)
impact_sound = Audio('impact.mp3', autoplay=False)
jump_sound = Audio('jump.mp3', autoplay=False)

# Música de fondo en loop
background_music = Audio(
    'song.mp3',
    loop=True,
    autoplay=True,
    volume=0.6
)

window.title = "Rex Jedi: Laser Deflection, Zoom & Jump Mode"

# =========================
# ESCENA Y ENTORNO
# =========================
Sky(texture='fondo.jpg')

textures = ['metal.jpg', 'metal1.jpeg']

tile_size = 6
map_size = 120

for x in range(-map_size//2, map_size//2, tile_size):
    for z in range(-map_size//2, map_size//2, tile_size):

        Entity(
            model='plane',
            texture=choice(textures),
            texture_scale=(1, 1),
            position=(x, 0, z),
            scale=(tile_size, 1, tile_size),
            #rotation_x=90,
            collider='box'
        )

planeta1 = Entity(
    model='planet1.glb',
    position=(0, 25, 40),
    scale=60,
    color=color.white
)

ship1 = Entity(
    model='ship1.glb',
    position=(0, 25, 0),
    scale=10,
    rotation=(0, 90, 0)
)
# =========================
# TORRES EN LAS ESQUINAS
# =========================

rect1 = Entity(
    model='rect.glb',
    position=(-55, 1, -55),
    scale=5,
    collider='mesh'
)

rect2 = Entity(
    model='rect.glb',
    position=(55, 1, -55),
    scale=5,
    collider='mesh'
)

rect3 = Entity(
    model='rect.glb',
    position=(-55, 1, 55),
    scale=5,
    collider='mesh'
)

rect4 = Entity(
    model='rect.glb',
    position=(55, 1, 55),
    scale=5,
    collider='mesh'
)

# 🏯 GENERACIÓN DE BASE MILITAR SITH (NUEVO)
# Creamos límites y obstáculos usando tus archivos .glb con colisionadores físicos
base_objects = []

# 1. Colocar Pilares de Suministros (ccc.glb) en la periferia como muros y algunos al centro
for i in range(16):
    # Alternamos entre posiciones perimetrales (bordes del mapa) y algunas centrales distribuidas
    if i < 12:
        # Distribución en los bordes del mapa de 120x120 (aproximadamente en coordenadas -55 y 55)
        angle = (i / 12) * math.pi * 2
        x_pos = math.cos(angle) * 55
        z_pos = math.sin(angle) * 55
    else:
        # Unos cuantos pilares de suministros en zonas internas aleatorias
        x_pos = uniform(-35, 35)
        z_pos = uniform(-35, 35)
        # Evitar que aparezcan justo en el centro donde spawnea el jugador
        if abs(x_pos) < 8 and abs(z_pos) < 8: 
            x_pos += 15

    pilar_sith = Entity(
        model='ccc.glb',
        position=(x_pos, 1, z_pos),
        scale=2.5,                      # Escalado para que parezca una estructura imponente
        rotation_y=uniform(0, 360),     # Rotación aleatoria orgánica
        collider='mesh'                 # <-- Bloquea el paso físico de garras, pies y enemigos
    )
    base_objects.append(pilar_sith)

# 2. Colocar Cajas de Munición (box.glb) esparcidas de forma táctica en el escenario
for _ in range(20):
    bx = uniform(-48, 48)
    bz = uniform(-48, 48)
    
    # Asegurar que no obstruyan el punto de inicio del jugador (0, 1, 0)
    if abs(bx) < 6 and abs(bz) < 6:
        bx += 12

    caja_sith = Entity(
        model='box.glb',
        position=(bx, 1, bz),
        scale=1.8,                      # Proporción adecuada para coberturas
        rotation_y=choice([0, 90, 180, 270]), # Rotaciones angulares de almacenamiento militar
        collider='mesh'                 # <-- Funciona como cobertura contra láseres o bloqueo
    )
    base_objects.append(caja_sith)


# =========================
# JUGADOR (PLAYER)
# =========================
player = Entity(
    position=(0, 1, 0),
    collider='box'
)

player_visual = Entity(parent=player)

dino = Entity(
    parent=player_visual,
    model='dinosaurio_jedi2.glb',
    scale=4.2,
    rotation_y=180
)
# Variables de movimiento y juego
speed = 8
score = 0
difficulty = 1
max_hp = 10000
hp = 10000
game_over = False

# 🦘 VARIABLES DE TRIPLE SALTO 
y_velocity = 0          
gravity = -26           
jump_force = 15        
jump_count = 0          

# =========================
# 🟦 SABLES DE LUZ JEDI
# =========================
saber_right = Entity(
    parent=player_visual,
    model='espada.glb',
    scale=0.22,
    # X más abierto a la derecha, Y a la altura del pecho/brazo, Z hacia adelante
    position=(0.32, 0.08, 1.7),   
    # Rotación alineada con el agarre natural de la muñeca
    rotation=(15, 10, -25)          
)

blade_right = Entity(
    parent=saber_right,
    model='cube',
    color=color.azure,
    scale=(0.16, 0.06, 4.5),
    position=(0, 0, 2),
    unlit=True
)

saber_left = Entity(
    parent=player_visual,
    model='espada.glb',
    scale=0.22,
    # X más abierto a la izquierda, Y ligeramente más bajo (postura asimétrica), Z hacia adelante
    position=(-0.48, 0.06, 1.77),  
    # Rotación inversa para la mano izquierda
    rotation=(15, -10, 25)         
)

blade_left = Entity(
    parent=saber_left,
    model='cube',
    color=color.azure,
    scale=(0.16, 0.06, 4.5),
    position=(0, 0, 2),
    unlit=True
)

# Duplicados de sables para Primera Persona (Se mantienen igual, están anclados a la cámara)
fp_saber_right = Entity(
    parent=camera,
    model='espada.glb',
    scale=0.18,
    position=(0.65, -0.65, 1.8),
    rotation=(25, -15, -20),
    enabled=False
)
fp_blade_right = Entity(parent=fp_saber_right, model='cube', color=color.azure, scale=(0.16, 0.06, 4.5), position=(0, 0, 2), unlit=True)

fp_saber_left = Entity(
    parent=camera,
    model='espada.glb',
    scale=0.18,
    position=(-0.65, -0.65, 1.8),
    rotation=(25, 15, 20),
    enabled=False
)
fp_blade_left = Entity(parent=fp_saber_left, model='cube', color=color.azure, scale=(0.16, 0.06, 4.5), position=(0, 0, 2), unlit=True)

PointLight(parent=player, color=color.azure)

# =========================
# 🎥 CÁMARA ORBITAL DINÁMICA
# =========================
camera_pivot = Entity(parent=player, position=(0, 1.5, 0), rotation=(22, 0, 0))

camera.parent = camera_pivot
camera.position = (0, 0, -18.5) 
camera.rotation = (0, 0, 0)

camera_sensitivity = 180
zoom_speed = 1.5
min_zoom = -1.5               
max_zoom = -35.0                 

# =========================
# ENEMIGOS Y LÁSERES
# =========================
enemies = []
lasers = []  
enemy_models = ['enemigo1.glb', 'enemigo2.glb']

def spawn_enemy():
    enemy = Entity(
        position=(uniform(-30, 30), 1, uniform(-30, 30)),
        collider='box'
    )
    
    enemy_visual = Entity(
        parent=enemy,
        model=choice(enemy_models),
        scale=1.56,
        rotation_y=180  
    )
    
    enemy.shoot_cooldown = uniform(4, 8)
    enemies.append(enemy)

for _ in range(8):
    spawn_enemy()

# =========================
# INTERFAZ DE USUARIO (UI)
# =========================
hp_bar_bg = Entity(parent=camera.ui, model='quad', color=color.dark_gray, scale=(0.4, 0.03), position=(-0.6, 0.45))
hp_bar = Entity(parent=camera.ui, model='quad', color=color.lime, scale=(0.4, 0.03), position=(-0.6, 0.45), origin=(-0.5, 0))
score_text = Text(text="", position=(-0.75, 0.40), scale=1.5)
game_over_text = Text(text="", origin=(0, 0), scale=3, color=color.red)

# =========================
# BUCLE PRINCIPAL (UPDATE)
# =========================
def update():
    
    global hp, score, difficulty, game_over, y_velocity, jump_count

    planeta1.rotation_y += 3 * time.dt


    if game_over:
        return

    # Movimiento horizontal del Jugador
    move = Vec3((held_keys['d'] - held_keys['a']), 0, (held_keys['w'] - held_keys['s']))
    player.position += (player.forward * move.z + player.right * move.x) * speed * time.dt

    # Restricción perimetral invisible adicional para el mapa (por si acaso saltan muy alto)
    player.x = clamp(player.x, -58, 58)
    player.z = clamp(player.z, -58, 58)

    # 🦘 FISICAS DE GRAVEDAD JUGADOR
    if player.y > 1 or y_velocity > 0:
        y_velocity += gravity * time.dt       
        player.y += y_velocity * time.dt      

    if player.y <= 1:
        player.y = 1
        y_velocity = 0
        jump_count = 0  

    # Rotación e inclinación de cámara según la perspectiva
    if camera.z >= -1.5 and held_keys['right mouse']:
        player.rotation_y += mouse.velocity[0] * camera_sensitivity
        camera_pivot.rotation_y = 0  
        camera_pivot.rotation_x -= mouse.velocity[1] * camera_sensitivity
        camera_pivot.rotation_x = clamp(camera_pivot.rotation_x, -40, 60)
    else:
        if held_keys['q']: player.rotation_y += 120 * time.dt
        if held_keys['e']: player.rotation_y -= 120 * time.dt
        if held_keys['right mouse']:
            camera_pivot.rotation_y += mouse.velocity[0] * camera_sensitivity
            camera_pivot.rotation_x -= mouse.velocity[1] * camera_sensitivity
            camera_pivot.rotation_x = clamp(camera_pivot.rotation_x, -5, 80)

    # Lógica de Inteligencia Artificial de los Enemigos
    for enemy in enemies:
        enemy.y = 1 
        direction = player.position - enemy.position
        direction.y = 0  
        dist = direction.length()

        if dist > 6:  
            enemy.position += direction.normalized() * (1.5 + difficulty * 0.2) * time.dt
        
        enemy.look_at(Vec3(player.x, enemy.y, player.z))

        enemy.shoot_cooldown -= time.dt
        if enemy.shoot_cooldown <= 0:
            enemy.shoot_cooldown = max(2.0, uniform(3.5, 7.0) - (difficulty * 0.1))
            
            beamshot_sound.play()

            laser = Entity(
                model='cube',
                color=color.red,
                scale=(0.15, 0.15, 3.5),
                position=enemy.position + Vec3(0, 1.5, 0),
                unlit=True
            )
            laser.look_at(player.position + Vec3(0, 1, 0))
            laser.direction = (player.position + Vec3(0, 1, 0) - laser.position).normalized()
            laser.deflected = False 
            lasers.append(laser)

    # Control e Impacto de Proyectiles Láser
    for laser in lasers[:]:
        laser.position += laser.direction * 25 * time.dt 
        
        if not laser.deflected:
            if distance(laser.position, player.position + Vec3(0, 1, 0)) < 1.8:
                hp -= 10  
                destroy(laser)
                lasers.remove(laser)
                continue
        else:
            for enemy in enemies[:]:
                if distance(laser.position, enemy.position + Vec3(0, 1, 0)) < 1.8:
                    destroy(enemy)
                    enemies.remove(enemy)
                    destroy(laser)
                    lasers.remove(laser)
                    score += 15  
                    spawn_enemy()
                    break
            if laser not in lasers:
                continue 

        if distance(laser.position, player.position) > 80:
            destroy(laser)
            lasers.remove(laser)

    if hp <= 0:
        hp = 0
        game_over = True
        game_over_text.text = "💀 GAME OVER 💀"

    hp_bar.scale_x = 0.4 * (hp / max_hp)
    hp_bar.color = color.lime if hp > 60 else (color.yellow if hp > 30 else color.red)
    score_text.text = f"⭐ Score: {score} | 💀 Dificultad: {difficulty}"

# =========================
# ENTRADAS DE EVENTOS (INPUT)
# =========================
def input(key):
    global score, difficulty, y_velocity, jump_count

    if game_over:
        return

    if key == 'space':
        jump_sound.play()
        if jump_count < 3:  
            y_velocity = jump_force
            jump_count += 1

    if key == 'right mouse down':
        mouse.locked = True  
    if key == 'right mouse up':
        mouse.locked = False 

    # Gestión de Scroll 
    if key == 'scroll up':
        camera.z = min(camera.z + zoom_speed, min_zoom)
        if camera.z == 0:
            player_visual.enabled = False
            fp_saber_right.enabled = True
            fp_saber_left.enabled = True
            camera_pivot.rotation_x = 0
            
    if key == 'scroll down':
        if camera.z >= -1.5:
            player_visual.enabled = True
            fp_saber_right.enabled = False
            fp_saber_left.enabled = False
            camera_pivot.rotation_x = 22
        camera.z = max(camera.z - zoom_speed, max_zoom)

    # Ataques y parry 
    if key == 'left mouse down':
        lightsaber_sound.play()
        saber_right.animate_rotation((0, 0, -100), duration=0.08)
        saber_left.animate_rotation((0, 0, 100), duration=0.08)
        invoke(saber_right.animate_rotation, (-60, 45, 0), delay=0.08)
        invoke(saber_left.animate_rotation, (-60, -45, 0), delay=0.08)

        fp_saber_right.animate_rotation((40, -20, -30), duration=0.08)
        fp_saber_left.animate_rotation((40, 20, 30), duration=0.08)
        invoke(fp_saber_right.animate_rotation, (20, -10, -10), delay=0.08)
        invoke(fp_saber_left.animate_rotation, (20, 10, 10), delay=0.08)

        for laser in lasers:
            if distance(player.position, laser.position) < 5.0: 
                if not laser.deflected:
                    laser.deflected = True
                    laser.color = color.azure 
                    impact_sound.play() 
                    impact_sound.pitch = uniform(0.9, 1.1)

                    if enemies:
                        target_enemy = min(enemies, key=lambda e: distance(laser.position, e.position))
                        laser.direction = (target_enemy.position - laser.position).normalized()
                    else:
                        laser.direction = -laser.direction
                    
                    laser.look_at(laser.position + laser.direction)

        killed = 0
        for enemy in enemies[:]:
            if distance(player.position, enemy.position) < 5:
                destroy(enemy)
                enemies.remove(enemy)
                killed += 1

        score += killed * 10
        for _ in range(killed):
            spawn_enemy()

    if key == 'f':
        fader_sound.play()
        for enemy in enemies:
            if distance(player.position, enemy.position) < 12:
                direction = (enemy.position - player.position).normalized()
                enemy.animate_position(enemy.position + direction * 15, duration=0.35)
                score += 2

    difficulty = 1 + score // 50

app.run()