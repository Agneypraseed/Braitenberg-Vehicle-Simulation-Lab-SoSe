import pygame
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 3c Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

# Stimuli sources
stimuli = [
    {"pos": pygame.math.Vector2(200, 200), "color": YELLOW, "type": "light"},
    {"pos": pygame.math.Vector2(600, 150), "color": RED, "type": "heat"},
    {"pos": pygame.math.Vector2(200, 500), "color": BLUE, "type": "oxygen"},
    {"pos": pygame.math.Vector2(600, 450), "color": GREEN, "type": "organic"}
]

class Vehicle:
    def __init__(self, pos, angle):
        self.pos = pygame.math.Vector2(pos)
        self.angle = angle
        self.radius = 25
        self.sensor_offset = 35
        self.sensor_spacing = 40
        self.speed_scale = 300
        self.rotation_scale = 0.003

    def get_sensor_positions(self):
        forward = pygame.math.Vector2(0, -1).rotate(self.angle)
        right = forward.rotate(90)
        left_sensor = self.pos + forward * self.sensor_offset - right * (self.sensor_spacing / 2)
        right_sensor = self.pos + forward * self.sensor_offset + right * (self.sensor_spacing / 2)
        return left_sensor, right_sensor

    def move(self, stimuli):
        speed_l = 0
        speed_r = 0

        # Get sensor positions
        left_sensor, right_sensor = self.get_sensor_positions()

        for stim in stimuli:
            s_pos = stim["pos"]
            s_type = stim["type"]

            l_dist = max(1, left_sensor.distance_to(s_pos))
            r_dist = max(1, right_sensor.distance_to(s_pos))

            # Influence drops with distance (1/d)
            l_signal = 1 / l_dist
            r_signal = 1 / r_dist

            # Apply different connection schemes
            if s_type == "light":
                # Uncrossed excitatory
                speed_l += l_signal
                speed_r += r_signal
            elif s_type == "heat":
                # Crossed excitatory
                speed_l += r_signal
                speed_r += l_signal
            elif s_type == "oxygen":
                # Crossed inhibitory
                speed_l -= r_signal
                speed_r -= l_signal
            elif s_type == "organic":
                # Uncrossed inhibitory
                speed_l -= l_signal
                speed_r -= r_signal

        # Clip speed
        speed_l = max(0, speed_l)
        speed_r = max(0, speed_r)

        # Compute movement
        speed = (speed_l + speed_r) / 2 * self.speed_scale / 100
        rotation = (speed_r - speed_l) * self.rotation_scale * self.speed_scale

        self.angle += math.degrees(rotation)
        direction = pygame.math.Vector2(0, -1).rotate(self.angle)
        self.pos += direction * speed

        # Wrap screen
        self.pos.x %= WIDTH
        self.pos.y %= HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, PURPLE, self.pos, self.radius)
        left_sensor, right_sensor = self.get_sensor_positions()
        pygame.draw.circle(surface, CYAN, left_sensor, 5)
        pygame.draw.circle(surface, CYAN, right_sensor, 5)

        label = font.render("Vehicle 3c", True, WHITE)
        surface.blit(label, (10, 10))


# Main loop
vehicle = Vehicle((400, 300), 0)
running = True

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw stimuli
    for s in stimuli:
        pygame.draw.circle(screen, s["color"], (int(s["pos"].x), int(s["pos"].y)), 20)

    # Update vehicle
    vehicle.move(stimuli)
    vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
