import pygame
import random
import sys

# Inisialisasi Pygame
pygame.init()
pygame.mixer.init()  # Inisialisasi mixer untuk audio

# Konstanta - Game Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Konstanta - Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
NIGHT_BLUE = (0, 0, 30)
NIGHT_NAVY = (0, 0, 50)

# Konstanta - Button Colors
BUTTON_NORMAL = (0, 150, 0)
BUTTON_HOVER = (0, 200, 0)
BUTTON_PRESS = (0, 100, 0)

# Konstanta - Game Rules
MAX_HEARTS = 3
MAX_LEVEL = 20
BASE_TIMER = 20
HINT_AVAILABLE_AT_HEARTS = 1
SHAKE_DURATION = 10
COMBO_BONUS_SCORE = 2  # Bonus skor per combo

# Setup layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🧟‍♂️ Zombie Math Game 🧮")
clock = pygame.time.Clock()

# Font
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

# ===== MUSIK & SOUND EFFECTS =====
# Load background music
try:
    pygame.mixer.music.load("background_music.mp3")  # Ganti dengan nama file musik Anda
    pygame.mixer.music.set_volume(0.3)  # Volume 30%
    pygame.mixer.music.play(-1)  # -1 = loop terus menerus
    MUSIC_LOADED = True
except:
    print("⚠️ File musik tidak ditemukan. Game berjalan tanpa musik.")
    MUSIC_LOADED = False

# Load sound effects (opsional)
try:
    sound_correct = pygame.mixer.Sound("correct.wav")  # Suara jawaban benar
    sound_correct.set_volume(0.5)
    SOUND_CORRECT_LOADED = True
except:
    print("⚠️ File sound 'correct.wav' tidak ditemukan.")
    SOUND_CORRECT_LOADED = False

try:
    sound_wrong = pygame.mixer.Sound("wrong.wav")  # Suara jawaban salah
    sound_wrong.set_volume(0.5)
    SOUND_WRONG_LOADED = True
except:
    print("⚠️ File sound 'wrong.wav' tidak ditemukan.")
    SOUND_WRONG_LOADED = False

try:
    sound_gameover = pygame.mixer.Sound("gameover.wav")  # Suara game over
    sound_gameover.set_volume(0.6)
    SOUND_GAMEOVER_LOADED = True
except:
    print("⚠️ File sound 'gameover.wav' tidak ditemukan.")
    SOUND_GAMEOVER_LOADED = False

try:
    sound_win = pygame.mixer.Sound("win.wav")  # Suara menang
    sound_win.set_volume(0.6)
    SOUND_WIN_LOADED = True
except:
    print("⚠️ File sound 'win.wav' tidak ditemukan.")
    SOUND_WIN_LOADED = False

class GraveyardBackground:
    def __init__(self):
        self.graves = []
        self.moon = {'x': 600, 'y': 100, 'size': 40}
        self.clouds = [{'x': i * 200, 'y': random.randint(50, 150), 'speed': random.uniform(0.5, 1)} for i in range(3)]
        
        # Buat kuburan dengan variasi
        for _ in range(8):
            width = random.randint(60, 100)
            height = random.randint(40, 60)
            x = random.randint(-50, SCREEN_WIDTH - width)
            y = SCREEN_HEIGHT - height - random.randint(10, 30)
            self.graves.append({
                'rect': pygame.Rect(x, y, width, height),
                'color': (30, 30, 40)
            })
    
    def draw(self, screen):
        # Langit malam gelap
        screen.fill(NIGHT_BLUE)
        
        # Bulan
        pygame.draw.circle(screen, (240, 240, 200), (self.moon['x'], self.moon['y']), self.moon['size'])
        pygame.draw.circle(screen, NIGHT_BLUE, (self.moon['x'] - 10, self.moon['y']), int(self.moon['size'] * 0.7))
        
        # Awan bergerak lambat
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            if cloud['x'] > SCREEN_WIDTH + 100:
                cloud['x'] = -100
            pygame.draw.ellipse(screen, (50, 50, 70), 
                              pygame.Rect(int(cloud['x']), int(cloud['y']), 120, 40))
        
        # Kuburan
        for grave in self.graves:
            # Batu nisan
            pygame.draw.rect(screen, grave['color'], grave['rect'], border_radius=5)
            # Salib sederhana
            cross_x = grave['rect'].centerx
            cross_y = grave['rect'].top - 10
            pygame.draw.line(screen, (70, 70, 90), (cross_x, cross_y), (cross_x, cross_y - 20), 3)
            pygame.draw.line(screen, (70, 70, 90), (cross_x - 10, cross_y - 10), (cross_x + 10, cross_y - 10), 3)
        
        # Pohon mati
        for i in range(3):
            tree_x = i * 300 + 50
            pygame.draw.line(screen, (40, 30, 20), (tree_x, SCREEN_HEIGHT), (tree_x, SCREEN_HEIGHT - 150), 8)
            for branch in range(5):
                pygame.draw.line(screen, (40, 30, 20), 
                               (tree_x, SCREEN_HEIGHT - 150 + branch * 15), 
                               (tree_x + random.choice([-20, 20]), SCREEN_HEIGHT - 150 + branch * 15), 3)

