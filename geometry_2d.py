class Vector:
    def __init__(self, coords):
        self.x = coords['x']
        self.y = coords['y']


def get_matrix(m_size, start, delta):
    if type(m_size) is not Vector:
        raise ValueError('m_size is not a 2d vector.')
    if type(start) is not Vector:
        raise ValueError('start is not a 2d vector.')
    if type(delta) is not Vector:
        raise ValueError('delta is not a 2d vector.')

    return [
        Vector({
            'x': start.x + delta.x * i,
            'y': start.y + delta.y * j
        })
        for j in range(m_size.x) for i in range(m_size.y)
    ]
