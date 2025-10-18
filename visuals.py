import pygame
import numpy as np
import time
import colorsys

def spiral_spectrum(context):
    screen, bands, WIDTH, HEIGHT = context
    time_val = time.time()
    center = (WIDTH // 2, HEIGHT // 2)
    points = 120

    for i in range(points):
        angle = i * 0.25 + time_val * 0.8
        energy = bands['bass'] * 0.5 + bands['mid'] * 0.3 + bands['treble'] * 0.2
        radius = 50 + energy * 300 * (i / points)
        x = int(center[0] + np.cos(angle) * radius)
        y = int(center[1] + np.sin(angle) * radius)
        hue = (angle * 30 + time_val * 100) % 360
        color = pygame.Color(0)
        color.hsva = (hue, 100, 100, 100)
        size = max(2, int(4 + bands['treble'] * 8))
        pygame.draw.circle(screen, color, (x, y), size)


def heart_pulse(context):
    screen, bands, WIDTH, HEIGHT = context
    time_val = time.time()
    points = []
    amplitude = 150
    for x in range(WIDTH):
        y_offset = (
            np.sin(x * 0.015 + time_val * 2) * bands['bass'] +
            np.sin(x * 0.03  + time_val * 3) * bands['mid'] +
            np.sin(x * 0.06  + time_val * 5) * bands['treble']
        )
        y = int(HEIGHT // 2 - y_offset * amplitude)
        points.append((x, y))
    pygame.draw.lines(screen, (255, 80, 100), False, points, 3)
    for glow in range(1, 4):
        faded_color = (255, 80, 100 - glow * 20)
        pygame.draw.lines(screen, faded_color, False, [(x, y + glow*2) for x, y in points], 2)


def mountain_ridge(context):
    screen, bands, WIDTH, HEIGHT = context
    time_val = time.time()
    margin = int(WIDTH * 0.1)
    draw_width = int(WIDTH * 0.8)
    vals = [bands['bass'], bands['mid'], bands['treble'], bands['mid'], bands['bass']]
    anchors_x = np.linspace(0, draw_width, len(vals))
    interp = np.interp(np.arange(draw_width), anchors_x, vals)
    ridge_points = []
    for i, val in enumerate(interp):
        wobble = np.sin(time_val * 2 + i * 0.01) * 10
        y = int(HEIGHT / 2 - val * 300 + wobble)
        ridge_points.append((margin + i, y))
    pygame.draw.lines(screen, (0, 255, 255), False, ridge_points, 6)
    
# Scatter glowing dots based on frequency energy-------------------------------------------------------------------
def scatter_glow(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH // 2, HEIGHT // 2)
    treb = bands.get('treble', 0.0)

    # helper: convert HSV to pygame color
    def hsl_color(hue, brightness=1):
        r, g, b = colorsys.hsv_to_rgb(hue / 360, 1, brightness)
        return (int(r * 255), int(g * 255), int(b * 255))

    for i in range(30):
        # random position in a circle around the center
        angle = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(50, 300)
        x = int(center[0] + dist * np.cos(angle))
        y = int(center[1] + dist * np.sin(angle))

        # brightness + color based on treble
        brightness = np.random.uniform(0.4, 1.0)
        color = hsl_color(np.random.uniform(0, 360), brightness)

        # size reacts to treble
        size = int(3 + treb * 15)
        pygame.draw.circle(screen, color, (x, y), size)
        
#radial bar spectrum-------------------------------------------------------------------
def radial_bars(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH//2, HEIGHT//2)
    angles = np.linspace(0, 2*np.pi, 60)
    max_val = max(bands.values()) or 1
    for i, angle in enumerate(angles):
        freq_val = np.interp(i, [0,len(angles)-1], [bands['bass'], bands['treble']])
        length = int(50 + (freq_val/max_val)*250)
        x = int(center[0] + np.cos(angle)*length)
        y = int(center[1] + np.sin(angle)*length)
        color = pygame.Color(0)
        color.hsva = ((angle*180/np.pi)%360, 100, 100, 100)
        pygame.draw.line(screen, color, center, (x,y), 3)
        
        
#circular particle vortex-------------------------------------------------------------------
def circular_particle_vortex(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH//2, HEIGHT//2)
    for i in range(50):
        angle = np.random.uniform(0,2*np.pi)
        radius = np.random.uniform(50, 150) + bands['bass']*50
        x = int(center[0] + np.cos(angle+time.time())*radius)
        y = int(center[1] + np.sin(angle+time.time())*radius)
        color = pygame.Color(0)
        color.hsva = ((angle*180/np.pi)%360, 100, 100, 100)
        pygame.draw.circle(screen, color, (x,y), 4)
        
#equalizer mountain ridges-------------------------------------------------------------------
def equalizer_mountain_ridges(context):
    screen, bands, WIDTH, HEIGHT = context
    x_vals = np.linspace(0, WIDTH, 50)
    center_y = HEIGHT // 2
    max_val = max(bands.values()) or 1
    for i, x in enumerate(x_vals):
        # Use bands cycling + time for animation
        val = list(bands.values())[i % 3]
        y = int(center_y - val/max_val*150 * np.sin(time.time()*2 + i))
        pygame.draw.line(screen, (50, 200, 50, 150), (x, center_y), (x, y), 3)
        
#Radial Wave Ripples - invalid hvsva-------------------------------------------------------------------
def radial_wave_ripples(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH//2, HEIGHT//2)
    for i, (name, val) in enumerate(bands.items()):
        radius = int(50 + val*200)
        h = int((i*120 + time.time()*50) % 360)
        s = 255
        v = 255
        a = 150
        color = pygame.Color(0,0,0,0)
        color.hsva = (h, 100, 100, 60)  # H, S, V, A in percent (pygame uses 0-100 for hsva)
        pygame.draw.circle(screen, color, center, radius, 4)
        
#Polygon Morph-------------------------------------------------------------------
def polygon_morph(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH//2, HEIGHT//2)
    num_verts = 5
    angle_step = 2*np.pi/num_verts
    max_val = max(bands.values()) or 1
    points = []
    for i in range(num_verts):
        val = list(bands.values())[i%3]
        radius = 100 + val/max_val*150
        angle = angle_step*i + time.time()
        x = int(center[0] + np.cos(angle)*radius)
        y = int(center[1] + np.sin(angle)*radius)
        points.append((x,y))
    pygame.draw.polygon(screen, (255,150,50), points, 4)
    
# Frequency Landscape / 3D Mesh (2D simplified)-------------------------------------------------------------------
def frequency_landscape(context):
    screen, bands, WIDTH, HEIGHT = context
    freq_vals = np.linspace(bands['bass'], bands['treble'], WIDTH)
    for x, val in enumerate(freq_vals):
        y = int(HEIGHT - val*200)
        pygame.draw.line(screen, (100,255,255), (x, HEIGHT), (x, y), 2)
        
#frequency 3d----------------------------------------------------------------------
def frequency_3d(context):
    screen, bands, WIDTH, HEIGHT = context
    vals = [bands['bass'], bands['mid'], bands['treble']]
    xs = [0, WIDTH//2, WIDTH]  # 3 anchor points: left, center, right
    freq_interp = np.interp(np.arange(WIDTH), xs, vals)
    for x, val in enumerate(freq_interp):
        y = int(HEIGHT - val * 300)  # scale height
        color = pygame.Color(0, 255, 255, 80)  # semi-transparent cyan
        pygame.draw.line(screen, color, (x, HEIGHT), (x, y), 1)
        
        
#5 wing flapping-------------------------------------------------------------------
def five_wing_flapping(context):
    screen, bands, WIDTH, HEIGHT = context
    # === CONFIG ===
    margin = int(WIDTH * 0.1)             # leave 10% space on each side
    draw_width = int(WIDTH * 0.8)         # total width of the ridge
    height_scale = 200                    # how tall the mountain is


    # Define 5 anchor points: Bass - Mid - Treble - Mid - Bass
    vals = [
        bands['bass'],
        bands['mid'],
        bands['treble'],
        bands['mid'],
        bands['bass']
    ]

    # X positions for those anchors
    anchors_x = np.linspace(0, draw_width, len(vals))

    # Interpolate smoothly between them
    freq_interp = np.interp(np.arange(draw_width), anchors_x, vals)

    # Build ridge line points
    ridge_points = []
    for i, val in enumerate(freq_interp):
        x = margin + i
        # optional: add a gentle "breathing" wobble
        wobble = np.sin(time.time() * 2 + i * 0.01) * 10
        y = int(HEIGHT / 2 - val * height_scale + wobble)
        ridge_points.append((x, y))

    # Draw the ridge
    pygame.draw.lines(screen, (0, 255, 255), False, ridge_points, 6)
    
#Dual Ridge “Sound Mountain” (layered terrain)-------------------------------------------------------------------
def dual_ridge_sound_mountain(context):
    screen, bands, WIDTH, HEIGHT = context
    for layer in range(3):
        scale = 200 + layer * 50
        offset = layer * 20
        color = (50, 255 - layer*60, 255)
        ridge_points = []
        vals = [bands['bass'], bands['mid'], bands['treble'], bands['mid'], bands['bass']]
        anchors_x = np.linspace(0, WIDTH*0.8, len(vals))
        interp = np.interp(np.arange(int(WIDTH*0.8)), anchors_x, vals)
        for i, val in enumerate(interp):
            wobble = np.sin(time.time()*2 + i*0.01 + layer)*10
            y = int(HEIGHT/2 - val * scale + wobble + offset)
            ridge_points.append((int(WIDTH*0.1 + i), y))
        pygame.draw.lines(screen, color, False, ridge_points, 4)
        
#mirrored eq - good-------------------------------------------------------------------
def mirrored_eq(context):
    screen, bands, WIDTH, HEIGHT = context
    bar_width = 20
    for i, (name, val) in enumerate(bands.items()):
        height = int(val * 300)
        x_left = WIDTH//2 - (i+1)*bar_width*2
        x_right = WIDTH//2 + i*bar_width*2
        pygame.draw.rect(screen, (0, 200, 255), (x_left, HEIGHT//2 - height, bar_width, height*2))
        pygame.draw.rect(screen, (0, 200, 255), (x_right, HEIGHT//2 - height, bar_width, height*2))
        
#audio heart pulse-------------------------------------------------------------------
def audio_heart_pulse(context):
    screen, bands, WIDTH, HEIGHT = context
    points = []
    for x in range(WIDTH):
        band_val = bands['bass'] * np.sin(x * 0.02) + bands['mid'] * np.sin(x * 0.05) + bands['treble'] * np.sin(x * 0.1)
        y = int(HEIGHT/2 - band_val * 150)
        points.append((x, y))
    pygame.draw.lines(screen, (255, 50, 50), False, points, 3)
    
#enhanced audio heart pulse-------------------------------------------------------------------
def enhanced_audio_heart_pulse(context):
    screen, bands, WIDTH, HEIGHT = context
    points = []
    amplitude = 150
    speed = 0.05

    for x in range(WIDTH):
        # Combine multiple frequencies
        y_offset = (
            np.sin(x * 0.015 + time.time() * 2) * bands['bass'] +
            np.sin(x * 0.03  + time.time() * 3) * bands['mid'] +
            np.sin(x * 0.06  + time.time() * 5) * bands['treble']
        )

        y = int(HEIGHT // 2 - y_offset * amplitude)
        points.append((x, y))

    # Main pulse line
    pygame.draw.lines(screen, (255, 80, 100), False, points, 3)

    # Optional glow effect (draw blurred layers)
    for glow in range(1, 4):
        faded_color = (255, 80, 100 - glow * 20)
        pygame.draw.lines(screen, faded_color, False, [(x, y + glow*2) for x, y in points], 2)
        
#spyral spectrun-------------------------------------------------------------------
def spyral_spectrum(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH//2, HEIGHT//2)
    for i in range(120):
        angle = i * 0.2 + time.time()
        radius = 50 + (bands['bass']*100 + bands['mid']*150 + bands['treble']*200) * (i/120)
        x = int(center[0] + np.cos(angle) * radius)
        y = int(center[1] + np.sin(angle) * radius)
        pygame.draw.circle(screen, (int(255 - i*2), 100, 255), (x, y), 4)
        
#enhanced spyral spectrum-------------------------------------------------------------------
def enhanced_spyral_spectrum(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH // 2, HEIGHT // 2)
    points = 120  # number of spiral points

    for i in range(points):
        # Spiral angle + slow rotation
        angle = i * 0.25 + time.time() * 0.8

        # Spiral radius grows with index and music energy
        energy = bands['bass'] * 0.5 + bands['mid'] * 0.3 + bands['treble'] * 0.2
        radius = 50 + energy * 300 * (i / points)

        x = int(center[0] + np.cos(angle) * radius)
        y = int(center[1] + np.sin(angle) * radius)

        # Smooth hue shift based on angle + time
        hue = (angle * 30 + time.time() * 100) % 360
        color = pygame.Color(0)
        color.hsva = (hue, 100, 100, 100)

        # Draw small particle
        size = max(2, int(4 + bands['treble'] * 8))
        pygame.draw.circle(screen, color, (x, y), size)
        
# Circular Color Halo - BEST-------------------------------------------------------------------
def circular_color_halo(context):
    screen, bands, WIDTH, HEIGHT = context
    center = (WIDTH//2, HEIGHT//2)
    for i, (name, val) in enumerate(bands.items()):
        radius = int(100 + val*200)
        h = int((i*120 + time.time()*60) % 360)
        color = pygame.Color(0)
        color.hsva = (h, 100, 100, 30)  # 30% alpha for transparency
        pygame.draw.circle(screen, color, center, radius, 8)