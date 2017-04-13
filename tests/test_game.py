import unittest
from game import Game
from copy import deepcopy


GAME = Game(3, 3)
GAME.field.create_from_colors(
    [
        ['red', 'red', 'yellow'],
        ['red', 'green', 'red'],
        ['blue', 'green', 'purple']
    ])


class GameTest(unittest.TestCase):

    def test_get_neighbours(self):
        game = deepcopy(GAME)
        cube = game.get(0, 0)
        self.assertEqual(game.field.get_neighbours(cube),
                         {game.get(0, 1), game.get(1, 0)})

    def test_get_the_same(self):
        game = deepcopy(GAME)
        cube = game.get(0, 1)
        self.assertEqual(game.field.get_the_same(cube),
                         {game.get(0, 0),
                          game.get(1, 0),
                          game.get(0, 1)})

    def test_the_same_count(self):
        game = deepcopy(GAME)
        cube = game.get(1, 0)
        self.assertEqual(len(game.field.get_the_same(cube)), 3)

    def test_delete_irremovable_block(self):
        game = deepcopy(GAME)
        cube = game.get(2, 0)
        self.assertFalse(game.try_delete_block(cube))

        cube = game.get(2, 2)
        self.assertFalse(game.try_delete_block(cube))

    def test_deleted_block(self):
        game = deepcopy(GAME)
        cube = game.get(0, 0)

        self.assertTrue(game.try_delete_block(cube))
        self.assertEqual(game.get(0, 0), None)
        self.assertEqual(game.get(0, 1), None)

    def test_has_empty_columns(self):
        game = deepcopy(GAME)
        self.assertFalse(game.field.has_empty_columns())

        game.field.set_empty_column(1)
        self.assertTrue(game.field.has_empty_columns())

    def test_falling(self):
        game = deepcopy(GAME)
        falling_cube = game.get(1, 0)
        self.assertTrue(game.try_delete_block(game.get(1, 1)))
        game.fall_down()

        self.assertIsNone(game.get(1, 0))
        self.assertIsNone(game.get(2, 0))
        self.assertTrue(game.get(1, 1), falling_cube)

    def test_is_finished(self):
        game = deepcopy(GAME)
        self.assertFalse(game.is_finished)

        game.field.set_empty_column(0)
        game.field.set_empty_column(1)
        self.assertTrue(game.is_finished)

    def test_shifting(self):
        game = deepcopy(GAME)
        game.field.set_empty_column(0)
        game.field.set_empty_column(1)

        game.join()
        self.assertIsNotNone(game.get(0, 0))
        self.assertIsNotNone(game.get(0, 1))
        self.assertIsNotNone(game.get(0, 2))

    def test_try_loot_points(self):
        self.assertEqual(GAME.get_points(1), 0)


if __name__ == '__main__':
    unittest.main()
