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
        self.speed_scalling = 50

        # sensor
        self.sensor_radius = 15
        self.sensor_offset = self.radius + self.sensor_radius
        self.sensor_position = self.position + \
            pygame.math.Vector2(0, -self.sensor_offset).rotate(self.direction)
        self.sensor_color = GREEN

    def update_direction(self):
        self.direction += random.randint(-5, 5)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

        pygame.draw.circle(surface, self.sensor_color,
                           self.sensor_position, self.sensor_radius)

    def calculate_sensor_position(self, sun_position):
        return self.sensor_position.distance_to(sun_position)

    def move(self, sun_position):
        direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        distance = self.calculate_sensor_position(sun_position)
        speed = self.speed_scalling * (1/distance)

        self.position += direction * speed
        self.sensor_position = self.position + \
            pygame.math.Vector2(0, -self.sensor_offset).rotate(self.direction)


def check_collision(vehicle1, vehicle2):
    distance = vehicle1.position.distance_to(vehicle2.position)
    return distance < (vehicle1.radius + vehicle2.radius)


sun = Circle((WIDTH//2, HEIGHT//2), radius=30, color=YELLOW)


vehicles = []
for _ in range(10):
    vehicle = Vehicle((random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                      random.randint(0, 360), radius=20, color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    vehicles.append(vehicle)

last_update_time = 0
update_interval = 240

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    sun.draw(screen)

    current_time = pygame.time.get_ticks()
    if current_time - last_update_time > update_interval:
        for vehicle in vehicles:
            vehicle.update_direction()
        last_update_time = current_time

    for i in range(len(vehicles)):
        for j in range(i + 1, len(vehicles)):
            if check_collision(vehicles[i], vehicles[j]):
                collision_vector = vehicles[i].position - vehicles[j].position
                collision_vector.normalize_ip()

                direction1 = pygame.math.Vector2(0, -1).rotate(vehicles[i].direction)
                direction2 = pygame.math.Vector2(0, -1).rotate(vehicles[j].direction)

                reflected1 = (direction1 - 2 * direction1.dot(collision_vector) * collision_vector).normalize()
                reflected2 = (direction2 - 2 * direction2.dot(collision_vector) * collision_vector).normalize()

                vehicles[i].direction = reflected1.angle_to(pygame.math.Vector2(0, -1))
                vehicles[j].direction = reflected2.angle_to(pygame.math.Vector2(0, -1))


    for vehicle in vehicles:
        vehicle.move(sun.position)
        vehicle.draw(screen)

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
