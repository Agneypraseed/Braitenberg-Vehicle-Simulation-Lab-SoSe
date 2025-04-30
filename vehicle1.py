import pygame
import sys
import math
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 1 Simulation")
clock = pygame.time.Clock()
fps = 60

# Environment: temperature source at center
CENTER = (WIDTH // 2, HEIGHT // 2)


def temperature_at(pos):
    dx, dy = pos[0] - CENTER[0], pos[1] - CENTER[1]
    distance = math.sqrt(dx**2 + dy**2)
    max_dist = math.sqrt((WIDTH//2)**2 + (HEIGHT//2)**2)
    # Normalized temperature : 1 at center, 0 at corners
    temp = max(0, 1-distance/max_dist)
    return temp


class Vehicle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.angle = random.uniform(0, 2*math.pi)  # Random angle in radians
        self.base_speed = 200   # maximum speed per second
        self.radius = 20

    def update(self, dt):
        temp = temperature_at(self.pos)
        # Adjust speed based on temperature
        speed = self.base_speed * temp

        self.angle += random.uniform(-0.1, 0.1)*dt  # Random turn

        dx = speed * math.cos(self.angle) * dt
        dy = speed * math.sin(self.angle) * dt

        # if speed > 10:
        self.pos.x += dx
        self.pos.y += dy

        # Wrap around the screen/ Keep within bounds
        self.pos.x = max(self.radius, min(WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(HEIGHT - self.radius, self.pos.y))

    def draw(self, surface):
        # Draw the vehicle as a circle
        pygame.draw.circle(surface, (0, 0, 255), (int(
            self.pos.x), int(self.pos.y)), self.radius)
        end_x = self.pos.x + self.radius * math.cos(self.angle)
        end_y = self.pos.y + self.radius * math.sin(self.angle)
        # Draw the direction vector
        pygame.draw.line(surface, (255, 255, 255), self.pos, (end_x, end_y), 2)


vehicle = Vehicle(100, 100)


while True:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    vehicle.update(dt)

    for y in range(0, HEIGHT, 5):
        for x in range(0, WIDTH, 5):
            t = temperature_at((x, y))
            color = (int(255 * t), 0, 0)  # red intensity = temperature
            pygame.draw.rect(screen, color, pygame.Rect(x, y, 5, 5))

    vehicle.draw(screen)

    pygame.display.flip()
    screen.fill((0, 0, 0))
