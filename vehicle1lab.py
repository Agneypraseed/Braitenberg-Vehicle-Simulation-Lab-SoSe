import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 1 Simulation")

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

    # def move(self):
    #     self.position.x = self.position.x + 1
    #     self.position.y = self.position.y + 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class Vehicle:
    def __init__(self, position, direction, radius=50, color=RED):
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color

        # sensor
        self.sensor_radius = 15
        self.sensor_offset = self.radius + self.sensor_radius
        self.sensor_position = self.position + pygame.math.Vector2(0,-self.sensor_offset)        
        self.sensor_color = GREEN

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

        self.sensor_position = self.position + pygame.math.Vector2(0,-self.sensor_offset).rotate(self.direction)
        pygame.draw.circle(surface, self.sensor_color,
                           self.sensor_position, self.sensor_radius)
        
    def move(self):
        direction =  pygame.math.Vector2(0,-1).rotate(self.direction)
        magnitude = 6
        self.position += direction * magnitude



sun = Circle((600, 300), radius=30, color=YELLOW)
vehicle = Vehicle((300, 500), 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Fill with black background
    # circle.move()
    sun.draw(screen)
    vehicle.move()
    vehicle.draw(screen)

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
