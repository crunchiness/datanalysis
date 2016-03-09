import math
import numpy as np

from matplotlib.ticker import FuncFormatter


class GaplessList:
    def __init__(self, fill='previous'):
        self.list = []
        self.fill = fill

    def set_element(self, pos, element):
        while len(self.list) <= pos:
            if self.fill == 'previous':
                try:
                    previous = self.list[-1]
                except IndexError:
                    previous = 0
                self.list.append(previous)
            else:
                self.list.append(self.fill)
        self.list[pos] = element

    def increment_element(self, pos, increment):
        try:
            self.list[pos] += increment
        except IndexError:
            self.set_element(pos, increment)

    def get_list(self):
        return self.list


def make_stream_id(src, src_port, dst, dst_port, protocol='TCP'):
    return '{0}:{1}-{2}:{3}-{4}'.format(src, src_port, dst, dst_port, protocol)


def make_storage_ticks(values):
    units = {
        0: 'B',
        1: 'KB',
        2: 'MB',
        3: 'GB',
        4: 'TB'
    }
    step_size = 1
    i = 0
    power = 0
    while (1.1 * max(values) - step_size) / step_size >= 15:
        step_size *= 10
        i += 1
        if i == 3:
            step_size = (step_size / 1000) * 1024
            i = 0
            power += 1
    if (1.1 * max(values) - step_size) / step_size < 5:
        step_size /= 5
    fn = FuncFormatter(lambda y, pos: '{0:.0f} {1}'.format(round(y / math.pow(1024, power), 0), units[power]))
    tix = np.arange(step_size, 1.1 * max(values), step_size)
    return fn, tix


def scale_data(data, total, change=1.):
    return map(lambda x: x * change * total / float(sum(data)), data)
