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

# Palette & Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ASPHALT = (50, 50, 55)
GRASS_LIGHT = (0, 120, 0)
DIRT = (101, 67, 33)
RED_KERB = (200, 0, 0)
WHITE_KERB = (220, 220, 220)
WATER_MAIN = (0, 119, 190)
WATER_HIGHLIGHT = (50, 150, 220)
LAVA_MAIN = (207, 16, 32)
LAVA_CORE = (255, 80, 0)
UI_BG = (20, 20, 20)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    # Removed "FINISHED" state because we want the game to keep running
    # We will handle the game-over screen as an overlay in PLAYING

class Kart:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.angle = 90
        self.speed = 0
        self.color = color
        self.is_player = is_player
        
        # Stats
        self.base_max_speed = 9.5 if is_player else 8.2
        self.current_max_speed = self.base_max_speed
        self.acceleration = 0.2
        self.friction = 0.06
        self.turn_speed = 4.5
        
        self.width = 30
        self.height = 40
        
        # Race State
        self.current_lap = 1
        self.last_checkpoint = 0
        self.finished = False
        self.finish_time = 0
        self.position = 0
        
        self.invincible_timer = 0
        
    def update(self, keys=None, track=None, all_karts=None):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # -- FINISH LINE BEHAVIOR --
        # If finished, ignore inputs and brake to a stop
        if self.finished:
            if self.speed > 0:
                self.speed -= 0.15 # Strong braking
                if self.speed < 0: self.speed = 0
            elif self.speed < 0:
                self.speed += 0.15
                if self.speed > 0: self.speed = 0
                
            # Move slightly to simulate momentum
            rad = math.radians(self.angle)
            self.x += self.speed * math.sin(rad)
            self.y -= self.speed * math.cos(rad)
            return

        # Check surface type
        on_road = track.is_on_road(self.x, self.y) if track else True
        
        if on_road:
            self.current_max_speed = self.base_max_speed
        else:
            # Grass slowdown
            self.current_max_speed = 3.0
            if self.speed > 3.0:
                self.speed *= 0.95

        if self.is_player and keys:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if self.speed < self.current_max_speed:
                    self.speed += self.acceleration
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.speed -= self.acceleration
            
            if abs(self.speed) > 0.5:
                direction = 1 if self.speed > 0 else -1
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.angle -= self.turn_speed * direction
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.angle += self.turn_speed * direction
        
        # Cap speed
        if self.speed > self.current_max_speed:
            self.speed -= 0.1 
            
        # Friction
        if self.speed > 0:
            self.speed = max(0, self.speed - self.friction)
        elif self.speed < 0:
            self.speed = min(0, self.speed + self.friction)
        
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
    
    def respawn(self, track_checkpoints):
        # Don't respawn if race is over for this kart
        if self.finished: return

        safe_point = track_checkpoints[self.last_checkpoint]['center']
        self.x = safe_point[0]
        self.y = safe_point[1]
        self.speed = 0
        
        # Face next checkpoint
        next_idx = (self.last_checkpoint + 1) % len(track_checkpoints)
        next_point = track_checkpoints[next_idx]['center']
        dx = next_point[0] - self.x
        dy = next_point[1] - self.y
        self.angle = math.degrees(math.atan2(dx, -dy))
        
        self.invincible_timer = 120 
    
    def draw(self, screen, camera_x=0, camera_y=0):
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return

        kart_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Tires
        pygame.draw.rect(kart_surface, (20, 20, 20), (0, 5, 8, 12))   
        pygame.draw.rect(kart_surface, (20, 20, 20), (22, 5, 8, 12))  
        pygame.draw.rect(kart_surface, (20, 20, 20), (0, 25, 8, 12))  
        pygame.draw.rect(kart_surface, (20, 20, 20), (22, 25, 8, 12)) 
        
        # Body
        pygame.draw.rect(kart_surface, self.color, (6, 10, 18, 26), border_radius=5)
        
        # Driver/Helmet
        pygame.draw.circle(kart_surface, (255, 220, 0), (15, 20), 7)
        
        rotated = pygame.transform.rotate(kart_surface, -self.angle)
        rect = rotated.get_rect(center=(int(self.x - camera_x), int(self.y - camera_y)))
        screen.blit(rotated, rect)

