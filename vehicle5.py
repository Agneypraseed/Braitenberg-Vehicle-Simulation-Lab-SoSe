import math
import random
import pygame
import time

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 5 - Threshold Device Brain")
pygame.font.init()
font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 14)
clock = pygame.time.Clock()
fps = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
OLIVE_GREEN = (128, 128, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

# --- "Friend" Definition ---
FRIEND_COLOR = OLIVE_GREEN
FRIEND_FREQUENCY_MIN = 2.0
FRIEND_FREQUENCY_MAX = 3.0
FRIEND_MAX_SPEED = 2.5


class ThresholdDevice:

    def __init__(self, threshold=1.0, delay=0.1, name="Unnamed"):
        self.threshold = threshold
        self.delay = delay
        self.name = name
        self.input_sum = 0.0
        self.output = 0.0
        self.activation_time = 0.0
        self.is_calculating = False

    def update(self, inputs, current_time):
        self.input_sum = sum(inputs) if inputs else 0.0
        if self.input_sum >= self.threshold:
            if not self.is_calculating:
                self.activation_time = current_time
                self.is_calculating = True
            if current_time - self.activation_time >= self.delay:
                self.output = 1.0
            else:
                self.output = 0.0
        else:
            self.is_calculating = False
            self.output = 0.0
        return self.output


class TargetVehicle:
    """Represents other vehicles in the environment."""

    def __init__(self, position, color, frequency, speed, label="Target"):
        self.position = pygame.math.Vector2(position)
        self.radius = 25
        self.color = color
        self.frequency = frequency
        self.speed = speed
        self.label = label
        self.direction = random.uniform(0, 360)
        self.buzz_phase = 0.0

    def update(self, dt):
        direction_vec = pygame.math.Vector2(0, -1).rotate(self.direction)
        self.position += direction_vec * self.speed * dt * 50
        bounced = False
        if self.position.x <= self.radius:
            self.position.x = self.radius
            direction_vec.x *= -1
            bounced = True
        elif self.position.x >= WIDTH - self.radius:
            self.position.x = WIDTH - self.radius
            direction_vec.x *= -1
            bounced = True
        if self.position.y <= self.radius:
            self.position.y = self.radius
            direction_vec.y *= -1
            bounced = True
        elif self.position.y >= HEIGHT - self.radius:
            self.position.y = HEIGHT - self.radius
            direction_vec.y *= -1
            bounced = True
        if bounced:
            self.direction = pygame.math.Vector2(0, -1).angle_to(direction_vec)
        self.buzz_phase += self.frequency * dt * 2 * math.pi

    def get_buzz_intensity(self): return (math.sin(self.buzz_phase) + 1) / 2

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        if self.frequency > 0:
            pygame.draw.circle(surface, WHITE, self.position,
                               int(3 + self.get_buzz_intensity() * 8))
        speed_text = small_font.render(f"Speed: {self.speed:.1f}", True, WHITE)
        surface.blit(speed_text, (self.position.x - 30,
                     self.position.y + self.radius + 5))
        freq_text = small_font.render(
            f"Freq: {self.frequency:.1f} Hz", True, WHITE)
        surface.blit(freq_text, (self.position.x - 30,
                     self.position.y + self.radius + 20))
        label_text = small_font.render(self.label, True, WHITE)
        surface.blit(label_text, (self.position.x - 20,
                     self.position.y - self.radius - 20))


class Vehicle5:

    def __init__(self, position):
        self.position = pygame.math.Vector2(position)
        self.initial_position = pygame.math.Vector2(position)
        self.radius = 35
        self.color = BLUE
        self.direction = 0.0
        self.speed = 0.0
        self.detection_range = 300
        self.last_friend = None
        self.friend_detected = False
        self.brain_state = {}
        # Brain components
        self.color_detector = ThresholdDevice(
            threshold=0.9, delay=0.1, name="Color")
        self.frequency_detector = ThresholdDevice(
            threshold=0.9, delay=0.15, name="Frequency")
        self.speed_detector = ThresholdDevice(
            threshold=0.9, delay=0.1, name="Speed")
        self.recognition_gate = ThresholdDevice(
            threshold=2.9, delay=0.2, name="Recognition")
        self.motor_controller = ThresholdDevice(
            threshold=0.9, delay=0.05, name="Motor")

    def detect_color_match(
        self, t, d): return 1.0 if d < self.detection_range and t.color == FRIEND_COLOR else 0.0

    def detect_speed_match(
        self, t, d): return 1.0 if d < self.detection_range and t.speed <= FRIEND_MAX_SPEED else 0.0

    def detect_frequency_match(self, t, d):
        if d < self.detection_range and FRIEND_FREQUENCY_MIN <= t.frequency <= FRIEND_FREQUENCY_MAX:
            return 1.0
        return 0.0

    def update_brain(self, targets, current_time):
        best_target, min_distance = None, float('inf')
        for t in targets:
            d = self.position.distance_to(t.position)
            if d < min_distance:
                min_distance, best_target = d, t

        c_in, f_in, s_in = 0, 0, 0
        if best_target and min_distance < self.detection_range:
            c_in, f_in, s_in = self.detect_color_match(best_target, min_distance), self.detect_frequency_match(
                best_target, min_distance), self.detect_speed_match(best_target, min_distance)

        c_out = self.color_detector.update([c_in], current_time)
        f_out = self.frequency_detector.update([f_in], current_time)
        s_out = self.speed_detector.update([s_in], current_time)
        r_out = self.recognition_gate.update(
            [c_out, f_out, s_out], current_time)

        motor_out = self.motor_controller.update([r_out], current_time)

        if motor_out > 0:
            self.friend_detected = True
            self.last_friend = best_target
        else:
            self.friend_detected = False
            self.last_friend = None

        self.brain_state = {'c_in': c_in, 'f_in': f_in, 's_in': s_in, 'c_out': c_out,
                            'f_out': f_out, 's_out': s_out, 'r_out': r_out, 'motor_out': motor_out}

    def update(self, targets, current_time, dt):
        self.update_brain(targets, current_time)
        if self.friend_detected and self.last_friend:
            target_vector = self.last_friend.position - self.position
            target_direction = math.degrees(
                math.atan2(target_vector.x, -target_vector.y))
            angle_diff = (target_direction - self.direction + 180) % 360 - 180
            self.direction += angle_diff * 0.1
            self.speed = 2.5
        else:
            self.speed = 0.0
        if self.speed > 0.01:
            direction_vec = pygame.math.Vector2(0, -1).rotate(self.direction)
            self.position += direction_vec * self.speed * dt * 60

    def draw(self, surface):
        pygame.draw.circle(surface, (40, 40, 60),
                           self.position, self.detection_range, 1)
        color = GREEN if self.friend_detected else self.color
        pygame.draw.circle(surface, color, self.position, self.radius)
        direction_vec = pygame.math.Vector2(
            0, -self.radius * 0.8).rotate(self.direction)
        pygame.draw.line(surface, WHITE, self.position,
                         self.position + direction_vec, 3)
        if self.friend_detected:
            pygame.draw.line(surface, YELLOW, self.position,
                             self.last_friend.position, 2)

    def draw_brain_state(self, surface, x=10, y=70):
        title = font.render("Threshold Device Brain State:", True, WHITE)
        surface.blit(title, (x, y))
        y += 25
        devices = [("Color", self.color_detector, self.brain_state.get('c_out')), ("Frequency", self.frequency_detector,
                                                                                   self.brain_state.get('f_out')), ("Speed", self.speed_detector, self.brain_state.get('s_out'))]
        for name, device, output in devices:
            color = GREEN if output > 0 else GRAY
            text = f"{name}: {device.input_sum:.2f} -> {output:.0f}"
            if device.is_calculating and output == 0:
                text += " (calculating...)"
            surface.blit(small_font.render(text, True, color), (x, y))
            y += 18
        recog_color = GREEN if self.brain_state.get('r_out') > 0 else GRAY
        surface.blit(small_font.render(
            f"Recognition: {self.recognition_gate.input_sum:.2f} -> {self.brain_state.get('r_out'):.0f}", True, recog_color), (x, y))
        y += 18
        motor_color = RED if self.brain_state.get('motor_out') > 0 else GRAY
        surface.blit(small_font.render(
            f"Motor Control: {self.motor_controller.input_sum:.2f} -> {self.brain_state.get('motor_out'):.0f}", True, motor_color), (x, y))
        y += 18

    def reset(self):
        self.position = self.initial_position.copy()
        self.friend_detected = False
        self.speed = 0.0


def simulation():
    v5 = Vehicle5((WIDTH // 2, HEIGHT // 2))
    friend = TargetVehicle(position=(
        150, HEIGHT // 2), color=FRIEND_COLOR, frequency=2.5, speed=2.0, label="FRIEND")
    # friend.direction = -90  # Move directly right
    decoys = [
        TargetVehicle((WIDTH - 150, 150), RED, 2.5, 1.5, "Wrong Color"),
        TargetVehicle((150, 150), FRIEND_COLOR, 0.5, 1.8, "Wrong Frequency"),
        TargetVehicle((WIDTH - 150, HEIGHT - 150),
                      FRIEND_COLOR, 2.5, 4.0, "Too Fast"),
    ]
    return v5, [friend] + decoys


vehicle5, targets = simulation()
running = True
start_time = time.time()
while running:
    dt = clock.tick(fps) / 1000.0
    current_time = time.time() - start_time
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            vehicle5, targets = simulation()
            start_time = time.time()
    screen.fill((20, 20, 40))
    for target in targets:
        target.update(dt)
        target.draw(screen)
    vehicle5.update(targets, current_time, dt)
    vehicle5.draw(screen)
    title_text = font.render("Braitenberg Vehicle 5", True, WHITE)
    screen.blit(title_text, (10, 10))
    control_text = small_font.render(
        "Press 'R' to reset simulation.", True, WHITE)
    screen.blit(control_text, (10, 50))
    vehicle5.draw_brain_state(screen)
    pygame.display.flip()

pygame.quit()
