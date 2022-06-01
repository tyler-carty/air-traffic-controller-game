import pygame
from pygame import *
import math

# load the image of the a310 plane and set it to a variable and resize the image to half the size
BIG_PLANE = pygame.image.load('Assets/a310.png')
SMALL_PLANE = pygame.transform.scale(BIG_PLANE, (int(BIG_PLANE.get_width() / 1.5), int(BIG_PLANE.get_height() / 1.5)))
TINY_PLANE = pygame.transform.scale(pygame.image.load('Assets/cessna.png'),
                                    (int(BIG_PLANE.get_width() / 2), int(BIG_PLANE.get_height() / 2)))

FAST_PLANE = pygame.image.load('Assets/b17.png')
HARRIER = pygame.image.load('Assets/harrier.png')
HORNET = pygame.image.load('Assets/hornet.png')
RAPTOR = pygame.image.load('Assets/raptor.png')
SPITFIRE = pygame.image.load('Assets/spitfire.png')
STUNT_PLANE = pygame.image.load('Assets/stuntplane.png') # LAND AT ANY LEVEL
TOKYO = pygame.image.load('Assets/tokyo_a310.png')
TOKYO_PLANE = pygame.image.load('Assets/tokyo_plane.png')

HELI_PLANE = pygame.image.load('Assets/heli1.png')
HELI_PLANE2 = pygame.image.load('Assets/heli2.png')
HELI_PLANE3 = pygame.image.load('Assets/heli3.png')
MILITARY_HELI = pygame.image.load('Assets/military_heli1.png')
MILITARY_HELI2 = pygame.image.load('Assets/military_heli2.png')
MILITARY_HELI3 = pygame.image.load('Assets/military_heli3.png')

OUTBACK_HELI = pygame.image.load('Assets/outback_heli1.png')
OUTBACK_HELI2 = pygame.image.load('Assets/outback_heli2.png')
OUTBACK_HELI3 = pygame.image.load('Assets/outback_heli3.png')

OUTBACK_REDBIG = pygame.image.load('Assets/outback_redbig.png')
OUTBACK_REDSMALL = pygame.image.load('Assets/outback_redsmall.png')

SEA_PLANE = pygame.image.load('Assets/sea_plane.png')
SEA_TRACKER = pygame.image.load('Assets/sea_tracker.png')



UNDERLAY_LAND_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_land_runway.png'), (1280, 720))
LAND_MASK = pygame.mask.from_surface(UNDERLAY_LAND_RUNWAY)

UNDERLAY_SEA_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_sea_runway.png'), (1280, 720))
SEA_MASK = pygame.mask.from_surface(UNDERLAY_SEA_RUNWAY)

UNDERLAY_HELI_RUNWAY = pygame.transform.scale(pygame.image.load('Assets/underlay_heli_runway.png'), (1280, 720))
HELI_MASK = pygame.mask.from_surface(UNDERLAY_HELI_RUNWAY)

LAND_RUNWAY_OUTLINE = pygame.transform.scale(pygame.image.load('Assets/Land_Overlay.png'), (1280, 720))
SEA_RUNWAY_OUTLINE = pygame.transform.scale(pygame.image.load('Assets/Sea_Overlay.png'), (1280, 720))
HELI_RUNWAY_OUTLINE = pygame.transform.scale(pygame.image.load('Assets/Heli_Overlay.png'), (1280, 720))

