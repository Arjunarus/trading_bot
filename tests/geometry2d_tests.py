import unittest

import geometry_2d


class Geometry2DTest(unittest.TestCase):
    def test_get_matrix(self):
        matrix = geometry_2d.get_matrix(
            m_size={'x': 3, 'y': 4},
            start={'x': 1, 'y': 1},
            delta={'x': 2, 'y': 3}
        )
        r_matrix = [
            {'x': 1, 'y': 1},  {'x': 3, 'y': 1},  {'x': 5, 'y': 1},
            {'x': 1, 'y': 4},  {'x': 3, 'y': 4},  {'x': 5, 'y': 4},
            {'x': 1, 'y': 7},  {'x': 3, 'y': 7},  {'x': 5, 'y': 7},
            {'x': 1, 'y': 10}, {'x': 3, 'y': 10}, {'x': 5, 'y': 10}
        ]

        self.assertListEqual(r_matrix, matrix, msg='Incorrect matrix generator')

    def test_get_matrix_invalid_argument(self):
        self.assertRaises(TypeError, geometry_2d.get_matrix)

        self.assertRaises(
            AssertionError,
            geometry_2d.get_matrix,
            m_size={'x': 3, 'y': 4},
            start={'x': 1, 'y': 1},
            delta=(2, 3)
        )

        self.assertRaises(
            AssertionError,
            geometry_2d.get_matrix,
            m_size={'x': 3, 'y': 4},
            start=(1, 1),
            delta={'x': 2, 'y': 3}
        )

        self.assertRaises(
            AssertionError,
            geometry_2d.get_matrix,
            m_size=(3, 4),
            start={'x': 1, 'y': 1},
            delta={'x': 2, 'y': 3}
        )
