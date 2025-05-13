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
        self.direction = direction  # Direction in degrees
        self.radius = radius
        self.color = color
        self.speed_scalling = 100
        self.rotation_scalling = 5

        # sensor
        self.sensor_radius = 15
        self.sensor_spacing = 50
        self.sensor_offset = self.radius + self.sensor_radius

        # Initialize sensor positions (will be updated in the first move call)
        self.left_sensor_position = pygame.math.Vector2(0, 0)
        self.right_sensor_position = pygame.math.Vector2(0, 0)
        self.sensor_color = GREEN

        # Update sensor positions initially
        self.update_sensor_positions()

    def update_direction(self, amount=0):
        """Update vehicle direction with optional random component"""
        if amount == 0:
            amount = random.randint(-5, 5)
        self.direction += amount
        self.normalize_direction()

    def normalize_direction(self):
        """Normalize direction to be between 0 and 360 degrees"""
        self.direction = self.direction % 360

    def update_sensor_positions(self):
        """Update the sensor positions based on vehicle position and direction"""
        # Calculate the forward and right direction vectors
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        right_direction = forward_direction.rotate(-90)

        # Calculate sensor positions
        self.left_sensor_position = self.position + forward_direction * \
            self.sensor_offset - right_direction * (self.sensor_spacing/2)
        self.right_sensor_position = self.position + forward_direction * \
            self.sensor_offset + right_direction * (self.sensor_spacing/2)

    def draw(self, surface):
        # Draw vehicle body
        pygame.draw.circle(surface, self.color, (int(
            self.position.x), int(self.position.y)), self.radius)

        # Draw direction indicator (optional)
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        endpoint = self.position + forward_direction * self.radius
        pygame.draw.line(surface, WHITE, self.position, endpoint, 3)

        # Draw sensors
        pygame.draw.circle(surface, self.sensor_color,
                           (int(self.left_sensor_position.x),
                            int(self.left_sensor_position.y)),
                           self.sensor_radius)
        pygame.draw.circle(surface, self.sensor_color,
                           (int(self.right_sensor_position.x),
                            int(self.right_sensor_position.y)),
                           self.sensor_radius)

    def keep_in_bounds(self):
        """Keep vehicle within screen boundaries"""
        self.position.x = max(self.radius, min(
            WIDTH - self.radius, self.position.x))
        self.position.y = max(self.radius, min(
            HEIGHT - self.radius, self.position.y))

    def move(self, sun_position):
        # Calculate distances from sensors to the sun
        left_distance = max(
            1.0, self.left_sensor_position.distance_to(sun_position))
        right_distance = max(
            1.0, self.right_sensor_position.distance_to(sun_position))

        # Calculate speeds based on inverse of distances (closer = faster)
        # Adding max() to avoid division by zero
        left_speed = self.speed_scalling * (1/left_distance)
        right_speed = self.speed_scalling * (1/right_distance)

        # Calculate average speed and rotation
        speed = (left_speed + right_speed) / 2
        rotation = (right_speed - left_speed) * self.rotation_scalling

        # Update direction based on rotation
        self.direction += rotation

        # Get forward direction vector based on current direction
        direction_vector = pygame.math.Vector2(0, -1).rotate(self.direction)

        # Update position
        self.position += direction_vector * speed

        # Add small random movement (Braitenberg vehicles often have this)
        # Remove this if you want more predictable movement
        self.direction += random.randint(-2, 2)

        # Keep vehicle in bounds and normalize direction
        self.keep_in_bounds()
        self.normalize_direction()

        # Update sensor positions
        self.update_sensor_positions()

        # Debug info
        text = font.render(
            f"Left Distance: {left_distance:.2f} Right Distance: {right_distance:.2f} Speed: {speed:.2f}", True, WHITE)
        screen.blit(text, (10, 10))


# Create sun and vehicle
sun = Circle((WIDTH//2, HEIGHT//2), radius=30, color=YELLOW)
vehicle = Vehicle((300, 500), 45)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Add mouse control for the sun (optional)
        if event.type == pygame.MOUSEBUTTONDOWN:
            sun.position = pygame.math.Vector2(event.pos)

    screen.fill((0, 0, 0))  # Fill with black background

    # Draw sun and update vehicle
    sun.draw(screen)
    vehicle.move(sun.position)
    vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
