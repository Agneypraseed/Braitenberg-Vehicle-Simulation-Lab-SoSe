import random
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 2 Simulation")

pygame.font.init()
font = pygame.font.SysFont("Arial", 24)

clock = pygame.time.Clock()
fps = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


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
        
        self.left_sensor_position = self.position
        self.right_sensor_position = self.position
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

        self.left_sensor_position = self.position + forward_direction * self.sensor_offset + right_direction * (self.sensor_spacing / 2)
        self.right_sensor_position = self.position + forward_direction * self.sensor_offset - right_direction * (self.sensor_spacing / 2)

        left_distance = self.left_sensor_position.distance_to(sun_position)
        right_distance = self.right_sensor_position.distance_to(sun_position)

        left_speed = self.speed_scalling * (1/left_distance)
        right_speed = self.speed_scalling * (1/right_distance)

        speed = (left_speed + right_speed) / 2  # Average speed
        # For vehicle 2b (Love): Crossed connections
        rotation = (right_speed - left_speed) * self.rotation_scalling 
        # For vehicle 2a (Fear): Normal connections
        # rotation = (right_speed - left_speed) * self.rotation_scalling *-1
        self.direction += rotation
        direction = pygame.math.Vector2(0, -1).rotate(self.direction)

        self.position += direction * speed
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

        self.left_sensor_position = self.position + forward_direction * \
            self.sensor_offset + right_direction * (self.sensor_spacing/2)

        self.right_sensor_position = self.position + forward_direction * \
            self.sensor_offset - right_direction * (self.sensor_spacing/2)
        
        self.direction += random.randint(-5, 5)


        # debug/print info
        text = font.render(
            f"Left Distance to sun: {left_distance:.2f} Right Distance to sun: {right_distance:.2f} Speed: {speed:.2f}", True, WHITE)
        screen.blit(text, (10, 10))


sun = Circle((WIDTH//2, HEIGHT//2), radius=30, color=YELLOW)
vehicle = Vehicle((300, 500), 45)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Fill with black background
    # circle.move()
    sun.draw(screen)
    vehicle.move(sun.position)
    vehicle.draw(screen)

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
