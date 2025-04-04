import pygame
import sys
import random

pygame.init()

# Impostazioni finestra
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Square!")
clock = pygame.time.Clock()
FPS = 60

# Caricamento immagini
background_img = pygame.image.load("background.png")
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

start_screen_img = pygame.image.load("start_screen.png")
start_screen_img = pygame.transform.scale(start_screen_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

bird_img = pygame.image.load("bird.png")
bird_img = pygame.transform.scale(bird_img, (40, 30))

pipe_img = pygame.image.load("pipe.png")
pipe_img = pygame.transform.scale(pipe_img, (80, SCREEN_HEIGHT))

game_over_img = pygame.image.load("game_over.png")
game_over_img = pygame.transform.scale(game_over_img, (500, 90))

# Sfondo per la leaderboard (utilizzato nella schermata leaderboard)
leaderboard_bg_img = pygame.image.load("leaderboard_bg.png")
leaderboard_bg_img = pygame.transform.scale(leaderboard_bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Caricamento effetti sonori e musica
jump_sound = pygame.mixer.Sound("jump.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
point_sound = pygame.mixer.Sound("point.wav")
enter_sound = pygame.mixer.Sound("enter.wav")
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0)

# Colori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Parametri dell'uccellino
bird_x = 100
bird_y = SCREEN_HEIGHT // 2
bird_speed_y = 0
gravity = 0.5
jump_strength = -10
rotation_angle = 0

# Parametri dei tubi
pipe_gap = 200
pipe_speed = 5
pipes = []
pipe_frequency = 1500
last_pipe_time = pygame.time.get_ticks()

# Punteggio, Best Score e flag per nuovo record
score = 0
best_score = 0
new_record_flag = False

# Font di base e per la leaderboard (più grande)
font = pygame.font.Font(None, 36)
leaderboard_font = pygame.font.Font(None, 42)

# Variabile per l'inserimento del nickname
nickname = ""

# Funzioni per la leaderboard
def load_leaderboard():
    entries = []
    try:
        with open("leaderboard.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if ',' in line:
                    name, s = line.split(',', 1)
                    entries.append((name, int(s)))
                else:
                    entries.append(("", int(line)))
        return entries
    except FileNotFoundError:
        return []

def save_leaderboard_record(nickname, score):
    entries = load_leaderboard()
    entries.append((nickname, score))
    entries = sorted(entries, key=lambda x: x[1], reverse=True)
    with open("leaderboard.txt", "w") as f:
        for entry in entries[:5]:
            f.write(f"{entry[0]},{entry[1]}\n")

# Stati del gioco
# Possibili stati: "title", "difficulty", "waiting", "playing", "gameover", "leaderboard", "insert_nickname", "confirm_exit"
state = "title"
previous_state = None

difficulty = None
def set_difficulty(level):
    global gravity, jump_strength, difficulty
    difficulty = level
    if level == "easy":
        gravity = 0.4
        jump_strength = -8
    elif level == "medium":
        gravity = 0.5
        jump_strength = -10
    elif level == "hard":
        gravity = 0.6
        jump_strength = -12

def reset_game():
    global bird_y, bird_speed_y, pipes, score, last_pipe_time, pipe_speed, rotation_angle
    bird_y = SCREEN_HEIGHT // 2
    bird_speed_y = 0
    rotation_angle = 0
    pipes = []
    last_pipe_time = pygame.time.get_ticks()
    score = 0
    pipe_speed = 5

def draw_confirm_exit():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    confirm_text = font.render("Vuoi tornare al titolo? (Y/N)", True, WHITE)
    rect = confirm_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(confirm_text, rect)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == "title":
                if event.key == pygame.K_RETURN:
                    enter_sound.play()
                    state = "difficulty"
                elif event.key == pygame.K_l:
                    enter_sound.play()
                    state = "leaderboard"
            elif state == "leaderboard":
                if event.key == pygame.K_ESCAPE:
                    state = "title"
            elif state == "difficulty":
                if event.key == pygame.K_e:
                    set_difficulty("easy")
                    enter_sound.play()
                    state = "waiting"
                elif event.key == pygame.K_m:
                    set_difficulty("medium")
                    enter_sound.play()
                    state = "waiting"
                elif event.key == pygame.K_h:
                    set_difficulty("hard")
                    enter_sound.play()
                    state = "waiting"
            elif state == "waiting":
                if event.key == pygame.K_SPACE:
                    bird_speed_y = jump_strength
                    jump_sound.play()
                    state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    previous_state = state
                    state = "confirm_exit"
            elif state == "playing":
                if event.key == pygame.K_SPACE:
                    bird_speed_y = jump_strength
                    jump_sound.play()
                elif event.key == pygame.K_ESCAPE:
                    previous_state = state
                    state = "confirm_exit"
            elif state == "gameover":
                if event.key == pygame.K_RETURN:
                    enter_sound.play()
                    reset_game()
                    state = "waiting"
                elif event.key == pygame.K_ESCAPE:
                    previous_state = state
                    state = "confirm_exit"
            elif state == "insert_nickname":
                if event.key == pygame.K_RETURN:
                    save_leaderboard_record(nickname, score)
                    state = "gameover"
                    new_record_flag = True
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    if len(nickname) < 10 and event.unicode.isprintable():
                        nickname += event.unicode
            elif state == "confirm_exit":
                if event.key == pygame.K_y:
                    reset_game()
                    state = "title"
                elif event.key == pygame.K_n:
                    state = previous_state

    if state == "playing":
        bird_speed_y += gravity
        bird_y += bird_speed_y
        rotation_angle = min(max(-bird_speed_y * 3, -30), 30)
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > pipe_frequency:
            last_pipe_time = current_time
            pipe_height = random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)
            pipes.append({"x": SCREEN_WIDTH, "height": pipe_height, "scored": False})
        for pipe in pipes:
            pipe["x"] -= pipe_speed
        for pipe in pipes:
            if not pipe["scored"] and bird_x > pipe["x"] + 80:
                score += 1
                point_sound.play()
                pipe["scored"] = True
        pipes = [pipe for pipe in pipes if pipe["x"] + 80 > 0]
        bird_rect = pygame.Rect(bird_x, bird_y, 40, 30)
        for pipe in pipes:
            pipe_top = pygame.Rect(pipe["x"], 0, 80, pipe["height"])
            pipe_bottom = pygame.Rect(pipe["x"], pipe["height"] + pipe_gap, 80, SCREEN_HEIGHT - pipe["height"] - pipe_gap)
            if bird_rect.colliderect(pipe_top) or bird_rect.colliderect(pipe_bottom) or bird_y < 0 or bird_y > SCREEN_HEIGHT:
                hit_sound.play()
                if score > best_score:
                    best_score = score
                    nickname = ""
                    state = "insert_nickname"
                else:
                    state = "gameover"
                break

    # Disegno in base allo stato
    if state == "title":
        screen.blit(start_screen_img, (0, 0))
        leaderboard_text = font.render("Premi L per visualizzare la leaderboard", True, BLACK)
        text_rect = leaderboard_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        screen.blit(leaderboard_text, text_rect)
    elif state == "leaderboard":
        screen.blit(leaderboard_bg_img, (0, 0))
        title_text = font.render("Leaderboard", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH//2, 50)))
        board = load_leaderboard()
        for idx, (name, score_val) in enumerate(board, start=1):
            score_line = leaderboard_font.render(f"{idx}. {name} - Score: {score_val}", True, WHITE)
            screen.blit(score_line, score_line.get_rect(topleft=(310, 150 + idx * 50)))
        exit_text = font.render("Premi ESC per tornare al titolo", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))
    elif state == "difficulty":
        screen.fill(BLACK)
        diff_text = font.render("Seleziona difficoltà: E - Easy, M - Medium, H - Hard", True, WHITE)
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(diff_text, diff_rect)
    elif state == "waiting":
        screen.blit(background_img, (0, 0))
        screen.blit(bird_img, (bird_x, bird_y))
        instruct_text = font.render("Premi SPAZIO per saltare", True, WHITE)
        instruct_rect = instruct_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(instruct_text, instruct_rect)
    elif state == "playing":
        screen.blit(background_img, (0, 0))
        rotated_bird = pygame.transform.rotate(bird_img, rotation_angle)
        screen.blit(rotated_bird, (bird_x, bird_y))
        for pipe in pipes:
            screen.blit(pygame.transform.flip(pipe_img, False, True), (pipe["x"], pipe["height"] - SCREEN_HEIGHT))
            screen.blit(pipe_img, (pipe["x"], pipe["height"] + pipe_gap))
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
    elif state == "gameover":
        screen.blit(background_img, (0, 0))
        for pipe in pipes:
            screen.blit(pygame.transform.flip(pipe_img, False, True), (pipe["x"], pipe["height"] - SCREEN_HEIGHT))
            screen.blit(pipe_img, (pipe["x"], pipe["height"] + pipe_gap))
        screen.blit(game_over_img, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//4))
        if new_record_flag:
            retry_text = font.render("Premi INVIO per riprovare", True, BLACK)
            screen.blit(retry_text, retry_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
            new_record_flag = False
        else:
            final_text = font.render(f"Final Score: {score}", True, BLACK)
            best_text = font.render(f"Best Score: {best_score}", True, BLACK)
            retry_text = font.render("Premi INVIO per riprovare", True, BLACK)
            screen.blit(final_text, final_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
            screen.blit(best_text, best_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            screen.blit(retry_text, retry_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))
    elif state == "insert_nickname":
        # Utilizza lo stesso sfondo del game over
        screen.blit(background_img, (0, 0))
        for pipe in pipes:
            screen.blit(pygame.transform.flip(pipe_img, False, True), (pipe["x"], pipe["height"] - SCREEN_HEIGHT))
            screen.blit(pipe_img, (pipe["x"], pipe["height"] + pipe_gap))
        screen.blit(game_over_img, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//4))
        # Tutte le scritte (eccetto l'immagine game over) sono stampate più in basso:
        # - Il "Best Score" (numero 2) viene centrato rispetto alla foto (SCREEN_HEIGHT//4 + 45)
        # - Le altre scritte sono spostate ulteriormente verso il basso
        final_text = font.render(f"Final Score: {score}", True, BLACK)
        best_text = font.render(f"Best Score: {best_score}", True, BLACK)
        new_record_text = font.render("Nuovo record! Inserisci il tuo nickname:", True, BLACK)
        nickname_text = font.render(nickname, True, BLACK)
        screen.blit(best_text, best_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 45)))
        screen.blit(final_text, final_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 90)))
        screen.blit(new_record_text, new_record_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 130)))
        screen.blit(nickname_text, nickname_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 170)))
    elif state == "confirm_exit":
        draw_confirm_exit()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
