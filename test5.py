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
RESPONSE_TYPE = "1"  # For 4b: different response functions (1-4)
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
        
        # For visualization
        self.sensor_activations = [0, 0]  # Left, right sensor activation levels

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

        # Draw sensors with intensity-based coloring
        l_color = tuple(min(255, int(g + 180 * self.sensor_activations[0])) for g in GREEN)
        r_color = tuple(min(255, int(g + 180 * self.sensor_activations[1])) for g in GREEN)
        
        pygame.draw.circle(surface, l_color, self.left_sensor_position, self.sensor_radius)
        pygame.draw.circle(surface, r_color, self.right_sensor_position, self.sensor_radius)
        
        # Draw the response curve if 4b is selected
        if VEHICLE_TYPE == "4b":
            self.draw_response_curve(surface)

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
        # Vehicle 4b: Threshold-based response - different types based on Figure 8
        normalized_distance = distance / self.threshold_distance
        
        if RESPONSE_TYPE == "1":
            # Type 1: Simple threshold with minimum activation
            if distance > self.threshold_distance:
                return 0  # No response beyond threshold
            
            # Linear response with minimum activation once threshold is passed
            response = self.speed_scaling * max(self.min_activation, 1 - normalized_distance)
            
        elif RESPONSE_TYPE == "2":
            # Type 2: Step function (abrupt change at threshold)
            if distance > self.threshold_distance:
                return 0
            else:
                response = self.speed_scaling * 0.8  # Constant high response below threshold
                
        elif RESPONSE_TYPE == "3":
            # Type 3: Multiple thresholds (as shown in top-right of Figure 8)
            if distance > self.threshold_distance:
                return 0
            elif distance > self.threshold_distance * 0.7:
                response = self.speed_scaling * 0.5  # Medium response
            elif distance > self.threshold_distance * 0.4:
                response = self.speed_scaling * 0.2  # Low response
            else:
                response = self.speed_scaling  # Full response when very close
                
        elif RESPONSE_TYPE == "4":
            # Type 4: Smooth increase after threshold (similar to bottom left in Figure 8)
            if distance > self.threshold_distance:
                return 0
            
            # Exponential growth as distance gets smaller
            response_factor = 1 - (distance / self.threshold_distance)**2
            response = self.speed_scaling * response_factor
            
        else:  # Type 5: Complex step function (bottom right in Figure 8)
            if distance > self.threshold_distance:
                return 0
            elif distance > self.threshold_distance * 0.6:
                response = self.speed_scaling * 0.3  # Low response
            elif distance > self.threshold_distance * 0.4:
                response = self.speed_scaling  # Full response
            elif distance > self.threshold_distance * 0.2:
                response = self.speed_scaling * 0.5  # Medium response
            else:
                response = self.speed_scaling  # Full response when very close
        
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
        
        response_types = {
            "1": "Minimum Threshold",
            "2": "Step Function",
            "3": "Multiple Thresholds",
            "4": "Smooth After Threshold",
            "5": "Complex Steps"
        }
        
        behavior = "Explorer" if CROSS else "Love"
        
        text1 = font.render(
            f"Type: {vehicle_types[VEHICLE_TYPE]}" + 
            (f" - {response_types[RESPONSE_TYPE]}" if VEHICLE_TYPE == "4b" else ""),
            True, WHITE)
        text2 = font.render(
            f"Behavior: {behavior} | Cross: {CROSS} | Inhibition: {INHIBITION} | L: {left_distance:.0f} R: {right_distance:.0f}",
            True, WHITE)
        text3 = font.render(
            f"Speed: {speed:.1f} | Motors: L: {left_motor:.1f} R: {right_motor:.1f} | T: type, R: response type",
            True, WHITE)

        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 35))
        screen.blit(text3, (10, 60))

    def draw_response_curve(self, surface):
        # Draw the response curve for the current 4b response type
        curve_width = 200
        curve_height = 100
        curve_x = WIDTH - curve_width - 20
        curve_y = HEIGHT - curve_height - 20
        
        # Draw border
        pygame.draw.rect(surface, WHITE, (curve_x, curve_y, curve_width, curve_height), 1)
        
        # Draw axes
        pygame.draw.line(surface, WHITE, (curve_x, curve_y + curve_height - 10), 
                        (curve_x + curve_width, curve_y + curve_height - 10), 1)  # X-axis
        pygame.draw.line(surface, WHITE, (curve_x + 10, curve_y), 
                        (curve_x + 10, curve_y + curve_height), 1)  # Y-axis
        
        # Draw axis labels
        label_font = pygame.font.SysFont("Arial", 16)
        x_label = label_font.render("I (stimulus)", True, WHITE)
        y_label = label_font.render("V (response)", True, WHITE)
        surface.blit(x_label, (curve_x + curve_width - 70, curve_y + curve_height - 20))
        surface.blit(y_label, (curve_x + 15, curve_y + 5))
        
        # Plot the response curve
        points = []
        for i in range(curve_width - 20):
            x = curve_x + 10 + i
            # Map x to a distance value (reversed, as smaller x = larger distance)
            distance = self.threshold_distance * (1 - i / (curve_width - 20))
            
            # Get the response value for this distance
            response = self.calculate_4b_response(distance) / self.speed_scaling
            
            # Map response to y coordinate (inverted, as y increases downward)
            y = curve_y + curve_height - 10 - response * (curve_height - 20)
            points.append((x, y))
        
        # Draw the response curve
        if len(points) >= 2:
            pygame.draw.lines(surface, RED, False, points, 2)
        
        # Draw title
        title = label_font.render(f"Response Type {RESPONSE_TYPE}", True, WHITE)
        surface.blit(title, (curve_x + curve_width // 2 - 50, curve_y - 25))    


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
                # Toggle response type for Vehicle 4b
                if VEHICLE_TYPE == "4b":
                    RESPONSE_TYPE = str((int(RESPONSE_TYPE) % 5) + 1)
                else:
                    # Reset vehicle position for other vehicle types
                    vehicle.position = pygame.math.Vector2(WIDTH//2 + 200, HEIGHT//2)
                    vehicle.direction = 0
                    vehicle.trail = []
            elif event.key == pygame.K_SPACE:
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