class AIKart(Kart):
    def __init__(self, x, y, color, waypoints):
        super().__init__(x, y, color, is_player=False)
        self.waypoints = waypoints
        self.current_waypoint = 0
        self.lane_offset = random.uniform(-40, 40)
        
    def update(self, keys=None, track=None, all_karts=None):
        if self.finished:
            super().update(keys, track, all_karts) # Call parent to handle braking
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
        on_road = track.is_on_road(self.x, self.y) if track else True
        self.current_max_speed = self.base_max_speed if on_road else 3.0

        # AI Targeting Logic
        tx, ty = self.waypoints[self.current_waypoint]
        
        dist_to_target = math.sqrt((tx - self.x)**2 + (ty - self.y)**2)
        offset_strength = min(1.0, dist_to_target / 300.0) 
        
        target_x = tx + (math.cos(math.radians(self.current_waypoint * 10)) * self.lane_offset * offset_strength)
        target_y = ty + (math.sin(math.radians(self.current_waypoint * 10)) * self.lane_offset * offset_strength)
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        target_angle = math.degrees(math.atan2(dx, -dy))
        diff = (target_angle - self.angle + 180) % 360 - 180
        
        if dist < 200:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)

        avoid_turn = 0
        
        # Avoid other karts
        if all_karts:
            for other in all_karts:
                if other != self and not other.finished:
                    d = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
                    if d < 70:
                        push_angle = math.degrees(math.atan2(self.x - other.x, -(self.y - other.y)))
                        a_diff = (push_angle - self.angle + 180) % 360 - 180
                        avoid_turn += a_diff * (50 / max(d, 1))
        
        # Simple Hazard Avoidance
        if track:
            for hazard in track.hazards:
                h_dist = math.sqrt((self.x - hazard['x'])**2 + (self.y - hazard['y'])**2)
                if h_dist < hazard['radius'] + 100:
                    avoid_angle = math.degrees(math.atan2(self.x - hazard['x'], -(self.y - hazard['y'])))
                    a_diff = (avoid_angle - self.angle + 180) % 360 - 180
                    avoid_turn += a_diff * 2

        final_turn = diff + max(min(avoid_turn, 40), -40)

        # Steering
        if abs(final_turn) > 2:
            turn_amt = min(abs(final_turn), self.turn_speed)
            if final_turn > 0: self.angle += turn_amt
            else: self.angle -= turn_amt
        
        # Throttle
        target_speed = self.current_max_speed
        if abs(diff) > 30: target_speed *= 0.6
        if abs(diff) > 60: target_speed *= 0.4
        
        if self.speed < target_speed:
            self.speed += self.acceleration
        elif self.speed > target_speed:
            self.speed -= 0.1
            
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)