class Zombie:
    """Class untuk merepresentasikan zombie individual"""
    def __init__(self, x, y, answer, is_correct):
        self.x = x
        self.y = y
        self.answer = answer
        self.is_correct = is_correct
        self.bounce = 0
    
    def update(self):
        self.bounce = (self.bounce + 0.1) % 6.28
    
    def draw(self, screen, font):
        bounce_offset = int(10 * abs(pygame.math.Vector2(0, 1).rotate(self.bounce * 57.3).y))
        zombie_y = self.y - bounce_offset
        zombie_x = self.x
        
        # Kepala zombie
        pygame.draw.circle(screen, (50, 150, 50), (zombie_x, zombie_y - 30), 30)
        # Mata kiri
        pygame.draw.circle(screen, WHITE, (zombie_x - 12, zombie_y - 35), 8)
        pygame.draw.circle(screen, BLACK, (zombie_x - 10, zombie_y - 35), 4)
        # Mata kanan
        pygame.draw.circle(screen, WHITE, (zombie_x + 12, zombie_y - 35), 8)
        pygame.draw.circle(screen, BLACK, (zombie_x + 14, zombie_y - 35), 4)
        
        # Mulut zigzag
        mouth_points = [
            (zombie_x - 15, zombie_y - 20),
            (zombie_x - 10, zombie_y - 15),
            (zombie_x - 5, zombie_y - 20),
            (zombie_x, zombie_y - 15),
            (zombie_x + 5, zombie_y - 20),
            (zombie_x + 10, zombie_y - 15),
            (zombie_x + 15, zombie_y - 20)
        ]
        for i in range(len(mouth_points) - 1):
            pygame.draw.line(screen, BLACK, mouth_points[i], mouth_points[i + 1], 3)
        
        # Badan
        pygame.draw.rect(screen, (40, 120, 40), (zombie_x - 25, zombie_y, 50, 60))
        # Tangan kiri
        pygame.draw.rect(screen, (50, 150, 50), (zombie_x - 45, zombie_y + 10, 20, 35))
        # Tangan kanan
        pygame.draw.rect(screen, (50, 150, 50), (zombie_x + 25, zombie_y + 10, 20, 35))
        
        # Kotak jawaban
        answer_bg = pygame.Rect(zombie_x - 40, zombie_y + 70, 80, 50)
        pygame.draw.rect(screen, (50, 50, 50), answer_bg, border_radius=5)
        pygame.draw.rect(screen, GREEN, answer_bg, 3, border_radius=5)
        
        answer_text = font.render(str(self.answer), True, WHITE)
        answer_rect = answer_text.get_rect(center=answer_bg.center)
        screen.blit(answer_text, answer_rect)
        
        return answer_bg

