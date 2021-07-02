# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 00:09:22 2021

@author: Ctariy
"""

import pygame
from random import randint
from time import time


class Game(object):
    """
    Main application class.
    Responsible for setting up the window and running the game.
    """

    def __init__(self, WIDTH, HEIGHT, FPS, obj_num, mines_num,
                 player_size, player_field_of_view):
        """
        Game class initiator.

        Parameters
        ----------
        WIDTH : The width of the game window.
        HEIGHT : The height of the game window.
        FPS : The framerate of the game.
        obj_num : Number of objects on the map.
        mines_num : Number of mines on the map.
        player_size : Player size in pixels.
        player_field_of_view : Player's field of view size in pixels.

        Returns
        -------
        Game object.

        """
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.FPS = FPS
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.display = pygame.display.set_caption("Search for objects")
        self.clock = pygame.time.Clock()
        self.player_size = player_size
        self.player_field_of_view = player_field_of_view
        self.obj_num = obj_num
        self.obj_counter = 0
        self.start_time = time()
        self.mines_num = mines_num
        self.map = Map(self.screen, self.WIDTH, self.HEIGHT,
                       self.obj_num, self.mines_num)
        self.player_history = []
        pygame.mouse.set_visible(False)

    def run(self):
        """Starting the gameplay, processing basic actions."""
        self.running = True
        while self.running:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player = Player(self.screen, event.pos,
                                    self.player_size,
                                    self.player_field_of_view)
                    self.map.object_collision(player)
                    pygame.display.update()
                if event.type == pygame.MOUSEMOTION:
                    self.player_history.append(event.pos)
                    self.player_history = self.map.fog_of_war(
                        self.screen,
                        self.player_history,
                        self.player_field_of_view)
                    pygame.draw.circle(
                        self.screen,
                        BLUE,
                        self.player_history[len(self.player_history)-2],
                        self.player_field_of_view)
                    pygame.draw.circle(self.screen,
                                       BLUE,
                                       event.pos,
                                       self.player_field_of_view)
                    player = Player(self.screen, event.pos,
                                    self.player_size,
                                    self.player_field_of_view)
                    if self.map.object_collision(player):
                        self.obj_counter += 1
                        print(f'{self.obj_counter} from {self.obj_num}')
                        if self.obj_counter == self.obj_num:
                            game_time = round(time() - self.start_time, 2)
                            print(f"Yeah, you found all the objects in {game_time}s!")
                            self.screen = pygame.display.set_mode(
                                (self.WIDTH, self.HEIGHT))
                            self.map = Map(self.screen, self.WIDTH,
                                           self.HEIGHT, self.obj_num,
                                           self.mines_num)
                            self.player_history = []
                            self.obj_counter = 0
                    if self.map.mine_collision(player):
                        print('Sorry, you could not find all the objects.')
                        self.obj_counter = 0
                    pygame.display.update()
            pygame.display.flip()
        self.stop()

    def stop(self):
        """Ending the game process."""
        pygame.quit()


class Player(object):
    """
    The class is responsible for all actions of the player.
    """

    def __init__(self, screen, pos, size, view_field):
        """
        Player class initiator.

        Parameters
        ----------
        screen : pygame.display object.
        pos : Player position on the map.
        size : Player size.
        view_field : Size of the player's field of view.
        Returns
        -------
        Player object.

        """
        self.screen = screen
        self.pos = pos
        self.size = size
        self.view_field = view_field
        self.show()

    def show(self):
        """Display the player."""
        self.player = pygame.draw.rect(
            self.screen,
            RED,
            (self.pos[0] - self.size / 2,
             self.pos[1] - self.size / 2,
             self.size, self.size))
        pygame.display.update()


class Map(object):
    """
    The class is responsible for all actions on the map
    related to the player, objects or mines.
    """

    def __init__(self, screen, WIDTH, HEIGHT, obj_num, mines_num):
        """
        Map class initiator.

        Parameters
        ----------
        screen : pygame.display object.
        WIDTH : The width of the game window.
        HEIGHT : The height of the game window.
        obj_num : Number of objects on the map..
        mines_num : Number of mines on the map.

        Returns
        -------
        Map object.

        """
        self.screen = screen
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.obj_num = obj_num
        self.mines_num = mines_num
        self.objects = self.generate_objects(self.obj_num)
        self.objects_found = []
        self.mines = self.generate_mines(self.mines_num)

    def restart(self):
        """Reloading in case of a loss."""
        self.objects = self.generate_objects(self.obj_num)
        self.mines = self.generate_mines(self.mines_num)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    def generate_objects(self, obj_num):
        """Place objects on the map."""
        field = []
        for i in range(obj_num):
            field.append([(randint(0, self.WIDTH),
                          randint(0, self.HEIGHT)),  # coords
                          randint(5, 20)])  # size
        return field

    def generate_mines(self, mines_num):
        """Place mines on the map."""
        mines = []
        for i in range(mines_num):
            mines.append([(randint(0, self.WIDTH),
                          randint(0, self.HEIGHT)),  # coords
                          randint(5, 15)])  # size
        return mines

    def object_collision(self, player):
        """Player's collision with an object."""
        for obj in self.objects:
            if self.view_collision(player, obj):
                pygame.draw.circle(self.screen,
                                   GREEN,
                                   obj[0], obj[1])
            if self.player_collision(player, obj):
                pygame.draw.circle(self.screen,
                                   WHITE,
                                   obj[0], obj[1])
                if obj not in self.objects_found:
                    self.objects_found.append(obj)
                    return True
        return False

    def mine_collision(self, player):
        """Player's collision with a mine."""
        for mine in self.mines:
            if self.view_collision(player, mine):
                pygame.draw.circle(self.screen,
                                   ORANGE,
                                   mine[0], mine[1])
            if self.player_collision(player, mine):
                pygame.draw.circle(self.screen,
                                   RED,
                                   mine[0], mine[1])
                print("BOOM")
                self.restart()
                return True
        return False

    def fog_of_war(self, screen, history, field_of_view):
        """Hide the map shown a long time ago."""
        if len(history) > 100:
            pos = history[0]
            pygame.draw.circle(
                screen,
                BLACK,
                pos, field_of_view)
            self.show_objects(screen, pos, field_of_view)
            self.hide_mines(screen, pos, field_of_view)
            history = history[1:]
        return history

    def show_objects(self, screen, pos, field_of_view):
        """Don't let the objects get lost in the fog of war."""
        for obj in self.objects:
            if self.circle_in_circle((pos[0], pos[1], 30),
                                     (obj[0][0], obj[0][1], obj[1])):
                pygame.draw.circle(
                    screen,
                    GREEN,
                    obj[0], obj[1])

    def hide_mines(self, screen, pos, field_of_view):
        """Hide the mines in the fog of war."""
        for mine in self.mines:
            if self.circle_in_circle((pos[0], pos[1], field_of_view),
                                     (mine[0][0], mine[0][1], mine[1])):
                pygame.draw.circle(
                    screen,
                    BLACK,
                    mine[0], mine[1])
                self.show_objects(screen, mine[0], field_of_view)

    def view_collision(self, player, obj):
        """Detect collision between player view field and object."""
        x, y = player.pos[0], player.pos[1]
        visibility = player.view_field

        x2, y2 = obj[0][0], obj[0][1]
        radius = obj[1]

        return self.circle_in_circle((x, y, visibility), (x2, y2, radius))

    def player_collision(self, player, obj):
        """Detect collision between player and object."""
        x, y = player.pos[0], player.pos[1]
        size = player.size

        x2, y2 = obj[0][0], obj[0][1]
        radius = obj[1]

        if self.point_in_rect((x2, y2), (x, y, size)):
            return True

        elif self.dist_to_quadrilateral((x2, y2), (x, y, size)) <= radius:
            return True
        else:
            return False

    def circle_in_circle(self, c1, c2):
        """Detect collision between two circles."""
        x1, y1, r1 = c1
        x2, y2, r2 = c2
        distance = ((x2 - x1)**2+(y2 - y1)**2)**.5
        if distance <= r1 + r2:
            return True
        else:
            return False

    def point_in_rect(self, point, rect):
        """Detect if the point lies inside the rectangle."""
        x, y, size = rect
        x1, y1, w, h = x - size/2, y - size/2, size, size
        x2, y2 = x1+w, y1+h
        x, y = point
        if (x1 < x and x < x2):
            if (y1 < y and y < y2):
                return True
        return False

    def dist_to_quadrilateral(self, point, quadrilateral):
        """Get the shortest distance from the point to the quadrilateral."""
        x, y, size = quadrilateral
        x1, y1, x2, y2 = x - size/2, y - size/2, x + size/2, y + size/2
        edges = [[[x1, y1], [x1, y2]], [[x1, y2], [x2, y2]],
                 [[x2, y2], [x2, y1]], [[x2, y1], [x1, y1]]]

        distances = []
        for edge in edges:
            x1, y1 = edge[0]
            x2, y2 = edge[1]
            x3, y3 = point

            px = x2 - x1
            py = y2 - y1

            u = 1 if ((x3 - x1)*px + (y3 - y1)*py) / (px*px + py*py) > 1 else 0

            x = x1 + u * px
            y = y1 + u * py

            dx = x - x3
            dy = y - y3

            dist = (dx*dx + dy*dy)**0.5
            distances.append(dist)

        return min(distances)


WIDTH = 480
HEIGHT = 480
FPS = 300
obj_num = 15
mines_num = 10
player_size = 20
player_field_of_view = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

if __name__ == "__main__":
    Game = Game(WIDTH, HEIGHT, FPS, obj_num, mines_num,
                player_size, player_field_of_view)
    Game.run()