class Plane():
    def __init__(self, x, y, direction):
        super().__init__()
        self.plane_id = self.__class__.__name__
        self.x = x
        self.y = y
        self.vel = 0
        self.direction = direction
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_img = pygame.transform.rotate(BIG_PLANE, self.angle)
        self.default_img = BIG_PLANE
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.runway_img = LAND_RUNWAY_OUTLINE
        self.runway_mask = LAND_MASK
        self.first_collided = False
        self.selected = False
        self.new_select = False
        self.inside = False
        self.movements = []
        self.movements_length = len(self.movements)
        self.interacted = False
        self.length_of_movements = 0
        self.alpha = 255

    def draw(self, game):
        '''
        Draw the plane using an offset to the center of the plane
        :param win: the window to draw the plane on
        :return:
        '''
        x_offset = self.x - self.plane_img.get_rect().width / 2
        y_offset = self.y - self.plane_img.get_rect().height / 2

        # for each movement in the list, draw a line from the last coordinate to the current one
        # if the plane is selected highlight the runway mask
        if self.selected and self.runway_img:
            game.screen.blit(self.runway_img, (0, 0))
        if self.movements and game.playing:
            for i in range(len(self.movements)):
                if i == 0:
                    continue
                # only draw every other line
                pygame.draw.line(game.screen, (80, 80, 80), (self.movements[i - 1][0], self.movements[i - 1][1]),
                                 (self.movements[i][0], self.movements[i][1]), 3)

        if self.movements and game.playing:
            # draw a dot at the last coordinate in the list
            pygame.draw.circle(game.screen, (80, 80, 80), (self.movements[-1][0], self.movements[-1][1]), 6)

        # draw the plane
        game.screen.blit(self.plane_img, (x_offset, y_offset))
        # if the plane is selected, draw a red circle border in the center of the plane
        if self.selected:
            pygame.draw.circle(game.screen, (80, 80, 80), (self.x, self.y), self.default_img.get_rect().width / 2 + 8, 3)

    def draw_runway(self, game):
        '''
        Draw the plane using an offset to the center of the plane
        :param win: the window to draw the plane on
        :return:
        '''
        x_offset = self.x - self.plane_img.get_rect().width / 2
        y_offset = self.y - self.plane_img.get_rect().height / 2

        self.alpha -= 5
        self.plane_img.set_alpha(self.alpha)
        game.screen.blit(self.plane_img, (x_offset, y_offset))
        return self.alpha
    # move the plane in the direction of the direction vector
    def move(self, cursor):
        '''
        Change the x and y coordinates of the plane based on the direction vector
        param cursor: the cursor
        return:
        '''
        if self.movements:
            self.track_movements(cursor)
            return
        self.rect = pygame.rect.Rect(self.x - self.plane_img.get_rect().width / 2,
                                     self.y - self.plane_img.get_rect().height / 2, self.plane_img.get_rect().width,
                                     self.plane_img.get_rect().height)
        self.smooth_angle()
        self.plane_image_check()
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)
        self.x += self.vel * self.direction[0]
        self.y += self.vel * self.direction[1]

    def smooth_angle(self):
        """
        This will smooth the angle of the plane so that it doesn't jerk when it moves
        This is done by calculating what the new angle should be and then calculating,
         the difference between the current angle and the new angle
        Then the angle is set to the new angle plus the difference
        :return:
        """
        new_angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        # smooth angles out
        if abs(new_angle - self.angle) > 1:
            if new_angle > self.angle:
                difference = new_angle - self.angle
                if difference > 180:
                    difference -= 360
                elif difference < -180:
                    difference += 360
                self.angle += difference / 10
            elif new_angle < self.angle:
                difference = self.angle - new_angle
                if difference > 180:
                    difference -= 360
                elif difference < -180:
                    difference += 360
                self.angle -= difference / 10
            elif new_angle == self.angle:
                self.angle = new_angle
        else:
            self.angle = new_angle


    def track_movements(self, cursor):
        '''
        This will track the movements array and change the vector of the plane
        depending on where the next movement is
        :param cursor:
        :return:
        '''
        # choose a random coordinate on the game board
        move = self.movements[0]
        # create a vector between the plane and the coordinate
        vector_x = move[0] - self.x
        vector_y = move[1] - self.y
        vector = pygame.Vector2(vector_x, vector_y)
        self.direction = pygame.Vector2.normalize(vector)
        self.x += self.vel * self.direction[0]
        self.y += self.vel * self.direction[1]
        if abs(self.x - move[0]) < 1 and abs(self.y - move[1]) < 1:
            self.movements.pop(0)

        new_angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi

        # smooth angles out
        self.smooth_angle()
        self.plane_image_check()
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)

    def wall_collide(self, mask, x=0, y=0):
        '''
        Manages the plane collision with the walls
        :param mask:
        :param x:
        :param y:
        :return:
        '''
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = mask.overlap(plane_mask, offset)
        return poi

    def plane_collide(self, other_plane):
        '''
        Manages the plane collisions with other planes
        using the offset of both planes
        :param other_plane:
        :return:
        '''
        other_mask = other_plane.mask
        x = other_plane.x
        y = other_plane.y
        offset = (
            ((self.x - self.plane_img.get_rect().width / 2) - (x - other_plane.plane_img.get_rect().width / 2)) ,
            ((self.y - self.plane_img.get_rect().height / 2) - (y - other_plane.plane_img.get_rect().height / 2)) )
        poi = other_mask.overlap(self.mask, offset)
        # check if two masks overlap
        return poi

    def runway_collide(self, runway_mask, x, y):
        '''
        Manages the collisions between the plane and the runway
        :param runway_mask:
        :param x:
        :param y:
        :return:
        '''
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = runway_mask.overlap(plane_mask, offset)
        return poi

    def plane_image_check(self):
        '''
        Sets the plane image using the subclasses
        :return:
        '''
        # for each subclass of Plane, set the plane image to the correct image
        for plane in Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                self.plane_img = self.default_img

    def handle_runway(self, game):
        for plane in Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                if self.runway_collide(self.runway_mask, 0, 0) and self.interacted is not False:
                    game.remove_plane(self)
                    game.increase_score()

    def refract(self, collide_point):
        # flip the direction vector
        if collide_point[0] == 0:
            self.direction = (-self.direction[0], self.direction[1])
            self.x += 10
        elif collide_point[1] == 0:
            self.direction = (self.direction[0], -self.direction[1])
            self.y += 10
        elif collide_point[0] == 1279:
            self.direction = (-self.direction[0], self.direction[1])
            self.x -= 10
        elif collide_point[1] == 719:
            self.direction = (self.direction[0], -self.direction[1])
            self.y -= 10

        self.plane_image_check()
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)
        self.interacted = False

