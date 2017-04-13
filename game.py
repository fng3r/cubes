import logging
from queue import Queue
from random import randint, random
from collections import defaultdict


logging.basicConfig(
            format='%(filename)s[LINE:%(lineno)d]# \
                    %(levelname)-8s [%(asctime)s]  %(message)s',
            filename='mylog.log')


class Cube:
    def __init__(self, color, location):
        self.colors = color
        self.location = location


class Field:
    colors = ['red', 'green', 'yellow', 'blue', 'purple', 'aqua', 'orange']

    def __init__(self, size, settings):
        self.size = size
        self.cubes = defaultdict(int)
        self._field = self.create_random_field(settings)
        self.empty = None
        self.right_border = self.size

    def create_random_field(self, settings=None):
        field = []
        colors_count = settings['colors_count']
        multiple_colors = settings['multiple_colors']
        multicube_count = settings['multicube_count']

        available_colors = self.colors[:colors_count]
        for x_coord in range(self.size):
            field.append([])
            for y_coord in range(self.size):
                multiplier = multiple_colors \
                    if (random() > 0.8 and multicube_count > 0) else 1
                cube_colors = tuple()

                if multiplier > 1:
                    multicube_count -= 1

                unused_colors = available_colors
                for i in range(0, multiplier):
                    unused_colors = [color for color in unused_colors
                                     if color not in cube_colors]
                    cube_colors += \
                        unused_colors[randint(0, len(unused_colors) - 1)],
                for color in cube_colors:
                    self.cubes[color] += 1
                field[x_coord].append(Cube(cube_colors, (x_coord, y_coord)))
        return field

    def create_from_colors(self, field):
        new_field = []
        for x_coord in range(len(field)):
            new_field.append([])
            for y_coord in range(len(field[x_coord])):
                color = field[x_coord][y_coord],
                self.cubes[color] += 1
                new_field[x_coord].append(Cube(color, (x_coord, y_coord)))
        self._field = new_field

    def set_column(self, num, column):
        column = column[0:self.size]
        self._field[num] = column

    def set_empty_column(self, num):
        empty_column = []
        for i in range(self.size):
            empty_column.append(None)
        self._field[num] = empty_column

    def get(self, x_coord, y_coord):
        return self._field[x_coord][y_coord]

    def set(self, x_coord, y_coord, cube):
        self._field[x_coord][y_coord] = cube
        if cube:
            cube.location = (x_coord, y_coord)

    def delete(self, cube):
        x_coord, y_coord = cube.location
        self._field[x_coord][y_coord] = None

    def has_empty_columns(self):
        for x_coord in range(0, self.right_border):
            if not any(self._field[x_coord]):
                self.empty = x_coord
                return True
        return False

    def make_shift(self):
        for x_coord in range(self.empty, self.right_border - 1):
            for y_coord in range(0, self.size):
                temp = self._field[x_coord][y_coord]
                self.set(x_coord, y_coord, self._field[x_coord + 1][y_coord])
                self.set(x_coord + 1, y_coord, temp)
        self.right_border -= 1

    def get_neighbours(self, cube):
        x_coord, y_coord = cube.location
        result = set()
        for delta_x in range(-1, 2):
            for delta_y in range(-1, 2):
                if abs(delta_x) + abs(delta_y) == 1 \
                        and x_coord + delta_x in range(self.size) \
                        and y_coord + delta_y in range(self.size):
                    neigh = self._field[x_coord + delta_x][y_coord + delta_y]
                    if neigh:
                        result.add(neigh)
        return result

    def get_the_same(self, cube):
        hashset = set()
        queue = Queue()
        queue.queue.append(cube)
        hashset.add(cube)
        while queue.qsize() > 0:
            current = queue.queue.pop()
            for neighbour in self.get_neighbours(current):
                if neighbour not in hashset:
                    for c_color in current.colors:
                        for n_color in neighbour.colors:
                            if n_color == c_color and \
                               n_color == cube.colors[0]:
                                hashset.add(neighbour)
                                queue.queue.append(neighbour)
        return hashset