class Game:
    def __init__(self):
        self.state = "menu"
        self.hearts = MAX_HEARTS
        self.score = 0
        self.level = 1
        self.question = None
        self.zombies = []
        self.shake_timer = 0
        self.show_hint = False
        self.time_left = BASE_TIMER
        self.timer_start = pygame.time.get_ticks()
        self.graveyard = GraveyardBackground()
        
        # Sistem Combo
        self.combo = 0
        self.max_combo = 0
        
        # Animasi tombol - sekarang dictionary untuk track multiple buttons
        self.button_scales = {}
        
        # Volume settings
        self.music_volume = 0.3  # Default 30%
        self.sfx_volume = 0.5    # Default 50%
        self.show_settings = False  # Toggle untuk menampilkan pengaturan
        
        # Dragging state untuk slider
        self.dragging_music = False
        self.dragging_sfx = False
    
    def get_max_number_for_level(self):
        """Menentukan batas angka berdasarkan level"""
        if self.level <= 3:
            return 10
        elif self.level <= 7:
            return 20
        elif self.level <= 12:
            return 50
        elif self.level <= 17:
            return 100
        else:
            return 200
    
    def generate_question(self):
        operations = ['+', '-', '*', '/']
        op = random.choice(operations)
        max_num = self.get_max_number_for_level()
        
        if op == '/':
            num2 = random.randint(1, max(1, min(9, max_num // 10)))
            answer = random.randint(1, max(1, min(10, max_num // 10)))
            num1 = num2 * answer
        elif op == '*':
            num1 = random.randint(1, min(12, max_num // 5))
            num2 = random.randint(1, min(12, max_num // 5))
            answer = num1 * num2
        elif op == '-':
            num1 = random.randint(max_num // 2, max_num)
            num2 = random.randint(0, num1)
            answer = num1 - num2
        else:  # '+'
            num1 = random.randint(1, max_num)
            num2 = random.randint(1, max_num)
            answer = num1 + num2
        
        self.question = {'num1': num1, 'num2': num2, 'op': op, 'answer': answer}
        self.time_left = BASE_TIMER
        self.timer_start = pygame.time.get_ticks()
        
        # Generate wrong answers
        wrong_answers = []
        variance = max(5, answer // 5)
        attempts = 0
        while len(wrong_answers) < 2 and attempts < 20:
            wrong = answer + random.randint(-variance, variance)
            if wrong != answer and wrong not in wrong_answers and wrong > 0:
                wrong_answers.append(wrong)
            attempts += 1
        
        # Fallback jika gagal generate
        while len(wrong_answers) < 2:
            wrong_answers.append(answer + len(wrong_answers) + 1)
        
        all_answers = [answer] + wrong_answers
        random.shuffle(all_answers)
        
        # Create zombie objects
        self.zombies = []
        zombie_positions = [150, 350, 550]
        for i, ans in enumerate(all_answers):
            self.zombies.append(Zombie(zombie_positions[i], 350, ans, ans == answer))
    
    def start_game(self):
        self.state = "playing"
        self.hearts = MAX_HEARTS
        self.score = 0
        self.level = 1
        self.show_hint = False
        self.time_left = BASE_TIMER
        self.combo = 0
        self.max_combo = 0
        self.generate_question()
    
    def shoot_zombie(self, zombie_index):
        if zombie_index >= len(self.zombies):
            return
            
        zombie = self.zombies[zombie_index]
        if zombie.is_correct:
            # Play sound effect untuk jawaban benar
            if SOUND_CORRECT_LOADED:
                sound_correct.set_volume(self.sfx_volume)
                sound_correct.play()
            
            # Jawaban benar - tambah combo
            self.combo += 1
            if self.combo > self.max_combo:
                self.max_combo = self.combo
            
            # Sistem recovery nyawa - tambah nyawa jika kurang dari maksimal
            if self.hearts < MAX_HEARTS:
                self.hearts += 1
            
            # Skor dasar + bonus combo
            base_score = 5
            combo_bonus = (self.combo - 1) * COMBO_BONUS_SCORE
            self.score += base_score + combo_bonus
            
            self.level += 1
            self.show_hint = False
            
            if self.level > MAX_LEVEL:
                # Play sound effect menang
                if SOUND_WIN_LOADED:
                    sound_win.set_volume(self.sfx_volume)
                    sound_win.play()
                pygame.time.wait(500)
                self.state = "win"
                return
            
            pygame.time.wait(300)
            self.generate_question()
        else:
            # Play sound effect untuk jawaban salah
            if SOUND_WRONG_LOADED:
                sound_wrong.set_volume(self.sfx_volume)
                sound_wrong.play()
            
            # Jawaban salah - reset combo
            self.combo = 0
            self.hearts -= 1
            self.shake_timer = SHAKE_DURATION
            if self.hearts == 0:
                # Play sound effect game over
                if SOUND_GAMEOVER_LOADED:
                    sound_gameover.set_volume(self.sfx_volume)
                    sound_gameover.play()
                pygame.time.wait(500)
                self.state = "gameover"
    
    def toggle_hint(self):
        self.show_hint = not self.show_hint
    
    def update_timer(self):
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.timer_start) / 1000
        self.time_left = max(0, BASE_TIMER - int(elapsed))
        
        if self.time_left == 0 and self.state == "playing":
            # Play sound effect game over saat timeout
            if SOUND_GAMEOVER_LOADED:
                sound_gameover.set_volume(self.sfx_volume)
                sound_gameover.play()
            self.combo = 0  # Reset combo saat timeout
            self.hearts = 0
            self.state = "gameover"
    
    def update_volumes(self):
        """Update volume musik dan sound effects"""
        if MUSIC_LOADED:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def draw_slider(self, screen, x, y, width, value, label):
        """Menggambar slider untuk volume control"""
        # Label
        label_text = font_small.render(label, True, WHITE)
        screen.blit(label_text, (x, y - 35))
        
        # Slider track (background)
        track_rect = pygame.Rect(x, y, width, 10)
        pygame.draw.rect(screen, (100, 100, 100), track_rect, border_radius=5)
        
        # Slider fill (progress)
        fill_width = int(width * value)
        fill_rect = pygame.Rect(x, y, fill_width, 10)
        pygame.draw.rect(screen, YELLOW, fill_rect, border_radius=5)
        
        # Slider handle (lingkaran untuk drag)
        handle_x = x + fill_width
        handle_y = y + 5
        pygame.draw.circle(screen, WHITE, (handle_x, handle_y), 12)
        pygame.draw.circle(screen, YELLOW, (handle_x, handle_y), 8)
        
        # Volume percentage
        percent_text = font_small.render(f"{int(value * 100)}%", True, WHITE)
        screen.blit(percent_text, (x + width + 20, y - 8))
        
        return pygame.Rect(handle_x - 12, handle_y - 12, 24, 24)
    
    def draw_settings_panel(self, screen):
        """Menggambar panel pengaturan volume"""
        # Background panel
        panel_width = 500
        panel_height = 350
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Panel background dengan border
        pygame.draw.rect(screen, (30, 30, 50), panel_rect, border_radius=15)
        pygame.draw.rect(screen, YELLOW, panel_rect, 3, border_radius=15)
        
        # Title
        title = font_medium.render("PENGATURAN", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 40))
        screen.blit(title, title_rect)
        
        # Music volume slider
        slider_y = panel_y + 100
        music_handle = self.draw_slider(
            screen, 
            panel_x + 50, 
            slider_y, 
            350, 
            self.music_volume, 
            "Volume Musik:"
        )
        
        # SFX volume slider
        sfx_slider_y = panel_y + 180
        sfx_handle = self.draw_slider(
            screen, 
            panel_x + 50, 
            sfx_slider_y, 
            350, 
            self.sfx_volume, 
            "Volume Efek Suara:"
        )
        
        # Close button
        close_button = pygame.Rect(SCREEN_WIDTH // 2 - 80, panel_y + panel_height - 70, 160, 50)
        mouse_pos = pygame.mouse.get_pos()
        close_scaled = self.animate_button(close_button, "settings_close", close_button.collidepoint(mouse_pos))
        
        close_text = font_small.render("TUTUP", True, WHITE)
        close_text_rect = close_text.get_rect(center=close_scaled.center)
        screen.blit(close_text, close_text_rect)
        
        return music_handle, sfx_handle, close_button
    
    def animate_button(self, rect, button_id, is_hovered, is_pressed=False):
        """Animasi button dengan tracking individual per button"""
        if button_id not in self.button_scales:
            self.button_scales[button_id] = 1.0
        
        target_scale = 1.1 if is_hovered else 1.0
        self.button_scales[button_id] += (target_scale - self.button_scales[button_id]) * 0.2
        
        # Warna berdasarkan state
        if is_pressed:
            color = BUTTON_PRESS
        elif is_hovered:
            color = BUTTON_HOVER
        else:
            color = BUTTON_NORMAL
        
        # Gambar button dengan scale
        scale_diff = self.button_scales[button_id] - 1
        scaled_rect = rect.inflate(
            int(rect.width * scale_diff),
            int(rect.height * scale_diff)
        )
        scaled_rect.center = rect.center
        
        pygame.draw.rect(screen, color, scaled_rect, border_radius=10)
        
        return scaled_rect
    
    def draw_menu(self):
        self.graveyard.draw(screen)
        
        # Judul dengan glow effect
        title = font_large.render("ZOMBIE MATH", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        
        # Efek glow
        glow = font_large.render("ZOMBIE MATH", True, (200, 200, 0))
        for offset in [(2,2), (-2,2), (2,-2), (-2,-2)]:
            screen.blit(glow, title_rect.move(offset))
        screen.blit(title, title_rect)
        
        subtitle = font_small.render("Tembak Zombie dengan Jawaban Benar!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(subtitle, subtitle_rect)
        
        # Tombol mulai dengan animasi
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 330, 200, 60)
        mouse_pos = pygame.mouse.get_pos()
        scaled_rect = self.animate_button(button_rect, "menu_start", button_rect.collidepoint(mouse_pos))
        
        button_text = font_medium.render("MULAI", True, BLACK)
        button_text_rect = button_text.get_rect(center=scaled_rect.center)
        screen.blit(button_text, button_text_rect)
        
        # Tombol pengaturan
        settings_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 410, 200, 60)
        settings_scaled = self.animate_button(settings_button, "menu_settings", settings_button.collidepoint(mouse_pos))
        
        settings_text = font_small.render("PENGATURAN", True, WHITE)
        settings_text_rect = settings_text.get_rect(center=settings_scaled.center)
        screen.blit(settings_text, settings_text_rect)
        
        # Tampilkan panel settings jika aktif
        music_handle = None
        sfx_handle = None
        close_button = None
        if self.show_settings:
            music_handle, sfx_handle, close_button = self.draw_settings_panel(screen)
        
        return button_rect, settings_button, music_handle, sfx_handle, close_button
    
    def draw_win(self):
        self.graveyard.draw(screen)
        
        # Selamat Menang!
        win_text = font_large.render("SELAMAT!", True, YELLOW)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, 120))
        screen.blit(win_text, win_rect)
        
        win_text2 = font_large.render("KAMU MENANG!!!", True, YELLOW)
        win_rect2 = win_text2.get_rect(center=(SCREEN_WIDTH//2, 200))
        screen.blit(win_text2, win_rect2)
        
        # Smiley face
        pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH//2, 280), 40)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH//2 - 15, 270), 5)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH//2 + 15, 270), 5)
        pygame.draw.arc(screen, BLACK, 
                        pygame.Rect(SCREEN_WIDTH//2 - 20, 275, 40, 25), 
                        3.14, 6.28, 3)
        
        # Skor
        score_text = font_medium.render(f"Skor Akhir: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 340))
        screen.blit(score_text, score_rect)
        
        level_text = font_small.render(f"Semua {MAX_LEVEL} Level Selesai!", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, 380))
        screen.blit(level_text, level_rect)
        
        # Tampilkan max combo
        combo_text = font_small.render(f"Max Combo: {self.max_combo}x", True, YELLOW)
        combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH//2, 410))
        screen.blit(combo_text, combo_rect)
        
        # Tombol menu dengan animasi
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 120, 450, 240, 60)
        mouse_pos = pygame.mouse.get_pos()
        scaled_rect = self.animate_button(button_rect, "win_menu", button_rect.collidepoint(mouse_pos))
        
        button_text = font_small.render("MENU UTAMA", True, WHITE)
        button_text_rect = button_text.get_rect(center=scaled_rect.center)
        screen.blit(button_text, button_text_rect)
        
        return button_rect
    
    def draw_gameover(self):
        self.graveyard.draw(screen)
        
        # Game Over dengan efek kedip
        if pygame.time.get_ticks() % 1000 < 500:
            gameover = font_large.render("GAME OVER", True, RED)
            gameover_rect = gameover.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(gameover, gameover_rect)
        
        # Skor
        score_text = font_medium.render(f"Skor Akhir: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(score_text, score_rect)
        
        level_reached = font_small.render(f"Level Tercapai: {self.level}/{MAX_LEVEL}", True, WHITE)
        level_rect = level_reached.get_rect(center=(SCREEN_WIDTH//2, 300))
        screen.blit(level_reached, level_rect)
        
        # Tampilkan max combo
        combo_text = font_small.render(f"Max Combo: {self.max_combo}x", True, YELLOW)
        combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH//2, 330))
        screen.blit(combo_text, combo_rect)
        
        # Tombol menu dengan animasi
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 120, 370, 240, 60)
        mouse_pos = pygame.mouse.get_pos()
        scaled_rect = self.animate_button(button_rect, "gameover_menu", button_rect.collidepoint(mouse_pos))
        
        button_text = font_small.render("MENU UTAMA", True, WHITE)
        button_text_rect = button_text.get_rect(center=scaled_rect.center)
        screen.blit(button_text, button_text_rect)
        
        return button_rect
    
    def draw_playing(self):
        self.graveyard.draw(screen)
        
        # Efek shake
        offset_x, offset_y = 0, 0
        if self.shake_timer > 0:
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            self.shake_timer -= 1
        
        # Tampilkan NYAWA sebagai teks
        nyawa_text = font_medium.render(f"NYAWA: {self.hearts}", True, RED)
        screen.blit(nyawa_text, (30 + offset_x, 20 + offset_y))
        
        # Skor, Level, dan Timer di kanan atas (lebih rapi dan teratur)
        info_x = SCREEN_WIDTH - 200
        
        score_text = font_medium.render(f"Skor: {self.score}", True, YELLOW)
        screen.blit(score_text, (info_x + offset_x, 20 + offset_y))
        
        level_text = font_small.render(f"Level: {self.level}/{MAX_LEVEL}", True, WHITE)
        screen.blit(level_text, (info_x + offset_x, 70 + offset_y))
        
        # Timer
        timer_color = RED if self.time_left <= 5 else YELLOW
        timer_text = font_small.render(f"Waktu: {self.time_left}s", True, timer_color)
        screen.blit(timer_text, (info_x + offset_x, 110 + offset_y))
        
        # Tampilkan COMBO jika > 0
        if self.combo > 0:
            combo_color = YELLOW if self.combo < 5 else (255, 165, 0)  # Orange untuk combo tinggi
            if self.combo >= 10:
                combo_color = RED  # Merah untuk combo sangat tinggi
            
            combo_text = font_medium.render(f"COMBO: {self.combo}x", True, combo_color)
            combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH//2, 70))
            
            # Efek glow untuk combo
            glow_color = tuple(max(0, c - 50) for c in combo_color)
            combo_glow = font_medium.render(f"COMBO: {self.combo}x", True, glow_color)
            for offset in [(2,2), (-2,2), (2,-2), (-2,-2)]:
                screen.blit(combo_glow, combo_rect.move(offset))
            screen.blit(combo_text, combo_rect)
            
            # Tampilkan bonus skor
            if self.combo > 1:
                bonus = (self.combo - 1) * COMBO_BONUS_SCORE
                bonus_text = font_small.render(f"+{bonus} bonus", True, GREEN)
                bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH//2, 105))
                screen.blit(bonus_text, bonus_rect)
        
        # Soal
        hint_button_rect = None
        if self.question:
            question_text = f"{self.question['num1']} {self.question['op']} {self.question['num2']} = ?"
            question_surface = font_large.render(question_text, True, WHITE)
            question_bg = pygame.Rect(SCREEN_WIDTH//2 - 200, 120, 400, 80)
            pygame.draw.rect(screen, (30, 30, 50), question_bg, border_radius=10)
            question_rect = question_surface.get_rect(center=(SCREEN_WIDTH//2, 160))
            screen.blit(question_surface, question_rect)
            
            # Tombol kunci jawaban (hanya tersedia saat 1 hati tersisa)
            if self.hearts == HINT_AVAILABLE_AT_HEARTS:
                hint_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 210, 200, 40)
                hint_color = YELLOW if self.show_hint else (100, 100, 100)
                pygame.draw.rect(screen, hint_color, hint_button_rect, border_radius=5)
                hint_text = font_small.render("Kunci Jawaban", True, BLACK)
                hint_text_rect = hint_text.get_rect(center=hint_button_rect.center)
                screen.blit(hint_text, hint_text_rect)
                
                if self.show_hint:
                    answer_hint = font_medium.render(f"Jawaban: {self.question['answer']}", True, YELLOW)
                    answer_hint_rect = answer_hint.get_rect(center=(SCREEN_WIDTH//2, 270))
                    screen.blit(answer_hint, answer_hint_rect)
        
        # Update dan gambar zombie
        zombie_rects = []
        for zombie in self.zombies:
            zombie.update()
            rect = zombie.draw(screen, font_small)
            zombie_rects.append(rect)
        
        return zombie_rects, hint_button_rect

# Main game loop
def main():
    game = Game()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "menu":
                    if game.show_settings:
                        # Handle settings panel
                        music_handle, sfx_handle, close_button = game.draw_settings_panel(screen)
                        
                        if close_button and close_button.collidepoint(mouse_pos):
                            game.show_settings = False
                        elif music_handle and music_handle.collidepoint(mouse_pos):
                            game.dragging_music = True
                        elif sfx_handle and sfx_handle.collidepoint(mouse_pos):
                            game.dragging_sfx = True
                    else:
                        button, settings_button, _, _, _ = game.draw_menu()
                        if button.collidepoint(mouse_pos):
                            game.start_game()
                        elif settings_button.collidepoint(mouse_pos):
                            game.show_settings = True
                
                elif game.state == "gameover":
                    button = game.draw_gameover()
                    if button.collidepoint(mouse_pos):
                        game.state = "menu"
                        game.show_settings = False
                
                elif game.state == "win":
                    button = game.draw_win()
                    if button.collidepoint(mouse_pos):
                        game.state = "menu"
                        game.show_settings = False
                
                elif game.state == "playing":
                    zombie_rects, hint_button = game.draw_playing()
                    
                    # Check zombie clicks
                    for i, rect in enumerate(zombie_rects):
                        if rect.collidepoint(mouse_pos):
                            game.shoot_zombie(i)
                            break
                    
                    # Check hint button click
                    if hint_button and hint_button.collidepoint(mouse_pos):
                        game.toggle_hint()
            
            if event.type == pygame.MOUSEBUTTONUP:
                game.dragging_music = False
                game.dragging_sfx = False
            
            if event.type == pygame.MOUSEMOTION:
                if game.dragging_music:
                    # Update music volume based on mouse position
                    slider_x = SCREEN_WIDTH // 2 - 200
                    slider_width = 350
                    relative_x = mouse_pos[0] - slider_x
                    game.music_volume = max(0.0, min(1.0, relative_x / slider_width))
                    game.update_volumes()
                
                if game.dragging_sfx:
                    # Update sfx volume based on mouse position
                    slider_x = SCREEN_WIDTH // 2 - 200
                    slider_width = 350
                    relative_x = mouse_pos[0] - slider_x
                    game.sfx_volume = max(0.0, min(1.0, relative_x / slider_width))
        
        # Update timer jika sedang bermain
        if game.state == "playing":
            game.update_timer()
        
        # Draw berdasarkan state
        if game.state == "menu":
            game.draw_menu()
        elif game.state == "gameover":
            game.draw_gameover()
        elif game.state == "win":
            game.draw_win()
        elif game.state == "playing":
            game.draw_playing()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()