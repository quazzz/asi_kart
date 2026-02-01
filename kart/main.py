import pygame
import math
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BLUE = (30, 144, 255)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
BROWN = (139, 69, 19)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    FINISHED = 4

class Kart:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.color = color
        self.is_player = is_player
        self.max_speed = 8 if is_player else 6
        self.acceleration = 0.3
        self.friction = 0.1
        self.turn_speed = 4
        self.off_road_friction = 0.3
        self.width = 30
        self.height = 40
        self.current_lap = 0
        self.last_checkpoint = 0
        self.checkpoint_x = x
        self.checkpoint_y = y
        self.finished = False
        self.finish_time = 0
        self.position = 0
        
    def update(self, keys=None, track=None):
        if self.is_player and keys:
            # Player controls
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.speed = min(self.speed + self.acceleration, self.max_speed)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if abs(self.speed) > 0.5:
                    self.angle -= self.turn_speed * (self.speed / self.max_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if abs(self.speed) > 0.5:
                    self.angle += self.turn_speed * (self.speed / self.max_speed)
        
        # Apply friction
        if abs(self.speed) > 0:
            friction = self.friction
            if track and not track.is_on_road(self.x, self.y):
                friction = self.off_road_friction
            
            if self.speed > 0:
                self.speed = max(0, self.speed - friction)
            else:
                self.speed = min(0, self.speed + friction)
        
        # Update position
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
    
    def respawn(self):
        self.x = self.checkpoint_x
        self.y = self.checkpoint_y
        self.speed = 0
    
    def draw(self, screen, camera_x=0, camera_y=0):
        # Create kart surface
        kart_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw kart body
        pygame.draw.rect(kart_surface, self.color, (5, 10, 20, 25))
        # Draw wheels
        pygame.draw.rect(kart_surface, BLACK, (2, 8, 6, 10))
        pygame.draw.rect(kart_surface, BLACK, (22, 8, 6, 10))
        pygame.draw.rect(kart_surface, BLACK, (2, 27, 6, 10))
        pygame.draw.rect(kart_surface, BLACK, (22, 27, 6, 10))
        # Draw driver helmet
        pygame.draw.circle(kart_surface, YELLOW, (15, 15), 6)
        
        # Rotate kart
        rotated = pygame.transform.rotate(kart_surface, -self.angle)
        rect = rotated.get_rect(center=(self.x - camera_x, self.y - camera_y))
        screen.blit(rotated, rect)

class AIKart(Kart):
    def __init__(self, x, y, color, waypoints):
        super().__init__(x, y, color, is_player=False)
        self.waypoints = waypoints
        self.current_waypoint = 0
        self.max_speed = random.uniform(5.5, 7)
        
    def update(self, keys=None, track=None):
        # AI follows waypoints
        target_x, target_y = self.waypoints[self.current_waypoint]
        
        # Calculate angle to target
        dx = target_x - self.x
        dy = target_y - self.y
        target_angle = math.degrees(math.atan2(dx, -dy))
        
        # Normalize angles
        angle_diff = target_angle - self.angle
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360
        
        # Turn towards target
        if abs(angle_diff) > 5:
            turn_amount = min(abs(angle_diff), self.turn_speed)
            if angle_diff > 0:
                self.angle += turn_amount
            else:
                self.angle -= turn_amount
        
        # Accelerate
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < 50:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
        
        self.speed = min(self.speed + self.acceleration, self.max_speed)
        
        # Update position
        super().update(None, track)

class Track:
    def __init__(self):
        # Define track as a series of points forming an oval circuit
        self.track_points = []
        self.checkpoints = []
        self.hazards = []
        self.create_track()
        
    def create_track(self):
        # Create an oval track
        center_x = 800
        center_y = 600
        
        # Outer oval
        self.outer_points = []
        for i in range(60):
            angle = (i / 60) * 2 * math.pi
            x = center_x + math.cos(angle) * 600
            y = center_y + math.sin(angle) * 400
            self.outer_points.append((x, y))
        
        # Inner oval
        self.inner_points = []
        for i in range(60):
            angle = (i / 60) * 2 * math.pi
            x = center_x + math.cos(angle) * 400
            y = center_y + math.sin(angle) * 250
            self.inner_points.append((x, y))
        
        # Create checkpoints
        num_checkpoints = 8
        for i in range(num_checkpoints):
            idx = int((i / num_checkpoints) * len(self.outer_points))
            outer = self.outer_points[idx]
            inner = self.inner_points[idx]
            self.checkpoints.append({
                'outer': outer,
                'inner': inner,
                'center': ((outer[0] + inner[0]) / 2, (outer[1] + inner[1]) / 2)
            })
        
        # Add some hazards (water/lava pools)
        self.hazards.append({'x': 1200, 'y': 500, 'radius': 60})
        self.hazards.append({'x': 500, 'y': 800, 'radius': 60})
        
    def is_on_road(self, x, y):
        # Check if point is between inner and outer track
        center_x = 800
        center_y = 600
        
        dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Approximate oval distance
        angle = math.atan2(y - center_y, x - center_x)
        outer_dist = math.sqrt((600 * math.cos(angle))**2 + (400 * math.sin(angle))**2)
        inner_dist = math.sqrt((400 * math.cos(angle))**2 + (250 * math.sin(angle))**2)
        
        return inner_dist < dist < outer_dist
    
    def is_in_hazard(self, x, y):
        for hazard in self.hazards:
            dist = math.sqrt((x - hazard['x'])**2 + (y - hazard['y'])**2)
            if dist < hazard['radius']:
                return True
        return False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        # Draw grass background
        screen.fill(GREEN)
        
        # Draw hazards (water/lava)
        for hazard in self.hazards:
            pygame.draw.circle(screen, BLUE, 
                             (int(hazard['x'] - camera_x), int(hazard['y'] - camera_y)), 
                             hazard['radius'])
        
        # Draw track (gray road)
        points = []
        for point in self.outer_points:
            points.append((point[0] - camera_x, point[1] - camera_y))
        pygame.draw.polygon(screen, GRAY, points)
        
        points = []
        for point in self.inner_points:
            points.append((point[0] - camera_x, point[1] - camera_y))
        pygame.draw.polygon(screen, GREEN, points)
        
        # Draw road markings
        for i in range(len(self.outer_points)):
            if i % 3 == 0:
                p1 = self.outer_points[i]
                pygame.draw.circle(screen, WHITE, 
                                 (int(p1[0] - camera_x), int(p1[1] - camera_y)), 3)
        
        # Draw checkpoints (semi-transparent)
        for i, cp in enumerate(self.checkpoints):
            color = YELLOW if i == 0 else WHITE
            p1 = (cp['outer'][0] - camera_x, cp['outer'][1] - camera_y)
            p2 = (cp['inner'][0] - camera_x, cp['inner'][1] - camera_y)
            pygame.draw.line(screen, color, p1, p2, 3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Kart Racing Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.state = GameState.MENU
        self.total_laps = 3
        self.game_time = 0
        
        self.track = Track()
        self.reset_game()
        
    def reset_game(self):
        # Create player kart
        start_x, start_y = self.track.checkpoints[0]['center']
        self.player = Kart(start_x, start_y - 50, RED, is_player=True)
        self.player.checkpoint_x = start_x
        self.player.checkpoint_y = start_y - 50
        
        # Create AI waypoints
        waypoints = [cp['center'] for cp in self.track.checkpoints]
        
        # Create AI karts
        self.ai_karts = [
            AIKart(start_x - 40, start_y - 50, BLUE, waypoints),
            AIKart(start_x + 40, start_y - 50, ORANGE, waypoints),
            AIKart(start_x - 40, start_y - 90, GREEN, waypoints)
        ]
        
        for ai in self.ai_karts:
            ai.checkpoint_x = ai.x
            ai.checkpoint_y = ai.y
        
        self.all_karts = [self.player] + self.ai_karts
        self.game_time = 0
        
    def check_checkpoint_collision(self, kart):
        next_checkpoint = (kart.last_checkpoint + 1) % len(self.track.checkpoints)
        cp = self.track.checkpoints[next_checkpoint]
        
        # Check if kart crosses checkpoint line
        outer = cp['outer']
        inner = cp['inner']
        
        # Simple distance check
        dist = math.sqrt((kart.x - cp['center'][0])**2 + (kart.y - cp['center'][1])**2)
        
        if dist < 80:
            kart.last_checkpoint = next_checkpoint
            kart.checkpoint_x = kart.x
            kart.checkpoint_y = kart.y
            
            # Check if completed lap
            if next_checkpoint == 0 and kart.current_lap < self.total_laps:
                kart.current_lap += 1
                if kart.current_lap == self.total_laps and not kart.finished:
                    kart.finished = True
                    kart.finish_time = self.game_time
    
    def update_positions(self):
        # Calculate positions based on laps and checkpoints
        def get_progress(kart):
            return kart.current_lap * len(self.track.checkpoints) + kart.last_checkpoint
        
        sorted_karts = sorted(self.all_karts, key=get_progress, reverse=True)
        for i, kart in enumerate(sorted_karts):
            kart.position = i + 1
    
    def draw_menu(self):
        self.screen.fill(DARK_GREEN)
        
        title = self.font.render("KART RACING", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        
        start_text = self.font.render("Press SPACE to Start", True, WHITE)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 350))
        
        controls = [
            "Controls:",
            "Arrow Keys or WASD - Move",
            "R - Reset Race",
            "P - Pause",
            "ESC - Menu"
        ]
        
        y = 450
        for line in controls:
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 30
    
    def draw_ui(self):
        # Semi-transparent background for UI
        ui_bg = pygame.Surface((300, 150))
        ui_bg.set_alpha(200)
        ui_bg.fill(BLACK)
        self.screen.blit(ui_bg, (10, 10))
        
        # Position
        pos_text = self.font.render(f"Position: {self.player.position}/{len(self.all_karts)}", 
                                   True, YELLOW)
        self.screen.blit(pos_text, (20, 20))
        
        # Lap
        lap_text = self.font.render(f"Lap: {self.player.current_lap}/{self.total_laps}", 
                                   True, WHITE)
        self.screen.blit(lap_text, (20, 60))
        
        # Speed
        speed_text = self.small_font.render(f"Speed: {abs(self.player.speed):.1f}", 
                                           True, WHITE)
        self.screen.blit(speed_text, (20, 100))
        
        # Time
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = self.small_font.render(f"Time: {minutes:02d}:{seconds:02d}", 
                                          True, WHITE)
        self.screen.blit(time_text, (20, 130))
        
        # Minimap
        self.draw_minimap()
    
    def draw_minimap(self):
        minimap_size = 150
        minimap_x = SCREEN_WIDTH - minimap_size - 10
        minimap_y = 10
        
        # Background
        minimap_bg = pygame.Surface((minimap_size, minimap_size))
        minimap_bg.set_alpha(200)
        minimap_bg.fill(DARK_GRAY)
        self.screen.blit(minimap_bg, (minimap_x, minimap_y))
        
        # Scale factor
        scale = minimap_size / 1400
        offset_x = 200
        offset_y = 200
        
        # Draw track outline
        for point in self.track.outer_points[::5]:
            x = int((point[0] - offset_x) * scale) + minimap_x
            y = int((point[1] - offset_y) * scale) + minimap_y
            pygame.draw.circle(self.screen, GRAY, (x, y), 2)
        
        # Draw karts
        for kart in self.all_karts:
            x = int((kart.x - offset_x) * scale) + minimap_x
            y = int((kart.y - offset_y) * scale) + minimap_y
            color = kart.color if kart != self.player else YELLOW
            pygame.draw.circle(self.screen, color, (x, y), 3)
    
    def draw_finish_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.player.finished:
            title = self.font.render("RACE FINISHED!", True, YELLOW)
            pos_text = self.font.render(f"You finished {self.player.position}!", 
                                       True, WHITE)
        else:
            title = self.font.render("RACE FINISHED!", True, RED)
            pos_text = self.font.render("You didn't finish in time!", True, WHITE)
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 250))
        self.screen.blit(pos_text, (SCREEN_WIDTH // 2 - pos_text.get_width() // 2, 320))
        
        # Show all finishers
        y = 400
        for kart in sorted([k for k in self.all_karts if k.finished], 
                          key=lambda k: k.finish_time):
            minutes = int(kart.finish_time // 60)
            seconds = int(kart.finish_time % 60)
            name = "YOU" if kart == self.player else f"AI {kart.color}"
            text = self.small_font.render(
                f"{kart.position}. {name} - {minutes:02d}:{seconds:02d}", 
                True, YELLOW if kart == self.player else WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 35
        
        restart = self.font.render("Press SPACE to restart", True, WHITE)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 600))
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.MENU
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING
                    
                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif self.state == GameState.FINISHED:
                            self.reset_game()
                            self.state = GameState.PLAYING
                    
                    if event.key == pygame.K_p and self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_p and self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    
                    if event.key == pygame.K_r and self.state == GameState.PLAYING:
                        self.reset_game()
            
            if self.state == GameState.MENU:
                self.draw_menu()
            
            elif self.state == GameState.PLAYING:
                self.game_time += dt
                
                keys = pygame.key.get_pressed()
                
                # Update player
                self.player.update(keys, self.track)
                
                # Check if player is in hazard
                if self.track.is_in_hazard(self.player.x, self.player.y):
                    self.player.respawn()
                
                # Update AI
                for ai in self.ai_karts:
                    ai.update(None, self.track)
                    if self.track.is_in_hazard(ai.x, ai.y):
                        ai.respawn()
                
                # Check checkpoints
                for kart in self.all_karts:
                    self.check_checkpoint_collision(kart)
                
                # Update positions
                self.update_positions()
                
                # Check if race is finished
                finished_count = sum(1 for k in self.all_karts if k.finished)
                if finished_count == len(self.all_karts) or self.game_time > 300:
                    self.state = GameState.FINISHED
                
                # Camera follows player
                camera_x = self.player.x - SCREEN_WIDTH // 2
                camera_y = self.player.y - SCREEN_HEIGHT // 2
                
                # Draw everything
                self.track.draw(self.screen, camera_x, camera_y)
                
                for kart in sorted(self.all_karts, key=lambda k: k.y):
                    kart.draw(self.screen, camera_x, camera_y)
                
                self.draw_ui()
            
            elif self.state == GameState.PAUSED:
                # Draw game state underneath
                camera_x = self.player.x - SCREEN_WIDTH // 2
                camera_y = self.player.y - SCREEN_HEIGHT // 2
                self.track.draw(self.screen, camera_x, camera_y)
                for kart in self.all_karts:
                    kart.draw(self.screen, camera_x, camera_y)
                self.draw_ui()
                
                # Draw pause overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                pause_text = self.font.render("PAUSED", True, YELLOW)
                self.screen.blit(pause_text, 
                               (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 - 50))
                
                continue_text = self.small_font.render("Press P to continue", True, WHITE)
                self.screen.blit(continue_text, 
                               (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 + 20))
            
            elif self.state == GameState.FINISHED:
                camera_x = self.player.x - SCREEN_WIDTH // 2
                camera_y = self.player.y - SCREEN_HEIGHT // 2
                self.track.draw(self.screen, camera_x, camera_y)
                for kart in self.all_karts:
                    kart.draw(self.screen, camera_x, camera_y)
                
                self.draw_finish_screen()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()