import pygame
import random
import sys
import json

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT_NAME = pygame.font.match_font('arial')
SCORE_FILE = "scores.json"
WORDS_FILE = "words.json"

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ahorcado')

# Load words
def leer_archivo(archivo):
    with open(archivo, 'r') as archivo:
        ahorcado = json.load(archivo)["ahorcado"]
    return ahorcado

WORDS = leer_archivo('ahorcado.json')

# Game variables
selected_word = None
guessed = []
attempts = 6
points = 0
game_over = False
language = None
nickname = ""
input_active = False
words_copy = WORDS.copy()
mute = False  # Sound mute flag

# Load and set up sounds
pygame.mixer.music.set_volume(0.7)
sonido_fondo = pygame.mixer.Sound("ringtones-got-theme.mp3")
sonido_fondo.set_volume(0.2)

# Load icons
sound_on_icon = pygame.image.load('unmute.png')
sound_off_icon = pygame.image.load('mute.png')
icon_size = 50
icon_pos = (WIDTH - icon_size - 10, 10)  # Top-right corner

# Load background image
background_image = pygame.image.load('fondo.png').convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Fonts
font = pygame.font.Font(FONT_NAME, 36)

# Position constants
TITLE_POS = (WIDTH / 2, 50)
WORD_POS = (WIDTH / 2, 150)
ATTEMPTS_POS = (WIDTH / 2, 200)
POINTS_POS = (WIDTH / 2, 250)
HANGMAN_POS = (400, 400)
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
BUTTON_START_Y = HEIGHT / 2 - 100
BUTTON_SPACING = 70

# Drawing functions
def draw_text(surf, text, size, x, y, align="center"):
    font = pygame.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.midtop = (x, y)
    elif align == "left":
        text_rect.topleft = (x, y)
    elif align == "right":
        text_rect.topright = (x, y)
    surf.blit(text_surface, text_rect)

def draw_hangman(attempts):
    if attempts <= 5:
        pygame.draw.circle(screen, BLACK, HANGMAN_POS, 30, 3)  # Head
    if attempts <= 4:
        pygame.draw.rect(screen, BLACK, (HANGMAN_POS[0] - 15, HANGMAN_POS[1] + 30, 30, 60), 3)  # Torso
    if attempts <= 3:
        pygame.draw.line(screen, BLACK, (HANGMAN_POS[0], HANGMAN_POS[1] + 30), (HANGMAN_POS[0] - 50, HANGMAN_POS[1] + 80), 3)  # Left Arm
    if attempts <= 2:
        pygame.draw.line(screen, BLACK, (HANGMAN_POS[0], HANGMAN_POS[1] + 30), (HANGMAN_POS[0] + 50, HANGMAN_POS[1] + 80), 3)  # Right Arm
    if attempts <= 1:
        pygame.draw.line(screen, BLACK, (HANGMAN_POS[0], HANGMAN_POS[1] + 90), (HANGMAN_POS[0] - 50, HANGMAN_POS[1] + 150), 3)  # Left Leg
    if attempts <= 0:
        pygame.draw.line(screen, BLACK, (HANGMAN_POS[0], HANGMAN_POS[1] + 90), (HANGMAN_POS[0] + 50, HANGMAN_POS[1] + 150), 3)  # Right Leg

# Language selection function
def select_language():
    selecting = True
    language = None

    while selecting:
        screen.fill(WHITE)
        draw_text(screen, translate("Select Language / Seleccione Idioma"), 48, WIDTH / 2, 100)
        draw_text(screen, translate("Press 'E' for English or 'S' for Spanish"), 36, WIDTH / 2, 200)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Exit the program when user closes the window
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    language = 'EN'
                    selecting = False
                elif event.key == pygame.K_s:
                    language = 'ES'
                    selecting = False

    return language

# Function to translate text based on selected language
def translate(key):
    if language == 'EN':
        translations = {
            "Select Language / Seleccione Idioma": "Select Language / Seleccione Idioma",
            "Press 'E' for English or 'S' for Spanish": "Press 'E' for English or 'S' for Spanish",
            "Enter Nickname:": "Enter Nickname:",
            "Word:": "Word:",
            "Attempts Left:": "Attempts Left:",
            "Points:": "Points:",
            "Hangman Game": "Hangman Game",
            "Jugar": "Play",
            "Salir": "Quit",
            "Puntaje": "Scores"
        }
    elif language == 'ES':
        translations = {
            "Select Language / Seleccione Idioma": "Seleccione Idioma / Select Language",
            "Press 'E' for English or 'S' for Spanish": "Presione 'E' para inglés o 'S' para español",
            "Enter Nickname:": "Ingrese Apodo:",
            "Word:": "Palabra:",
            "Attempts Left:": "Intentos Restantes:",
            "Points:": "Puntos:",
            "Hangman Game": "Juego del Ahorcado",
            "Jugar": "Jugar",
            "Salir": "Salir",
            "Puntaje": "Puntaje"
        }
    else:
        return key  # Default to returning the key if language not supported

    return translations.get(key, key)  # Return translated text or key itself if not found

