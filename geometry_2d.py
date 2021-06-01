class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return other.x == self.x and other.y == self.y

    def __ne__(self, other):
        return not other == self

    def __add__(self, other):
        return Vector(
            x=self.x + other.x,
            y=self.y + other.y
        )


def get_matrix(m_size, start, delta):
    assert type(m_size) is Vector, 'm_size is not a 2d vector.'
    assert type(start) is Vector, 'start is not a 2d vector.'
    assert type(delta) is Vector, 'delta is not a 2d vector.'

    return [
        Vector(x=start.x + delta.x * i, y=start.y + delta.y * j)
        for j in range(m_size.y) for i in range(m_size.x)
    ]