# create a child class of the plane class called small plane
class SmallPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SMALL_PLANE, self.angle)
        self.default_img = SMALL_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.9
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


# create a child class of the plane class called big plane
class BigPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(BIG_PLANE, self.angle)
        self.default_img = BIG_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.0
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()


class FastPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(FAST_PLANE, self.angle)
        self.default_img = FAST_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.2
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

    def refract(self, collide_point):
        # flip the direction vector
        if collide_point[0] == 0:
            self.direction = (-self.direction[0], self.direction[1])
            self.x += 15
        elif collide_point[1] == 0:
            self.direction = (self.direction[0], -self.direction[1])
            self.y += 15
        elif collide_point[0] == 1279:
            self.direction = (-self.direction[0], self.direction[1])
            self.x -= 15
        elif collide_point[1] == 719:
            self.direction = (self.direction[0], -self.direction[1])
            self.y -= 15


class TinyPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(TINY_PLANE, self.angle)
        self.default_img = TINY_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.8
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class Harrier(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(HARRIER, self.angle)
        self.default_img = HARRIER
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.5
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class Hornet(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(HORNET, self.angle)
        self.default_img = HORNET
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.7
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class Raptor(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(RAPTOR, self.angle)
        self.default_img = RAPTOR
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.8
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class SpitFire(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SPITFIRE, self.angle)
        self.default_img = SPITFIRE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.2
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class StuntPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(STUNT_PLANE, self.angle)
        self.default_img = STUNT_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.9
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class Tokyo(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(TOKYO, self.angle)
        self.default_img = TOKYO
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.0
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class TokyoPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(TOKYO_PLANE, self.angle)
        self.default_img = TOKYO_PLANE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 1.0
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class SeaPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SEA_PLANE, self.angle)
        self.default_img = SEA_PLANE
        self.runway_mask = SEA_MASK
        self.runway_img = SEA_RUNWAY_OUTLINE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.6
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class SeaTracker(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.plane_img = pygame.transform.rotate(SEA_TRACKER, self.angle)
        self.default_img = SEA_TRACKER
        self.runway_mask = SEA_MASK
        self.runway_img = SEA_RUNWAY_OUTLINE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.7
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

class HeliPlane(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.animations = [HELI_PLANE, HELI_PLANE2, HELI_PLANE3]
        self.animation_frame = 0
        self.plane_img = pygame.transform.rotate(self.animations[self.animation_frame], self.angle)
        self.default_img = HELI_PLANE
        self.runway_mask = HELI_MASK
        self.runway_img = HELI_RUNWAY_OUTLINE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.4
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

    def plane_image_check(self):
        '''
        Sets the plane image using the subclasses
        :return:
        '''
        # for each subclass of Plane, set the plane image to the correct image
        for plane in Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                self.plane_img = self.animations[self.animation_frame]
                self.animation_frame += 1
                if self.animation_frame == len(self.animations):
                    self.animation_frame = 0

    def refract(self, collide_point):
        if not self.inside:
            return
        # flip the direction vector
        if collide_point[0] == 0:
            self.direction = (-self.direction[0], self.direction[1])
            self.x += 3
        elif collide_point[1] == 0:
            self.direction = (self.direction[0], -self.direction[1])
            self.y += 3
        elif collide_point[0] == 1279:
            self.direction = (-self.direction[0], self.direction[1])
            self.x -= 3
        elif collide_point[1] == 719:
            self.direction = (self.direction[0], -self.direction[1])
            self.y -= 3

        self.plane_image_check()
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)
        self.interacted = False

    def wall_collide(self, mask, x=0, y=0):
        '''
        Manages the plane collision with the walls
        :param mask:
        :param x:
        :param y:
        :return:
        '''
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = mask.overlap(plane_mask, offset)
        return poi

class MilitaryHeli(Plane):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.plane_id = self.__class__.__name__
        self.animations = [MILITARY_HELI, MILITARY_HELI2, MILITARY_HELI3]
        self.animation_frame = 0
        self.plane_img = pygame.transform.rotate(self.animations[self.animation_frame], self.angle)
        self.default_img = MILITARY_HELI
        self.runway_mask = HELI_MASK
        self.runway_img = HELI_RUNWAY_OUTLINE
        # create the plane image mask
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.vel = 0.5
        self.width = self.plane_img.get_width()
        self.height = self.plane_img.get_height()

    def plane_image_check(self):
        '''
        Sets the plane image using the subclasses
        :return:
        '''
        # for each subclass of Plane, set the plane image to the correct image
        for plane in Plane.__subclasses__():
            if self.plane_id == plane.__name__:
                self.plane_img = self.animations[self.animation_frame]
                self.animation_frame += 1
                if self.animation_frame == len(self.animations):
                    self.animation_frame = 0

    def refract(self, collide_point):
        if not self.inside:
            return
        # flip the direction vector
        if collide_point[0] == 0:
            self.direction = (-self.direction[0], self.direction[1])
            self.x += 3
        elif collide_point[1] == 0:
            self.direction = (self.direction[0], -self.direction[1])
            self.y += 3
        elif collide_point[0] == 1279:
            self.direction = (-self.direction[0], self.direction[1])
            self.x -= 3
        elif collide_point[1] == 719:
            self.direction = (self.direction[0], -self.direction[1])
            self.y -= 3

        self.plane_image_check()
        self.angle = math.atan2(self.direction[0], self.direction[1]) * 180 / math.pi
        self.plane_img = pygame.transform.rotate(self.plane_img, self.angle)
        self.interacted = False

    def wall_collide(self, mask, x=0, y=0):
        '''
        Manages the plane collision with the walls
        :param mask:
        :param x:
        :param y:
        :return:
        '''
        plane_mask = pygame.mask.from_surface(self.plane_img)
        offset = (
            (self.x - x) - self.plane_img.get_rect().width / 2, (self.y - y) - self.plane_img.get_rect().height / 2)
        poi = mask.overlap(plane_mask, offset)
        return poi