# Nickname input function
def input_nickname():
    global nickname, input_active
    input_active = True
    input_box = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 - 25, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Exit the program when user closes the window
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        nickname = text
                        done = True
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(WHITE)
        draw_text(screen, translate("Enter Nickname:"), 48, WIDTH / 2, HEIGHT / 2 - 100)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()

# Function to create buttons
def draw_button(text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    draw_text(screen, text, 36, x + (width / 2), y + (height / 2) - 18)

# Save scores to a file
def save_scores(scores):
    with open(SCORE_FILE, 'w') as file:
        json.dump(scores, file)

# Load scores from a file
def load_scores():
    try:
        with open(SCORE_FILE, 'r') as archivo:
            ranking = json.load(archivo)["scores"]
    except FileNotFoundError:
        ranking = []
    return ranking

# Function to show the ranking
def show_ranking():
    scores = load_scores()
    scores = sorted(scores, key=lambda x: x['points'], reverse=True)[:5]  # Top 5 scores

    screen.blit(background_image, (0, 0))

    draw_text(screen, translate("High Scores"), 48, WIDTH / 2, 20)
    y_offset = 150
    for score in scores:
        draw_text(screen, f"{score['nickname']}: {score['points']}", 36, WIDTH / 2, y_offset)
        y_offset += 50

    draw_button(translate("Back"), 50, 50, 120, 50, (50, 50, 255), (100, 100, 255), main_menu)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Salir del programa cuando se cierra la ventana
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 50 < mouse_pos[0] < 170 and 50 < mouse_pos[1] < 100:
                    main_menu()  # Vuelve al menú principal si se hace clic en "Back"

def start_game():
    global language, nickname, words_copy

    select_language()
    input_nickname()

    # Reset game variables
    words_copy = WORDS.copy()
    main_game()

def main_menu():
    global language

    # Play background music
    sonido_fondo.play(loops=-1)

    running = True
    while running:
        screen.blit(background_image, (0, 0))  # Draw background image

        # Draw title
        draw_text(screen, translate("Hangman Game"), 48, TITLE_POS[0], TITLE_POS[1])

        # Draw buttons
        draw_button(translate("Jugar"), WIDTH / 2 - BUTTON_WIDTH / 2, BUTTON_START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, WHITE, (200, 200, 200), start_game)
        draw_button(translate("Puntaje"), WIDTH / 2 - BUTTON_WIDTH / 2, BUTTON_START_Y + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT, WHITE, (200, 200, 200), show_ranking)
        draw_button(translate("Salir"), WIDTH / 2 - BUTTON_WIDTH / 2, BUTTON_START_Y + 2 * BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT, WHITE, (200, 200, 200), pygame.quit)

        # Draw sound icon
        if mute:
            screen.blit(sound_off_icon, icon_pos)
        else:
            screen.blit(sound_on_icon, icon_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Exit the program when user closes the window
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Check if sound icon clicked
                if icon_pos[0] <= mouse_pos[0] <= icon_pos[0] + icon_size and icon_pos[1] <= mouse_pos[1] <= icon_pos[1] + icon_size:
                    toggle_sound()

# Main game loop
def main_game():
    global selected_word, guessed, attempts, points, game_over, words_copy, mute

    if not words_copy:
        draw_text(screen, f"{translate('Final Score for')} {nickname}: {points}", 48, WIDTH / 2, HEIGHT / 2)
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    selected_word = random.choice([word[language] for word in words_copy])
    words_copy = [word for word in words_copy if word[language] != selected_word]
    guessed = ['_' for _ in selected_word]
    attempts = 6
    game_over = False

    running = True
    while running:
        screen.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not game_over and not input_active:
                if event.unicode.isalpha():
                    char = event.unicode.lower()
                    if char in selected_word:
                        for i in range(len(selected_word)):
                            if selected_word[i] == char:
                                guessed[i] = char
                                points += 1
                    else:
                        attempts -= 1

        if attempts == 0 or '_' not in guessed:
            game_over = True

        draw_text(screen, translate("Hangman Game"), 48, TITLE_POS[0], TITLE_POS[1])
        draw_text(screen, f"{translate('Word')}: {' '.join(guessed)}", 36, WORD_POS[0], WORD_POS[1])
        draw_text(screen, f"{translate('Attempts Left')}: {attempts}", 36, ATTEMPTS_POS[0], ATTEMPTS_POS[1])
        draw_text(screen, f"{translate('Points')}: {points}", 36, POINTS_POS[0], POINTS_POS[1])
        draw_hangman(attempts)

        if game_over:
            pygame.time.wait(1000)
            main_game()

        pygame.display.flip()

    pygame.quit()

# Function to toggle sound
def toggle_sound():
    global mute
    mute = not mute
    if mute:
        sonido_fondo.stop()
    else:
        sonido_fondo.play(-1)  # Loop the sound indefinitely

# Start the game
select_language()
input_nickname()
main_menu()

#traducido no se puede mutear