class Game:
    _default_record_table = [
        ['Nick', '5000'],
        ['John', '4500'],
        ['Matthew', '4000'],
        ['Mary', '3500'],
        ['Mike', '3250'],
        ['Alice', '2500'],
        ['Jay', '2300'],
        ['Anny', '2100'],
        ['Clementine', '1950'],
        ['WeakPlayer', '100']
    ]

    _default_settings = {
        'colors_count': 5,
        'multiple_colors': 2,
        'multicube_count': 0
    }

    record_table = []

    def __init__(self, size, player, settings=None):
        self.size = size
        self.settings = settings or Game._default_settings
        self.field = Field(size, self.settings)
        self.player = player
        # self.logger = logging
        # self.logger.basicConfig(
        #     format='%(filename)s[LINE:%(lineno)d]# \
        #             %(levelname)-8s [%(asctime)s]  %(message)s',
        #     filename='mylog.log')
        if not self.record_table:
            Game.record_table = self.load_record_table()
        self.score = 0

    def replicate(self):
        return Game(self.size, self.player, self.settings)

    def autocomplete(self):
        for x_coord in range(self.size):
            for y_coord in range(self.size):
                cube = self.get(x_coord, y_coord)
                if cube:
                    if self.try_delete_block(cube):
                        break

    def try_delete_block(self, cube):
        result = self.field.get_the_same(cube)
        count = len(result)
        if count > 1:
            for item in result:
                self.delete(item)
                for color in item.colors:
                    self.field.cubes[color] -= 1
            self.score += self.get_points(count)

        self.tick()
        return count > 1

    def load_record_table(self):
        try:
            with open('record_table.txt') as file:
                records = [item.split() for item in file.read().split('\n')]
        except (FileNotFoundError, PermissionError, IndexError) as error:
            logging.error('Can not read record table file: %s' % error)
            records = Game._default_record_table
        return records

    def insert_result(self):
        self.record_table.append([self.player, str(self.score)])
        self.record_table.sort(key=lambda item: int(item[1]), reverse=True)
        self.record_table = self.record_table[0:10]

    def save_record_table(self):
        try:
            with open('record_table.txt', 'w+') as file:
                file.write('\n'.join(
                    [' '.join(record) for record in self.record_table]))
        except PermissionError as error:
            logging.error("Record table couldn't be saved: %s" % error)

    @staticmethod
    def get_points(cubes_amount):
        if cubes_amount < 2:
            return 0

        points = 0
        for multiplier in range(2, cubes_amount):
            points += int(5 * (multiplier - 1) + 1.6 ** multiplier)
        points = max(2, points)
        return points

    def tick(self):
        self.fall_down()
        self.join()

    def fall_down(self):
        for x_coord in range(self.size):
            for y_coord in range(self.size - 2, -1, -1):
                cube = self.get(x_coord, y_coord)
                if cube:
                    lower_cube = self.get(x_coord, y_coord + 1)
                    stages_down = 0
                    while not lower_cube:
                        stages_down += 1
                        if y_coord + stages_down + 1 >= self.size:
                            break
                        lower_cube = self.get(
                            x_coord, y_coord + stages_down + 1)
                    if stages_down > 0:
                        self.move_to(x_coord, y_coord + stages_down, cube)

    def join(self):
        while self.field.has_empty_columns():
            self.field.make_shift()

    def move_to(self, x_coord, y_coord, cube):
        self.set(cube.location[0], cube.location[1], None)
        self.set(x_coord, y_coord, cube)

    def get(self, x_coord, y_coord):
        return self.field.get(x_coord, y_coord)

    def set(self, x_coord, y_coord, value):
        self.field.set(x_coord, y_coord, value)

    def delete(self, cube):
        self.field.delete(cube)

    @property
    def is_finished(self):
        for x_coord in range(self.size):
            for y_coord in range(self.size):
                cube = self.get(x_coord, y_coord)
                if cube:
                    neighs = self.field.get_the_same(cube)
                    if len(neighs) > 1:
                        return False
        return True
