import random
import sys
import threading
import time

import numpy as np
import pygame



map_size = 800
map = np.eye(map_size)

dots = []



for i in range(map_size):
    for j in range(map_size):
        map[i][j] = 0

pygame.init()
screen = pygame.display.set_mode((map_size, map_size))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()



def get_len(x1, x2, y1, y2):
    return (((x2 - x1)**2) + ((y2 - y1)**2))**0.5

def thread_start():
    global thread
    thread = threading.Thread(target=map_create, daemon=True)
    thread.start()


def upp(_map):
    maximum = 0
    for i in range(map_size):
        for j in range(map_size):
            if _map[i][j] > maximum:
                maximum = _map[i][j]



    for i in range(map_size):
        for j in range(map_size):
            _map[i][j] += 255 - maximum



    return _map

def normalize(_map):
    maximum = 0
    for i in range(map_size):
        for j in range(map_size):
            if _map[i][j] > maximum:
                maximum = _map[i][j]


    for i in range(map_size):
        for j in range(map_size):
            _map[i][j] = int(((_map[i][j]) / maximum) * 255)

    return _map


def add_noise(noise_mult):
    global _noise
    _noise1 = np.eye(map_size)
    for i in range(map_size):
        for j in range(map_size):
            _noise1[i][j] = random.randint(0, 100)

    _noise1 = smooth(_noise1, noise_mult)

    return _noise1

def smooth(map, smooth_mult):
    for m in range(smooth_mult):
        for x in range(map_size):
            for y in range(map_size):
                if x == 0 and y == 0:
                    map[x][y] = (map[x + 1][y] + map[x + 1][y + 1] + map[x][y + 1]) // 3
                elif x == map_size - 1 and y == 0:
                    map[x][y] = (map[x - 1][y] + map[x - 1][y + 1] + map[x][y + 1]) // 3
                elif x == 0 and y == map_size - 1:
                    map[x][y] = (map[x + 1][y] + map[x + 1][y - 1] + map[x][y - 1]) // 3
                elif x == map_size - 1 and y == map_size - 1:
                    map[x][y] = (map[x - 1][y] + map[x - 1][y - 1] + map[x][y - 1]) // 3
                elif x == 0 and 0 < y < map_size - 1:
                    map[x][y] = (map[x][y - 1] + map[x + 1][y - 1] + map[x + 1][y] + map[x + 1][y + 1] +
                                     map[x][y + 1])//5
                elif x == map_size - 1 and 0 < y < map_size - 1:
                    map[x][y] = (map[x][y - 1] + map[x - 1][y - 1] + map[x - 1][y] + map[x - 1][y + 1] +
                                     map[x][y + 1]) // 5
                elif 0 < x < map_size - 1 and y == 0:
                    map[x][y] = (map[x - 1][y] + map[x - 1][y + 1] + map[x][y + 1] + map[x + 1][y + 1] +
                                     map[x + 1][y]) // 5
                elif 0 < x < map_size - 1 and y == map_size - 1:
                    map[x][y] = (map[x - 1][y] + map[x - 1][y - 1] + map[x][y - 1] + map[x + 1][y - 1] +
                                     map[x + 1][y]) // 5
                elif 0 < x < map_size - 1 and 0 < y < map_size - 1:
                    map[x][y] = (map[x - 1][y] + map[x - 1][y - 1] +
                                     map[x][y - 1] + map[x + 1][y - 1] +
                                     map[x + 1][y] + map[x + 1][y + 1] +
                                     map[x][y + 1] + map[x - 1][y + 1]) // 8

    return map

