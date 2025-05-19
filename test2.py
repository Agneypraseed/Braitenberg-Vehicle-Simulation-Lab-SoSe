import random
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 3 Simulation")

pygame.font.init()
font = pygame.font.SysFont("Arial", 24)

clock = pygame.time.Clock()
fps = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FRICTION = False
INHIBITION = True
CROSS = True  # Switch between 3a (False) and 3b (True)


class Circle:
    def __init__(self, position, radius=30, color=YELLOW):
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class Vehicle:
    def __init__(self, position, direction, radius=20, color=RED):
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color
        self.speed_scaling = 100  # Renamed for clarity
        self.rotation_scaling = 5
        self.max_speed = 5  # Add a max speed to prevent too fast movement
        self.base_speed = 1  # Base speed when far from source

        # sensor
        self.sensor_radius = 15
        self.sensor_spacing = 50
        self.sensor_offset = self.radius + self.sensor_radius

        # Initialize sensor positions
        self.update_sensor_positions()

    def update_sensor_positions(self):
        # Calculate forward and right directions
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        right_direction = forward_direction.rotate(90)  # Using 90 for right

        # Update sensor positions
        self.left_sensor_position = self.position + forward_direction * \
            self.sensor_offset - right_direction * (self.sensor_spacing/2)
        self.right_sensor_position = self.position + forward_direction * \
            self.sensor_offset + right_direction * (self.sensor_spacing/2)

    def update_direction(self):
        self.direction += random.randint(-5, 5)

    def draw(self, surface):
        # Draw vehicle body
        pygame.draw.circle(surface, self.color, self.position, self.radius)

        # Draw direction indicator (a line pointing in the direction)
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        pygame.draw.line(surface, WHITE, 
                        self.position, 
                        self.position + forward_direction * self.radius * 1.5, 
                        3)

        # Draw sensors
        sensor_color = BLUE if CROSS else GREEN
        pygame.draw.circle(surface, sensor_color,
                          self.left_sensor_position, self.sensor_radius)

        pygame.draw.circle(surface, sensor_color,
                          self.right_sensor_position, self.sensor_radius)

    def move(self, sun_position):
        # Calculate sensor distances
        left_distance = self.left_sensor_position.distance_to(sun_position)
        right_distance = self.right_sensor_position.distance_to(sun_position)

        # Calculate sensor readings (higher when closer)
        # Use a max distance to limit the influence range
        max_distance = 400
        left_reading = min(1.0, self.speed_scaling / max(left_distance, 10))
        right_reading = min(1.0, self.speed_scaling / max(right_distance, 10))
        
        # Apply proper connections based on vehicle type
        if CROSS:  # Vehicle 3b - crossed inhibitory connections
            left_motor = self.base_speed - right_reading  # Right sensor inhibits left motor
            right_motor = self.base_speed - left_reading  # Left sensor inhibits right motor
        else:      # Vehicle 3a - straight inhibitory connections
            left_motor = self.base_speed - left_reading   # Left sensor inhibits left motor
            right_motor = self.base_speed - right_reading  # Right sensor inhibits right motor
            
        # Ensure speeds don't go below a minimum (to prevent getting completely stuck)
        min_speed = 0.1
        left_motor = max(min_speed, left_motor)
        right_motor = max(min_speed, right_motor)
        
        # Calculate average speed and rotation
        speed = (left_motor + right_motor) / 2
        rotation = (right_motor - left_motor) * self.rotation_scaling
        
        # Update direction and position
        self.direction += rotation
        
        # Get movement vector
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        
        # Apply movement
        self.position += forward_direction * speed
        
        # Screen Wrapping
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        
        # Update sensor positions
        self.update_sensor_positions()
        
        # Apply random friction if enabled
        if FRICTION:
            self.update_direction()
            
        # Display info
        behavior = "Permanent Love (3a)" if not CROSS else "Explorer (3b)"
        text1 = font.render(
            f"Behavior: {behavior} | Cross: {CROSS} | Inhibition: {INHIBITION} | Friction: {FRICTION}",
            True, WHITE)
        text2 = font.render(
            f"Left Motor: {left_motor:.2f} | Right Motor: {right_motor:.2f} | Speed: {speed:.2f}",
            True, WHITE)
        text3 = font.render(
            f"Press C to toggle between 3a/3b | Press R to reset vehicle",
            True, WHITE)

        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 40))
        screen.blit(text3, (10, 70))


# Create objects
sun = Circle((WIDTH//2, HEIGHT//2), radius=30, color=YELLOW)
vehicle = Vehicle((300, 500), 45)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                CROSS = not CROSS
                vehicle.color = BLUE if CROSS else RED
            elif event.key == pygame.K_i:
                INHIBITION = not INHIBITION
            elif event.key == pygame.K_f:
                FRICTION = not FRICTION
            elif event.key == pygame.K_r:
                # Reset vehicle position
                vehicle = Vehicle((300, 500), 45, color=BLUE if CROSS else RED)
            elif event.key == pygame.K_SPACE:
                # Add a new light source at mouse position
                mouse_pos = pygame.mouse.get_pos()
                sun.position = pygame.math.Vector2(mouse_pos)

    screen.fill((0, 0, 0))  # Fill with black background
    
    # Display controls info
    controls_text = font.render("Space: Move light source to mouse position", True, WHITE)
    screen.blit(controls_text, (10, HEIGHT - 30))
    
    # Draw objects
    sun.draw(screen)
    vehicle.move(sun.position)
    vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()