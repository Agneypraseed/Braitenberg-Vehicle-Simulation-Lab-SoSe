import random
import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 4 Simulation")

pygame.font.init()
font = pygame.font.SysFont("Arial", 20)

clock = pygame.time.Clock()
fps = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Vehicle behavior settings
FRICTION = False
INHIBITION = False
CROSS = True
VEHICLE_TYPE = "4a"  # Options: "3", "4a", "4b"
MAX_DISTANCE = 400  # Maximum effective distance for sensor calculations


class Circle:
    def __init__(self, position, radius=30, color=YELLOW):
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color
        self.dragging = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.math.Vector2(event.pos)
                if mouse_pos.distance_to(self.position) <= self.radius:
                    self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.position = pygame.math.Vector2(event.pos)


class Vehicle:
    def __init__(self, position, direction, radius=20, color=RED):
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color
        self.speed_scaling = 100
        self.rotation_scaling = 5

        # sensor
        self.sensor_radius = 15
        self.sensor_spacing = 30
        self.sensor_offset = self.radius + self.sensor_radius

        # Vehicle 4a parameters
        self.optimal_distance = 200  # Distance where motor response is maximum
        self.response_width = 150    # Width of the gaussian-like response curve
        
        # Vehicle 4b parameters
        self.threshold_distance = 300  # Threshold distance for motor activation
        self.min_activation = 0.3      # Minimum activation once threshold is passed

        self.update_sensor_positions()
        self.sensor_color = GREEN
        
        # Trajectory tracking
        self.max_trail_length = 200
        self.trail = []

    def update_sensor_positions(self):
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        right_direction = forward_direction.rotate(-90)

        self.left_sensor_position = self.position + forward_direction * \
            self.sensor_offset - right_direction * (self.sensor_spacing/2)
        self.right_sensor_position = self.position + forward_direction * \
            self.sensor_offset + right_direction * (self.sensor_spacing/2)

    def update_direction(self):
        self.direction += random.randint(-2, 2)

    def draw(self, surface):
        # Draw trail
        if len(self.trail) >= 2:
            pygame.draw.lines(surface, (100, 100, 100), False, self.trail, 1)
        
        # Draw vehicle body
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        
        # Draw direction indicator
        forward_direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        nose_position = self.position + forward_direction * self.radius
        pygame.draw.line(surface, BLUE, self.position, nose_position, 3)

        # Draw sensors
        pygame.draw.circle(surface, self.sensor_color,
                           self.left_sensor_position, self.sensor_radius)
        pygame.draw.circle(surface, self.sensor_color,
                           self.right_sensor_position, self.sensor_radius)

    def calculate_standard_response(self, distance):
        # Standard Vehicle 3 response (inverse proportional)
        if distance < 1:  # Avoid division by zero
            return self.speed_scaling
        response = self.speed_scaling * (1 / distance)
        if INHIBITION:
            response = self.speed_scaling - response
        return max(0, min(response, self.speed_scaling))  # Clamp to [0, speed_scaling]
    
    def calculate_4a_response(self, distance):
        # Vehicle 4a: Non-monotonic response with peak at optimal_distance
        # Using a Gaussian-inspired response curve
        if distance < 1:  # Avoid division by zero
            return 0  # Too close, minimal response
            
        # Calculate normalized response using Gaussian-like formula
        exponent = -((distance - self.optimal_distance) ** 2) / (2 * (self.response_width ** 2))
        response = self.speed_scaling * math.exp(exponent)
        
        if INHIBITION:
            response = self.speed_scaling - response
            
        return max(0, min(response, self.speed_scaling))  # Clamp to [0, speed_scaling]
    
    def calculate_4b_response(self, distance):
        # Vehicle 4b: Threshold-based response
        if distance > self.threshold_distance:
            return 0  # No response beyond threshold
            
        # Linear response with minimum activation once threshold is passed
        normalized_distance = distance / self.threshold_distance
        response = self.speed_scaling * max(self.min_activation, 1 - normalized_distance)
        
        if INHIBITION:
            response = self.speed_scaling - response
            
        return max(0, min(response, self.speed_scaling))  # Clamp to [0, speed_scaling]

    def move(self, sun_position):
        # Update sensor positions
        self.update_sensor_positions()

        # Calculate distances
        left_distance = self.left_sensor_position.distance_to(sun_position)
        right_distance = self.right_sensor_position.distance_to(sun_position)
        
        # Apply maximum effective distance
        left_distance = min(left_distance, MAX_DISTANCE)
        right_distance = min(right_distance, MAX_DISTANCE)

        # Calculate motor responses based on vehicle type
        if VEHICLE_TYPE == "3":
            left_speed = self.calculate_standard_response(left_distance)
            right_speed = self.calculate_standard_response(right_distance)
        elif VEHICLE_TYPE == "4a":
            left_speed = self.calculate_4a_response(left_distance)
            right_speed = self.calculate_4a_response(right_distance)
        elif VEHICLE_TYPE == "4b":
            left_speed = self.calculate_4b_response(left_distance)
            right_speed = self.calculate_4b_response(right_distance)
        
        # Apply cross-wiring if enabled
        if CROSS:
            left_motor, right_motor = right_speed, left_speed
        else:
            left_motor, right_motor = left_speed, right_speed
        
        # Calculate resulting speed and rotation
        speed = (left_motor + right_motor) / 2  # Average speed
        rotation = (right_motor - left_motor) * self.rotation_scaling

        # Update direction and position
        self.direction += rotation
        direction_vector = pygame.math.Vector2(0, -1).rotate(self.direction)
        self.position += direction_vector * speed / fps  # Scale by framerate for consistent speed

        # Add current position to trail
        self.trail.append((int(self.position.x), int(self.position.y)))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Screen Wrapping
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

        # Apply random direction changes if friction is enabled
        if FRICTION:
            self.update_direction()

        # Update display info
        vehicle_types = {
            "3": "Vehicle 3 (Monotonic)",
            "4a": "Vehicle 4a (Peak Response)",
            "4b": "Vehicle 4b (Threshold)"
        }
        behavior = "Explorer" if CROSS else "Love"
        
        text1 = font.render(
            f"Type: {vehicle_types[VEHICLE_TYPE]} | Behavior: {behavior} | Cross: {CROSS} | Inhibition: {INHIBITION}",
            True, WHITE)
        text2 = font.render(
            f"Left Distance: {left_distance:.0f} Right Distance: {right_distance:.0f} | Speed: {speed:.1f}",
            True, WHITE)
        text3 = font.render(
            f"Left Motor: {left_motor:.1f} Right Motor: {right_motor:.1f} | Press T to change vehicle type",
            True, WHITE)

        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 35))
        screen.blit(text3, (10, 60))


# Create objects
sun = Circle((WIDTH//2, HEIGHT//2), radius=30, color=YELLOW)
vehicle = Vehicle((WIDTH//2 + 200, HEIGHT//2), 0)

# Main loop
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
            elif event.key == pygame.K_t:
                # Toggle vehicle type
                if VEHICLE_TYPE == "3":
                    VEHICLE_TYPE = "4a"
                elif VEHICLE_TYPE == "4a":
                    VEHICLE_TYPE = "4b"
                else:
                    VEHICLE_TYPE = "3"
            elif event.key == pygame.K_r:
                # Reset vehicle position
                vehicle.position = pygame.math.Vector2(WIDTH//2 + 200, HEIGHT//2)
                vehicle.direction = 0
                vehicle.trail = []
        
        # Handle sun dragging
        sun.handle_event(event)

    screen.fill((0, 0, 0))  # Fill with black background
    
    # Update and draw objects
    sun.draw(screen)
    vehicle.move(sun.position)
    vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()