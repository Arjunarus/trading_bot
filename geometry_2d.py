
def get_matrix(m_size, start, delta):
    assert type(m_size) is dict, 'm_size is not a dict.'
    assert type(start) is dict, 'start is not a dict.'
    assert type(delta) is dict, 'delta is not a dict.'

    return [
        {
            'x': start['x'] + delta['x'] * i,
            'y': start['y'] + delta['y'] * j
        }
        for j in range(m_size['y']) for i in range(m_size['x'])
    ]