def voronoi(map, dots_amount, mode):
    if mode == 1:
        for d in range(dots_amount):
            dots.append((random.randint(0, map_size), random.randint(0, map_size)))
    elif mode == 2:
        border_width = 10
        for i in range(dots_amount):
            r = random.randint(0, 3)
            if r == 0:
                dots.append((random.randint(0, map_size // border_width), random.randint(0, map_size)))
            elif r == 1:
                dots.append((random.randint(0, map_size), random.randint(0, map_size // border_width)))
            elif r == 2:
                dots.append((random.randint(map_size - (map_size // border_width), map_size), random.randint(0, map_size)))
            elif r == 3:
                dots.append((random.randint(0, map_size), random.randint(map_size - (map_size // border_width), map_size)))
        print(dots)
    minimum_len = ((map_size ** 2) // dots_amount)

    for i in range(map_size):
        for j in range(map_size):
            minimum = minimum_len
            for d in dots:
                if get_len(i, d[0], j, d[1]) <= minimum:
                    minimum = get_len(i, d[0], j, d[1])
            map[i][j] += int(minimum)

    return map

def draw(map):
    for i in range(map_size):
        for j in range(map_size):
            pygame.draw.rect(screen, (map[i][j], map[i][j], map[i][j]), (i, j, 1, 1))

def corrosion():
    rains = []
    def rain(x, y):
        prev = [x, y]
        paths = [[x-1, y], [x-1, y-1],
                [x, y-1], [x+1, y-1],
                [x+1, y], [x+1, y+1],
                [x, y+1], [x-1, y+1]]
        next = [x, y]
        for p in paths:
            try:
                if map[p[0]][p[1]] <= map[next[0]][next[1]] and p != prev:
                    next = p
            except IndexError:
                continue
        try :
            if (next[0], next[1]) != (x, y):
                map[x][y] = (map[x][y] + map[x-1][y] + map[x-1][y-1] +
                             map[x][y-1] + map[x+1][y-1] + map[x+1][y] +
                             map[x+1][y+1] + map[x][y+1] + map[x-1][y+1] +
                             map[next[0]][next[1]]) / 10
                map[x-1][y] = (map[x][y] + map[x - 1][y] + map[x - 1][y - 1] +
                               map[x][y - 1] + map[x + 1][y - 1] + map[x + 1][y] +
                               map[x + 1][y + 1] + map[x][y + 1] + map[x - 1][y + 1]) / 9
                map[x][y-1] = (map[x][y] + map[x - 1][y] + map[x - 1][y - 1] +
                               map[x][y - 1] + map[x + 1][y - 1] + map[x + 1][y] +
                               map[x + 1][y + 1] + map[x][y + 1] + map[x - 1][y + 1]) / 9
                map[x + 1][y] = (map[x][y] + map[x - 1][y] + map[x - 1][y - 1] +
                                 map[x][y - 1] + map[x + 1][y - 1] + map[x + 1][y] +
                                 map[x + 1][y + 1] + map[x][y + 1] + map[x - 1][y + 1]) / 9
                map[x][y + 1] = (map[x][y] + map[x - 1][y] + map[x - 1][y - 1] +
                                 map[x][y - 1] + map[x + 1][y - 1] + map[x + 1][y] +
                                 map[x + 1][y + 1] + map[x][y + 1] + map[x - 1][y + 1]) / 9
                pygame.draw.rect(screen, (255, 0, 0), (x, y, 1, 1))
                try:
                    rain(next[0], next[1])
                except RecursionError:
                    return 0
            else:
                return 0
        except IndexError:
            return 0

    for i in range(20000):
        rains.append(rain(random.randint(1, map_size - 3), random.randint(1, map_size - 3)))

def map_create():
    global map
    map = voronoi(map, 10, 2)
    map = smooth(map, 10)
    #map = voronoi(map, 50, 1)
    map += add_noise(20)
    map += add_noise(20)
    map = normalize(map)
    #map = smooth(map, 2)
    #map = normalize(map)
    #map = smooth(map, 2)
    draw(map)
    corrosion()
    map = smooth(map, 2)
    map = normalize(map)
    time.sleep(2)
    draw(map)
    corrosion()
    map = smooth(map, 2)
    map = normalize(map)
    time.sleep(2)
    draw(map)
    corrosion()
    map = smooth(map, 10)
    map = normalize(map)
    time.sleep(2)
    draw(map)

    #map = voronoi(map)

    #map = normalize(map)
    #noise()



#print(map)
i = 0
j = 0
running = True
thread_start()
while running:
    clock.tick(220)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        #i += 1

    pygame.display.flip()
pygame.quit()
