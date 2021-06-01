import unittest

import geometry_2d


class Geometry2DTest(unittest.TestCase):
    def test_vector_neq(self):
        v1 = geometry_2d.Vector(10, 20)
        v2 = geometry_2d.Vector(10, 30)
        self.assertNotEqual(v1, v2, msg='Different vectors are equal!')

        v1 = geometry_2d.Vector(10, 20)
        v2 = geometry_2d.Vector(20, 20)
        self.assertNotEqual(v1, v2, msg='Different vectors are equal!')

    def test_vector_eq(self):
        v1 = geometry_2d.Vector(10, 20)
        v2 = geometry_2d.Vector(10, 20)
        self.assertEqual(v1, v2, msg='Same vectors are not equal!')

    def test_vector_add(self):
        v1 = geometry_2d.Vector(10, 20)
        v2 = geometry_2d.Vector(30, 40)
        self.assertEqual(v1 + v2, geometry_2d.Vector(40, 60), msg='Incorrect addition!')

    def test_get_matrix(self):
        matrix = geometry_2d.get_matrix(
            m_size=geometry_2d.Vector(3, 4),
            start=geometry_2d.Vector(1, 1),
            delta=geometry_2d.Vector(2, 3)
        )
        r_matrix = map(lambda p: geometry_2d.Vector(*p), [
            (1,  1), (3,  1), (5,  1),
            (1,  4), (3,  4), (5,  4),
            (1,  7), (3,  7), (5,  7),
            (1, 10), (3, 10), (5, 10)
        ])

        self.assertListEqual(list(r_matrix), matrix, msg='Incorrect matrix generator')

    def test_get_matrix_invalid(self):
        self.assertRaises(TypeError, geometry_2d.get_matrix)

        self.assertRaises(
            AssertionError,
            geometry_2d.get_matrix,
            m_size=geometry_2d.Vector(3, 4),
            start=geometry_2d.Vector(1, 1),
            delta=(2, 3)
        )

        self.assertRaises(
            AssertionError,
            geometry_2d.get_matrix,
            m_size=geometry_2d.Vector(3, 4),
            start=(1, 1),
            delta=geometry_2d.Vector(2, 3)
        )

        self.assertRaises(
            AssertionError,
            geometry_2d.get_matrix,
            m_size=(3, 4),
            start=geometry_2d.Vector(1, 1),
            delta=geometry_2d.Vector(2, 3)
        )