class Track:
    def __init__(self):
        self.track_points = []
        self.checkpoints = []
        self.hazards = []
        self.centerline = []
        self.outer_points = []
        self.inner_points = []
        self.create_track()
        
    def create_track(self):
        self.centerline = [
            (500, 400), (500, 600), (500, 800), # START
            (550, 950), (700, 1050), (900, 1100), # TURN 1
            (1100, 1080), (1300, 1000), (1500, 850), # STRAIGHT
            (1600, 700), (1600, 500), # TURN 2
            (1500, 350), (1300, 250), (1100, 200), (900, 200), (700, 200), # TOP CURVE
            (600, 300), 
        ]
        
        track_width = 130
        
        for i in range(len(self.centerline)):
            curr = self.centerline[i]
            next_pt = self.centerline[(i + 1) % len(self.centerline)]
            prev_pt = self.centerline[(i - 1) % len(self.centerline)]
            
            dx = next_pt[0] - prev_pt[0]
            dy = next_pt[1] - prev_pt[1]
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                perp_x = -dy / length
                perp_y = dx / length
            else:
                perp_x, perp_y = 0, 1
            
            self.outer_points.append((curr[0] + perp_x * track_width, curr[1] + perp_y * track_width))
            self.inner_points.append((curr[0] - perp_x * track_width, curr[1] - perp_y * track_width))
        
        # Checkpoints
        num_checkpoints = 18
        for i in range(num_checkpoints):
            idx = int((i / num_checkpoints) * len(self.centerline))
            self.checkpoints.append({
                'center': self.centerline[idx],
                'idx': idx
            })
        
        # Hazards - UPDATED LOCATIONS (ON ROAD)
        # Note: Centerline points are approx:
        # Straight: (1300, 1000)
        # Top Curve: (900, 200)
        self.hazards = [
            # Water on the grass (optional decoration)
            {'x': 400, 'y': 1050, 'radius': 85, 'type': 'water'},
            
            # LAVA ON THE TRACK - Mid Straight
            {'x': 1300, 'y': 1000, 'radius': 60, 'type': 'lava'},
            
            # WATER ON THE TRACK - Top Curve Apex
            {'x': 1100, 'y': 200, 'radius': 55, 'type': 'water'},
            
            # LAVA ON THE TRACK - Before Finish
            {'x': 650, 'y': 350, 'radius': 50, 'type': 'lava'},
        ]
        
    def is_on_road(self, x, y):
        def point_in_poly(x, y, poly):
            n = len(poly)
            inside = False
            p1x, p1y = poly[0]
            for i in range(n + 1):
                p2x, p2y = poly[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            return inside
        return point_in_poly(x, y, self.outer_points) and not point_in_poly(x, y, self.inner_points)
    
    def draw(self, screen, camera_x, camera_y):
        # 1. Background
        screen.fill(GRASS_LIGHT)
        
        # 2. Track Segments
        N = len(self.centerline)
        
        # Dirt Shoulder
        for i in range(N):
            next_i = (i + 1) % N
            p1_out = (self.outer_points[i][0] - camera_x, self.outer_points[i][1] - camera_y)
            p2_out = (self.outer_points[next_i][0] - camera_x, self.outer_points[next_i][1] - camera_y)
            p2_in = (self.inner_points[next_i][0] - camera_x, self.inner_points[next_i][1] - camera_y)
            p1_in = (self.inner_points[i][0] - camera_x, self.inner_points[i][1] - camera_y)
            pygame.draw.polygon(screen, DIRT, [p1_out, p2_out, p2_in, p1_in], width=10)

        # Asphalt Road
        for i in range(N):
            next_i = (i + 1) % N
            p1_out = (self.outer_points[i][0] - camera_x, self.outer_points[i][1] - camera_y)
            p2_out = (self.outer_points[next_i][0] - camera_x, self.outer_points[next_i][1] - camera_y)
            p2_in = (self.inner_points[next_i][0] - camera_x, self.inner_points[next_i][1] - camera_y)
            p1_in = (self.inner_points[i][0] - camera_x, self.inner_points[i][1] - camera_y)
            
            pygame.draw.polygon(screen, ASPHALT, [p1_out, p2_out, p2_in, p1_in])
            
            kerb_color = RED_KERB if (i // 2) % 2 == 0 else WHITE_KERB
            pygame.draw.line(screen, kerb_color, p1_out, p2_out, 8)
            pygame.draw.line(screen, kerb_color, p1_in, p2_in, 8)
            
        # 3. Start/Finish Line - DRAWN EXPLICITLY ON INDEX 0
        # This matches the logical starting checkpoint exactly
        sx_out, sy_out = self.outer_points[0]
        sx_in, sy_in = self.inner_points[0]
        
        steps = 8
        for j in range(steps):
            t1 = j / steps
            t2 = (j + 1) / steps
            lx1 = sx_out + (sx_in - sx_out) * t1 - camera_x
            ly1 = sy_out + (sy_in - sy_out) * t1 - camera_y
            lx2 = sx_out + (sx_in - sx_out) * t2 - camera_x
            ly2 = sy_out + (sy_in - sy_out) * t2 - camera_y
            
            col = WHITE if j % 2 == 0 else BLACK
            pygame.draw.polygon(screen, col, [(lx1, ly1), (lx2, ly2), (lx2+4, ly2), (lx1+4, ly1)])

        # 4. Hazards
        for hazard in self.hazards:
            x = int(hazard['x'] - camera_x)
            y = int(hazard['y'] - camera_y)
            r = hazard['radius']
            
            if hazard['type'] == 'water':
                pygame.draw.circle(screen, (200, 200, 255), (x, y), r + 5, 2)
                pygame.draw.circle(screen, WATER_MAIN, (x, y), r)
                pygame.draw.circle(screen, WATER_HIGHLIGHT, (x - r//3, y - r//3), r//4)
            else:
                pygame.draw.circle(screen, (100, 0, 0), (x, y), r + 5, 2)
                pygame.draw.circle(screen, LAVA_MAIN, (x, y), r)
                pygame.draw.circle(screen, LAVA_CORE, (x, y), int(r * 0.7))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Kart Racing")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)
        self.title_font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 28)
        self.state = GameState.MENU
        self.total_laps = 3
        self.track = Track()
        self.reset_game()
        
    def reset_game(self):
        start_cp = self.track.centerline[0]
        next_cp = self.track.centerline[1]
        
        angle = math.degrees(math.atan2(next_cp[0] - start_cp[0], -(next_cp[1] - start_cp[1])))
        
        self.player = Kart(start_cp[0] - 30, start_cp[1], (220, 20, 60), is_player=True)
        self.player.angle = angle
        
        waypoints = self.track.centerline
        self.ai_karts = [
            AIKart(start_cp[0] + 30, start_cp[1], (30, 144, 255), waypoints),
            AIKart(start_cp[0] - 30, start_cp[1] + 60, (255, 140, 0), waypoints),
            AIKart(start_cp[0] + 30, start_cp[1] + 60, (128, 0, 128), waypoints)
        ]
        for ai in self.ai_karts: ai.angle = angle
        
        self.all_karts = [self.player] + self.ai_karts
        self.game_time = 0
        
    def check_checkpoints(self, kart):
        # Don't check if already finished
        if kart.finished: return

        next_idx = (kart.last_checkpoint + 1) % len(self.track.checkpoints)
        cp_data = self.track.checkpoints[next_idx]
        cp_pos = cp_data['center']
        
        dist = math.sqrt((kart.x - cp_pos[0])**2 + (kart.y - cp_pos[1])**2)
        
        if dist < 200:
            kart.last_checkpoint = next_idx
            if next_idx == 0:
                kart.current_lap += 1
                if kart.current_lap > self.total_laps:
                    kart.finished = True
                    # Record time immediately
                    kart.finish_time = self.game_time
    
    def update_positions(self):
        def get_score(k):
            if k.finished:
                # Finished karts are ranked by time (lower is better, so negative time)
                return 99999999 - k.finish_time
            
            # Unfinished karts ranked by distance
            next_idx = (k.last_checkpoint + 1) % len(self.track.checkpoints)
            next_cp = self.track.checkpoints[next_idx]['center']
            dist = math.sqrt((k.x - next_cp[0])**2 + (k.y - next_cp[1])**2)
            return (k.current_lap * 100000) + (k.last_checkpoint * 1000) - dist
            
        sorted_karts = sorted(self.all_karts, key=get_score, reverse=True)
        for i, k in enumerate(sorted_karts):
            k.position = i + 1

    def draw_menu(self):
        self.screen.fill(UI_BG)
        pygame.draw.rect(self.screen, RED_KERB, (0, 100, SCREEN_WIDTH, 100))
        pygame.draw.rect(self.screen, WHITE, (0, 110, SCREEN_WIDTH, 5))
        pygame.draw.rect(self.screen, WHITE, (0, 185, SCREEN_WIDTH, 5))
        
        title = self.title_font.render("SUPER KART RACING", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))
        
        sub = self.font.render("LAVA EDITION", True, (255, 80, 0))
        self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 220))
        
        hint = self.font.render("PRESS [SPACE] TO START", True, (0, 255, 0))
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 500))

    def draw_results_overlay(self):
        # Draw a semi-transparent dark panel on the left side
        panel = pygame.Surface((400, SCREEN_HEIGHT))
        panel.set_alpha(220)
        panel.fill(BLACK)
        self.screen.blit(panel, (0, 0))
        
        txt = "VICTORY!" if self.player.position == 1 else "FINISHED!"
        col = (255, 215, 0) if self.player.position == 1 else WHITE
        
        title = self.title_font.render(txt, True, col)
        self.screen.blit(title, (200 - title.get_width()//2, 50))
        
        # Leaderboard
        sorted_karts = sorted(self.all_karts, key=lambda k: k.finish_time if k.finished else 999999)
        
        for i, k in enumerate(sorted_karts):
            name = "PLAYER" if k.is_player else f"CPU {i+1}"
            
            if k.finished:
                m = int(k.finish_time // 60)
                s = int(k.finish_time % 60)
                ms = int((k.finish_time * 100) % 100)
                t_str = f"{m:02d}:{s:02d}.{ms:02d}"
            else:
                t_str = "DRIVING..."
                
            color = k.color
            # Highlight player row
            if k.is_player:
                pygame.draw.rect(self.screen, (50, 50, 50), (10, 150 + i * 60 - 5, 380, 40))
                
            row_txt = f"{i+1}. {name}"
            time_txt = t_str
            
            r1 = self.font.render(row_txt, True, color)
            r2 = self.font.render(time_txt, True, WHITE)
            
            self.screen.blit(r1, (20, 150 + i * 60))
            self.screen.blit(r2, (220, 150 + i * 60))
            
        hint = self.small_font.render("Press [SPACE] to Restart", True, (150, 150, 150))
        self.screen.blit(hint, (200 - hint.get_width()//2, 600))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif self.state == GameState.PLAYING and self.player.finished:
                             # Allow restart only if player is finished
                            self.reset_game()
                    if event.key == pygame.K_r and self.state == GameState.PLAYING:
                        self.reset_game()
            
            if self.state == GameState.MENU:
                self.draw_menu()
                
            elif self.state == GameState.PLAYING:
                # Timer only stops for UI display, logic tracks individual finish times
                if not self.player.finished:
                    self.game_time += dt
                else:
                    # If player finished, we still increment a background timer for AI
                    self.game_time += dt

                keys = pygame.key.get_pressed()
                
                # Update ALL karts (Player brakes if finished, AI keeps going)
                self.player.update(keys, self.track)
                
                # Check hazards for player
                if not self.player.finished:
                    for haz in self.track.hazards:
                        dist = math.sqrt((self.player.x - haz['x'])**2 + (self.player.y - haz['y'])**2)
                        if dist < haz['radius'] * 0.8:
                            self.player.respawn(self.track.checkpoints)

                # Update AI
                for ai in self.ai_karts:
                    ai.update(None, self.track, self.all_karts)
                    if not ai.finished:
                        for haz in self.track.hazards:
                            dist = math.sqrt((ai.x - haz['x'])**2 + (ai.y - haz['y'])**2)
                            if dist < haz['radius'] * 0.8:
                                ai.respawn(self.track.checkpoints)
                
                # Check Checkpoints & Laps
                for k in self.all_karts:
                    self.check_checkpoints(k)
                
                self.update_positions()
                
                # Drawing
                cam_x = int(self.player.x - SCREEN_WIDTH // 2)
                cam_y = int(self.player.y - SCREEN_HEIGHT // 2)
                
                self.track.draw(self.screen, cam_x, cam_y)
                
                # Draw shadows
                for k in self.all_karts:
                    shadow = pygame.Surface((k.width, k.height), pygame.SRCALPHA)
                    pygame.draw.rect(shadow, (0,0,0,100), (0,0,k.width, k.height), border_radius=5)
                    rot_shadow = pygame.transform.rotate(shadow, -k.angle)
                    s_rect = rot_shadow.get_rect(center=(int(k.x - cam_x + 5), int(k.y - cam_y + 5)))
                    self.screen.blit(rot_shadow, s_rect)

                # Draw Karts
                for k in sorted(self.all_karts, key=lambda x: x.y):
                    k.draw(self.screen, cam_x, cam_y)
                
                # Draw UI
                if not self.player.finished:
                    # Standard Race HUD
                    hud_surface = pygame.Surface((220, 120), pygame.SRCALPHA)
                    pygame.draw.rect(hud_surface, (0, 0, 0, 150), (0, 0, 220, 120), border_radius=10)
                    self.screen.blit(hud_surface, (20, 20))
                    
                    pos_color = (255, 215, 0) if self.player.position == 1 else WHITE
                    t1 = self.font.render(f"POS: {self.player.position}/4", True, pos_color)
                    t2 = self.font.render(f"LAP: {self.player.current_lap}/{self.total_laps}", True, WHITE)
                    
                    mins = int(self.game_time // 60)
                    secs = int(self.game_time % 60)
                    ms = int((self.game_time * 100) % 100)
                    t3 = self.font.render(f"{mins:02d}:{secs:02d}.{ms:02d}", True, WHITE)
                    
                    self.screen.blit(t1, (35, 30))
                    self.screen.blit(t2, (35, 65))
                    self.screen.blit(t3, (35, 100))
                else:
                    # Results Overlay (Game continues in background)
                    self.draw_results_overlay()
                
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
