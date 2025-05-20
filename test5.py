import random
import math
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

VEHICLE_TYPE = "4a"  # Change to "4b" for threshold behavior

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
        self.speed_scaling = 100
        self.rotation_scaling = 5

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

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        pygame.draw.circle(surface, self.sensor_color,
                           self.left_sensor_position, self.sensor_radius)
        pygame.draw.circle(surface, self.sensor_color,
                           self.right_sensor_position, self.sensor_radius)

    def sensor_response_4a(self, distance):
        # Gaussian-like non-monotonic response: peak at optimal distance
        optimal_distance = 15
        sigma = 80
        return math.exp(-((distance - optimal_distance) ** 2) / (2 * sigma ** 2))

    def sensor_response_4b(self, distance):
        # Step function: no response below threshold, then full speed
        threshold = 200
        if distance > threshold:
            return 0
        else:
            return 1

    def move(self, sun_position):
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        right_direction = forward_direction.rotate(-90)

        self.left_sensor_position = self.position + forward_direction * \
            self.sensor_offset + right_direction * (self.sensor_spacing/2)
        self.right_sensor_position = self.position + forward_direction * \
            self.sensor_offset - right_direction * (self.sensor_spacing/2)

        left_distance = self.left_sensor_position.distance_to(sun_position)
        right_distance = self.right_sensor_position.distance_to(sun_position)

        if VEHICLE_TYPE == "4a":
            left_response = self.sensor_response_4a(left_distance)
            right_response = self.sensor_response_4a(right_distance)
        elif VEHICLE_TYPE == "4b":
            left_response = self.sensor_response_4b(left_distance)
            right_response = self.sensor_response_4b(right_distance)

        left_speed = self.speed_scaling * left_response
        right_speed = self.speed_scaling * right_response

        speed = (left_speed + right_speed) / 2
        rotation = (right_speed - left_speed) * self.rotation_scaling

        self.direction += rotation
        direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        self.position += direction * speed

        # Screen Wrapping
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

        behavior = f"Vehicle {VEHICLE_TYPE.upper()}"
        text1 = font.render(
            f"Behavior: {behavior}", True, WHITE)
        text2 = font.render(
            f"Left D: {left_distance:.2f} Right D: {right_distance:.2f} Speed: {speed:.2f}", True, WHITE)

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
            if event.key == pygame.K_v:
                VEHICLE_TYPE = "4b" if VEHICLE_TYPE == "4a" else "4a"

    screen.fill((0, 0, 0))
    sun.draw(screen)
    vehicle.move(sun.position)
    vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
