import math


def calculate_size(nbytes):

    if nbytes == 0:
        return '0B'
    units = ('B', 'KB', 'MB', 'GB', 'TB')
    i = math.floor(math.log(nbytes, 1024))
    p = math.pow(1024, i)
    s = round(nbytes / p, 2)
    return f'{s} {units[i]}'