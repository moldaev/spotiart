import numpy as np
import sounddevice as sd
import pygame
import threading
import colorsys
import time
import visuals

# === CONFIG ===
SAMPLERATE = 44100
CHUNK = 2048
WIDTH, HEIGHT = 1500, 700
global audio_data

bands = {'bass': 0, 'mid': 0, 'treble': 0}
running = True

def audio_callback(indata, frames, time_, status):
    global bands
    if status:
        print(status)
    audio_data = np.mean(indata, axis=1)

    # FFT
    fft = np.fft.rfft(audio_data)
    freq = np.fft.rfftfreq(len(audio_data), 1/SAMPLERATE)
    magnitude = np.abs(fft)

    # Band energies
    def energy(low, high):
        idx = np.where((freq >= low) & (freq < high))
        return np.mean(magnitude[idx]) if len(idx[0]) > 0 else 0

    bands = {
        'bass': energy(20, 250),
        'mid': energy(250, 2000),
        'treble': energy(2000, 8000)
    }

def find_loopback_device():
    target_keywords = ["Sztereó keverő", "Realtek(R)"]
    devices = sd.query_devices()

    found_id = None
    for idx, device in enumerate(devices):
        name = device['name']
        for keyword in target_keywords:
            if keyword in name:
                found_id = idx
                print(f"Found target device '{name}' with ID {found_id}")
                break
        if found_id is not None:
            break
    return found_id

def audio_thread():
    with sd.InputStream(device=find_loopback_device(), channels=1, callback=audio_callback,
                        samplerate=SAMPLERATE, blocksize=CHUNK):
        while running:
            sd.sleep(100)

def draw_flow(screen, hue_shift):
    screen.fill((0, 0, 0, 0))
    center = (WIDTH // 2, HEIGHT // 2)
    max_val = max(bands.values()) or 1

    # Normalize and smooth motion
    bass = min(bands['bass'] / max_val, 1)
    mid = min(bands['mid'] / max_val, 1)
    treb = min(bands['treble'] / max_val, 1)

    # Dynamic color palette based on time
    hue_base = (time.time() * 30 + hue_shift) % 360

    # Convert HSL -> RGB (for artistic gradients)
    def hsl_color(offset, brightness=1):
        rgb = colorsys.hsv_to_rgb(((hue_base + offset) % 360) / 360, 1, brightness)
        return tuple(int(c * 255) for c in rgb)

    # Background fade (motion trail effect)
    fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade_surface.fill((0, 0, 0, 35))  # semi-transparent black
    screen.blit(fade_surface, (0, 0))

    # Draw flowing circles
    radius_bass = int(100 + bass * 300)
    radius_mid = int(80 + mid * 250)
    radius_treb = int(60 + treb * 200)

    #noisy when not playing anything
    # pygame.draw.circle(screen, hsl_color(0, treb), center, radius_bass, width=6)
    # pygame.draw.circle(screen, hsl_color(120, bass), center, radius_mid, width=5)
    # pygame.draw.circle(screen, hsl_color(240, mid), center, radius_treb, width=4)
    
    context = (screen, bands, WIDTH, HEIGHT)
    
    # visuals.enhanced_audio_heart_pulse(context)

    # visuals.circular_color_halo(context)
    visuals.spiral_spectrum(context)
    visuals.heart_pulse(context)
    visuals.mountain_ridge(context)
    visuals.scatter_glow(context)
    visuals.radial_bars(context)
    visuals.circular_particle_vortex(context)
    visuals.equalizer_mountain_ridges(context)
    visuals.radial_wave_ripples(context)
    visuals.polygon_morph(context)
    visuals.frequency_landscape(context)
    visuals.frequency_3d(context)
    visuals.five_wing_flapping(context)
    visuals.dual_ridge_sound_mountain(context)
    visuals.mirrored_eq(context)
    visuals.audio_heart_pulse(context)
    visuals.enhanced_audio_heart_pulse(context)
    visuals.spyral_spectrum(context)
    visuals.enhanced_spyral_spectrum(context)
    visuals.circular_color_halo(context)

    pygame.display.flip()

def main():
    global running
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎵 BeatLight Flow — Audio Reactive Art")

    thread = threading.Thread(target=audio_thread)
    thread.start()

    clock = pygame.time.Clock()
    hue_shift = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_flow(screen, hue_shift)
        hue_shift += 1
        clock.tick(250)

    pygame.quit()

if __name__ == "__main__":
    main()
