import pygame
from math import sin, cos, pi
import random

pygame.init()

SCALE = 2
WIDTH, HEIGHT = 320*SCALE, 240*SCALE

HEART = [[6.5, 4.5], [9, 2], [11, 4], [9, 8], [6.5, 12], [4, 8], [2, 4], [4, 2]]

white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)

class Player:
    def __init__(self):
        self.rotation = 270
        self.speed = 0

        self.velocity = [0, 0]

        self.d_rotation = 0
        self.acceleration = 0
        self.invulnerability = 0

        self.center = [WIDTH//2, HEIGHT//2]
        self.shape = []
        self.lives = 3

        self.color = white
        self.height = 16*SCALE
        self.width = 10*SCALE

    def generate_shape(self):  # generate points for corners relative to the top's coordinate

        return rotate(
            [[0, -self.height/2],
            [-self.width/2, self.height/2], 
            [0, self.height * 0.85/2], 
            [self.width/2, self.height/2]], 
            self.center, self.rotation)

class Asteroid:
    def __init__(self):

        mean_radius = 8*SCALE

        self.radius = random.randint(int(mean_radius*0.9), int(mean_radius*1.25))
        self.corners = random.randint(5, 8)

        self.center = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
        self.relative_shape = self.generate_relative_shape(self.radius, self.corners)  # (radius, corners)

        self.shape = self.generate_shape(self.relative_shape, self.center)

        speed = random.randint(1, 10) / 10
        direction = random.randint(0, 360) / (180/pi)
        self.velocity = [speed * cos(direction), speed * sin(direction)]

        self.color = white

    def generate_relative_shape(self, radius, corners):
        return rotate(
            [[random.randint(radius//1.5, radius//0.75) * cos(2*pi * (n/corners)), 
            random.randint(radius//1.5, radius//0.75) * sin(2*pi * (n/corners))] 
            for n in range(corners)], (0, 0), random.randint(0, 360))
    
    def generate_shape(self, offset, center):
        return [[center[0] + offset[n][0], center[1] + offset[n][1]] for n in range(self.corners)]

def rotate(points, center, angle):
    
    return [[center[0] - (point[1])*cos(angle / (180/pi)) - (point[0])*sin(angle / (180/pi)), 
            center[1] - (point[1])*sin(angle / (180/pi)) + (point[0])*cos(angle / (180/pi))]
        for point in points]

def ray_casting_collision(points, polygon):

    intersects = 0

    for point in points:
        for i in range(len(polygon)):
            if (polygon[i][1] - polygon[i-1][1]) == 0 or (polygon[i][0] - polygon[i-1][0]) == 0:
                break

            k = ((polygon[i][1] - polygon[i-1][1])/(polygon[i][0] - polygon[i-1][0]))
            x = (point[1] - polygon[i][1])/k + polygon[i][0]

            if x < point[0]:
                if min(polygon[i][0], polygon[i - 1][0]) < x < max(polygon[i][0], polygon[i - 1][0]):
                    intersects += 1

    if intersects % 2 != 0:
        return True
    return False

window = pygame.display.set_mode((WIDTH, HEIGHT))  # start window
ship = Player()  # player variable
asteroids = [Asteroid() for i in range((WIDTH*HEIGHT)//(80*80*SCALE*SCALE))]

def main():
    clock = pygame.time.Clock()  # to set fps and possibly deltaTime
    menu_loop = True
    gameloop = True
    app_loop = True

    while app_loop:
        handle_events()
        ship.lives = 3
        menu_loop = True
        gameloop = True

        while menu_loop:
            handle_events()
            menu_loop = False
            print("death")

        while gameloop:
            handle_events()  # events

            ship.rotation += ship.d_rotation
            ship.speed += ship.acceleration
            
            if ship.speed:  # acceleration
                ship.velocity[0] += ship.speed * cos(ship.rotation / (180/pi))
                ship.velocity[1] += ship.speed * sin(ship.rotation / (180/pi))
                ship.speed = 0

            deceleration = 0.99
            ship.velocity = [ship.velocity[0]*deceleration, ship.velocity[1]*deceleration]  # deceleration

            ship.center[0] += ship.velocity[0]
            ship.center[1] += ship.velocity[1]

            for asteroid in asteroids:
                asteroid.center[0] += asteroid.velocity[0]
                asteroid.center[1] += asteroid.velocity[1]

                asteroid.shape = asteroid.generate_shape(asteroid.relative_shape, asteroid.center)  # (offset, center)

                if asteroid.center[0] < 0 - asteroid.radius:
                    asteroid.center[0] += WIDTH + 2*asteroid.radius
                if asteroid.center[0] > WIDTH + asteroid.radius:
                    asteroid.center[0] -= WIDTH + 2*asteroid.radius
                if asteroid.center[1] < 0 - asteroid.radius:
                    asteroid.center[1] += HEIGHT + 2*asteroid.radius
                if asteroid.center[1] > HEIGHT + asteroid.radius:
                    asteroid.center[1] -= HEIGHT + 2*asteroid.radius

            # bounds
            if ship.center[0] < 0:
                ship.center[0] += WIDTH
            if ship.center[0] > WIDTH:
                ship.center[0] -= WIDTH
            if ship.center[1] < 0:
                ship.center[1] += HEIGHT
            if ship.center[1] > HEIGHT:
                ship.center[1] -= HEIGHT

            ship.shape = ship.generate_shape()  # get posistion of each point of ship
            if not ship.invulnerability:
                for asteroid in asteroids:
                    if ray_casting_collision(ship.shape, asteroid.shape) or \
                    ray_casting_collision(asteroid.shape, ship.shape):
                        ship.lives -= 1
                        ship.center = [WIDTH/2, HEIGHT/2]
                        ship.rotation = 270
                        i = 1
                        while ray_casting_collision(ship.generate_shape(), asteroid.shape) or \
                          ray_casting_collision(asteroid.shape, ship.generate_shape()):
                            ship.center = [WIDTH/2 + 10*i, HEIGHT/2 + 10*i]
                            i += 1
                        ship.velocity = [0, 0]
                        ship.color = red
                        ship.invulnerability = 40
                        break
                    ship.color = white
                if ship.lives == 0:
                    gameloop = False
            else:
                ship.invulnerability -= 1
                ship.color = green
            draw()  # graphics

            clock.tick(60)  # 60 fps

def handle_events():
    acceleration = 0.06

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # X button, or similar
            exit_app()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit_app()
            if event.key == pygame.K_w:
                ship.acceleration = acceleration*SCALE
            if event.key == pygame.K_a:
                ship.d_rotation -= 6
            if event.key == pygame.K_d:
                ship.d_rotation += 6
            if event.key == pygame.K_SPACE:
                pass  # shoot
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                ship.acceleration = 0
            if event.key == pygame.K_a:
                ship.d_rotation += 6
            if event.key == pygame.K_d:
                ship.d_rotation -= 6


def draw():
    window.fill(black)  # fill window with black

    pygame.draw.polygon(window, ship.color, ship.shape, width=3)  # rotate and draw the ship
    for asteroid in asteroids:
        pygame.draw.polygon(window, asteroid.color, asteroid.shape, width=3)
    for i in range(ship.lives):
        pygame.draw.polygon(window, white, [[point[0] + i*13, point[1]] for point in HEART])
    for i in range(3 - ship.lives):
        pygame.draw.polygon(window, white, [[point[0] + (2-i)*13, point[1]] for point in HEART], width=2)

    pygame.display.update()  # update display

def exit_app():  # exit the application
    pygame.quit()
    quit()

if __name__ == '__main__':  # run
    main()
