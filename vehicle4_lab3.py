import random
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 4 Simulation")

pygame.font.init()
font = pygame.font.SysFont("Arial", 24)

clock = pygame.time.Clock()
fps = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

FRICTION = True
INHIBITION = True
CROSS = False


def inverse_distance(distance):
    if distance == 0:
        return float('inf')  # Avoid division by zero
    return 1 / distance


def threshold(d):
    return inverse_distance(d) if d > 150 else 0


class Circle:
    def __init__(self, position, radius=30, color=RED):
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class Vehicle:
    def __init__(self, position, direction, radius=50, color=RED):
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color
        self.speed_scalling = 100
        self.rotation_scalling = 5

        # sensor
        self.sensor_radius = 15
        self.sensor_spacing = 50
        self.sensor_offset = self.radius + self.sensor_radius

        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        right_direction = forward_direction.rotate(-90)

        self.left_sensor_position = self.position + forward_direction * \
            self.sensor_offset - right_direction * (self.sensor_spacing/2)
        self.right_sensor_position = self.position + forward_direction * \
            self.sensor_offset + right_direction * (self.sensor_spacing/2)

        self.sensor_color = GREEN

    def update_direction(self):
        self.direction += random.randint(-5, 5)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

        pygame.draw.circle(surface, self.sensor_color,
                           self.left_sensor_position, self.sensor_radius)

        pygame.draw.circle(surface, self.sensor_color,
                           self.right_sensor_position, self.sensor_radius)

    def calculate_sensor_position(self, sun_position):
        return self.position.distance_to(sun_position)

    def move(self, sun_position):

        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        right_direction = forward_direction.rotate(-90)

        left_distance = self.left_sensor_position.distance_to(sun_position)
        right_distance = self.right_sensor_position.distance_to(sun_position)

        left_speed = self.speed_scalling * threshold(left_distance)
        right_speed = self.speed_scalling * threshold(right_distance)

        speed = (left_speed + right_speed) / 2  # Average speed

        if INHIBITION:
            speed = 1 - speed

        rotation = (right_speed - left_speed) * \
            self.rotation_scalling
        if CROSS:
            rotation *= -1

        self.direction += rotation
        direction = pygame.math.Vector2(0, -1).rotate(self.direction)

        self.position += direction * speed

        # Screen Wrapping
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

        self.left_sensor_position = self.position + forward_direction * \
            self.sensor_offset + right_direction * (self.sensor_spacing/2)

        self.right_sensor_position = self.position + forward_direction * \
            self.sensor_offset - right_direction * (self.sensor_spacing/2)

        if FRICTION:
            self.update_direction()

        # debug/print info
        # text = font.render(
        #     f"Left Distance to sun: {left_distance:.2f} Right Distance to sun: {right_distance:.2f} Speed: {speed:.2f}", True, WHITE)
        # screen.blit(text, (10, 10))
        text1 = font.render(
            f"Cross: {CROSS} | Inhibition: {INHIBITION} | Friction: {FRICTION}",
            True, WHITE)
        text2 = font.render(
            f"Left Distance: {left_distance:.2f} Right Distance: {right_distance:.2f} Speed: {speed:.2f}",
            True, WHITE)

        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 40))


sun = Circle((WIDTH//2, HEIGHT//2), radius=30, color=YELLOW)
vehicle = Vehicle((300, 500), 45)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                CROSS = not CROSS
            elif event.key == pygame.K_i:
                INHIBITION = not INHIBITION
            elif event.key == pygame.K_f:
                FRICTION = not FRICTION

    screen.fill((0, 0, 0))  # Fill with black background
    # circle.move()
    sun.draw(screen)
    vehicle.move(sun.position)
    vehicle.draw(screen)

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
