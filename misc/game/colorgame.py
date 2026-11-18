import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (RGB format)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
GREEN = (46, 204, 113)
YELLOW = (241, 196, 15)
BG_COLOR = (245, 247, 250)
BUTTON_COLOR = (46, 204, 113)
BUTTON_HOVER = (39, 174, 96)

# Map color names to RGB tuples
COLOR_DICT = {
    "Red": RED,
    "Blue": BLUE,
    "Green": GREEN,
    # "Black": BLACK,
    "Yellow": YELLOW,
    # "White": WHITE
}

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kids Color Learning Game!")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont(None, 56)
font_medium = pygame.font.SysFont(None, 36)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.radius = random.randint(5, 9)
        self.life = 25  
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Balloon:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.name, self.rgb = random.choice(list(COLOR_DICT.items()))
        self.radius = 55  
        self.x = random.randint(100, WIDTH - 100)
        self.y = HEIGHT + self.radius
        self.speed = random.randint(1, 2)  
        
    def update(self):
        self.y -= self.speed  
        if self.y < -self.radius:
            self.reset()
            
    def draw(self, surface):
        pygame.draw.circle(surface, self.rgb, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (self.x - 15, self.y - 15), 12)
        knot_points = [(self.x - 6, self.y + self.radius), 
                       (self.x + 6, self.y + self.radius), 
                       (self.x, self.y + self.radius + 12)]
        pygame.draw.polygon(surface, self.rgb, knot_points)

def main():
    # Game state: "START_SCREEN" or "PLAYING"
    game_state = "START_SCREEN"
    
    balloons = [Balloon() for _ in range(4)]
    particles = []  
    
    target_name, target_rgb = random.choice(list(COLOR_DICT.items()))
    
    score = 0
    feedback_text = ""
    feedback_timer = 0

    # Button dimensions for start screen
    button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 80)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BG_COLOR)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "START_SCREEN":
                    if button_rect.collidepoint(mouse_pos):
                        game_state = "PLAYING"  # Start the game!
                        
                elif game_state == "PLAYING":
                    for balloon in balloons:
                        distance = ((mouse_pos[0] - balloon.x) ** 2 + (mouse_pos[1] - balloon.y) ** 2) ** 0.5
                        if distance <= balloon.radius:
                            if balloon.name == target_name:
                                score += 1
                                feedback_text = "Yay! Pop!"
                                feedback_timer = 45 
                                
                                for _ in range(25):
                                    particles.append(Particle(balloon.x, balloon.y, balloon.rgb))
                                    
                                target_name, target_rgb = random.choice(list(COLOR_DICT.items()))
                                balloon.reset()
                            else:
                                feedback_text = f"Oops! That was {balloon.name}."
                                feedback_timer = 45

        # --- DRAW SCREENS BASED ON STATE ---
        if game_state == "START_SCREEN":
            # Title text
            title_surface = font_large.render("Kids Color Learning Game!", True, BLACK)
            title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
            screen.blit(title_surface, title_rect)

            # Subtitle
            sub_surface = font_medium.render("Pop the matching color balloons!", True, (100, 100, 100))
            sub_rect = sub_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(sub_surface, sub_rect)

            # Draw Start Button
            is_hovered = button_rect.collidepoint(mouse_pos)
            current_button_color = BUTTON_HOVER if is_hovered else BUTTON_COLOR
            
            pygame.draw.rect(screen, current_button_color, button_rect, border_radius=15)
            pygame.draw.rect(screen, BLACK, button_rect, 3, border_radius=15)  # Border outline
            
            # Button text
            btn_text = font_large.render("START GAME", True, WHITE)
            btn_rect = btn_text.get_rect(center=button_rect.center)
            screen.blit(btn_text, btn_rect)

        elif game_state == "PLAYING":
            # Update and draw balloons
            for balloon in balloons:
                balloon.update()
                balloon.draw(screen)

            # Update and draw explosion particles
            for p in particles[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    particles.remove(p)

            # Draw UI Banner at the top
            pygame.draw.rect(screen, (230, 235, 245), (0, 0, WIDTH, 110))
            pygame.draw.line(screen, (200, 210, 225), (0, 110), (WIDTH, 110), 3)

            # Render instructions
            instruction_surface = font_medium.render("Pop the balloon that matches this color:", True, BLACK)
            screen.blit(instruction_surface, (30, 20))

            # DRAW TARGET PICTURE (Colored circle)
            target_circle_center = (600, 55)
            target_radius = 25
            
            if target_rgb == WHITE:
                pygame.draw.circle(screen, BLACK, target_circle_center, target_radius + 2)
                
            pygame.draw.circle(screen, target_rgb, target_circle_center, target_radius)

            # Render Score
            score_surface = font_medium.render(f"Score: {score}", True, (40, 40, 40))
            screen.blit(score_surface, (WIDTH - 150, 70))

            # Render feedback message if active
            if feedback_timer > 0:
                feedback_surface = font_medium.render(feedback_text, True, (200, 50, 50))
                screen.blit(feedback_surface, (30, 70))
                feedback_timer -= 1

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()