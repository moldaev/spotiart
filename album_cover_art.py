import numpy as np
import sounddevice as sd
import pygame
import threading, requests, time
from io import BytesIO
from PIL import Image
import colorsys


# === CONFIG ===
SAMPLERATE = 44100
CHUNK = 1024
WIDTH, HEIGHT = 1200, 1000
PIXEL_SIZE = 5  # smaller = more detailed
running = True
bands = {'bass': 0, 'mid': 0, 'treble': 0}
pixel_polar = None  # stores (radius, angle) for each pixel
center = (WIDTH // 2, HEIGHT // 2)
color_phase = 0
last_bass = 0


# === 1. Download & prepare album art ===
def get_album_surface(url, size=(400, 400)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img = img.resize(size)
    mode = img.mode
    data = img.tobytes()
    return img, pygame.image.fromstring(data, size, mode)

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os

sp = Spotify(auth_manager=SpotifyOAuth(
    scope="user-read-currently-playing",
    # If you set env vars (recommended), you don't need to pass client_id/client_secret here.
    # client_id="...", client_secret="...",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

# This will open a browser the first run so you can authorize the app
now = sp.current_user_playing_track()
if now and now['item']:
    print("Track:", now['item']['name'], "by", now['item']['artists'][0]['name'])
    album_url = now['item']['album']['images'][0]['url']
    print("Album cover URL:", album_url)


ALBUM_URL = album_url 
album_img, album_surface = get_album_surface(ALBUM_URL)

# === 2. Audio processing ===
def audio_callback(indata, frames, time_, status):
    global bands
    audio_data = np.mean(indata, axis=1)
    fft = np.fft.rfft(audio_data)
    freq = np.fft.rfftfreq(len(audio_data), 1/SAMPLERATE)
    magnitude = np.abs(fft)

    def energy(low, high):
        idx = np.where((freq >= low) & (freq < high))
        return np.mean(magnitude[idx]) if len(idx[0]) > 0 else 0

    bands = {
        'bass': energy(20, 250),
        'mid': energy(250, 2000),
        'treble': energy(2000, 8000)
    }

def audio_thread():
    with sd.InputStream(channels=1, callback=audio_callback, device = 0,
                        samplerate=SAMPLERATE, blocksize=CHUNK):
        while running:
            sd.sleep(100)

# === 3. Visualization ===
def main():
    global running
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎨 Album Pixel Pulse Visualizer")

    threading.Thread(target=audio_thread, daemon=True).start()
    clock = pygame.time.Clock()

    start_time = time.time()
    pixel_mode = False

    # Precompute center
    center = (WIDTH // 2, HEIGHT // 2)
    base_rect = album_surface.get_rect(center=center)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed = time.time() - start_time
        if elapsed > 3 and not pixel_mode:
            pixel_mode = True  # switch to pixel art mode
            print("🎆 Switching to pixel mode!")

        screen.fill((0, 0, 0))

        max_val = max(bands.values()) or 1
        bass, mid, treb = [bands[k] / max_val for k in bands]

        if not pixel_mode:
            # --- Regular album art view ---
            scale = 1.0 + 0.1 * bass
            scaled_img = pygame.transform.rotozoom(album_surface, 0, scale)
            rect = scaled_img.get_rect(center=center)
            screen.blit(scaled_img, rect)

            # Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(int(120 * (bass + mid + treb) / 3))
            overlay.fill((
                int(255 * bass),
                int(255 * mid),
                int(255 * treb)
            ))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        else:
            # --- Pixel mode (full-screen swirling) ---
            # Keep the original album art size small, just for colors
            small = album_img.resize((album_img.width // PIXEL_SIZE, album_img.height // PIXEL_SIZE))
            pixels = np.array(small)
            h_pixels, w_pixels, _ = pixels.shape

            global pixel_polar, color_phase, last_bass

            # Initialize polar coordinates for full screen
            if pixel_polar is None:
                pixel_polar = np.zeros((h_pixels, w_pixels, 2))  # [radius, angle]
                max_radius = min(WIDTH, HEIGHT) // 2 * 0.9  # allow pixels to almost reach edges
                for y in range(h_pixels):
                    for x in range(w_pixels):
                        dx = (x / w_pixels - 0.5) * max_radius * 2
                        dy = (y / h_pixels - 0.5) * max_radius * 2
                        r = np.sqrt(dx**2 + dy**2)
                        theta = np.arctan2(dy, dx)
                        pixel_polar[y, x, 0] = r
                        pixel_polar[y, x, 1] = theta

            # Detect beat to shift hue
            if bass > last_bass * 1.3 and bass > 0.01:
                color_phase = (color_phase + 0.05) % 1.0
            last_bass = bass

            # Draw swirling pixels
            for y in range(h_pixels):
                for x in range(w_pixels):
                    r, theta = pixel_polar[y, x]

                    # Update angle to swirl; treble controls rotation speed
                    theta += treb * 0.5
                    pixel_polar[y, x, 1] = theta

                    # Pulse radius with bass
                    r_display = r * (1 + bass * 0.5)

                    # Convert polar to screen coordinates
                    px = int(center[0] + r_display * np.cos(theta))
                    py = int(center[1] + r_display * np.sin(theta))

                    # Pick color from album art pixel
                    orig_r, orig_g, orig_b = pixels[y, x]
                    h = (color_phase + (orig_r + orig_g + orig_b) / 765) % 1.0
                    s = 1.0
                    v = min(1, 0.6 + 0.8 * bass)
                    r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)

                    pygame.draw.rect(screen, (int(r2 * 255), int(g2 * 255), int(b2 * 255)),
                                    (px, py, PIXEL_SIZE, PIXEL_SIZE))


        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
