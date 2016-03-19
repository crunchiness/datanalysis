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


def make_stream_id(src, src_port, dst, dst_port, protocol='TCP', q_cid='0'):
    if protocol == 'TCP':
        return '{0}:{1}-{2}:{3}-{4}'.format(src, src_port, dst, dst_port, protocol)
    elif protocol == 'UDP':
        if q_cid in ['', '0']:
            return '{0}:{1}-{2}:{3}-{4}'.format(src, src_port, dst, dst_port, protocol)
        else:
            return '{0}-{1}'.format(q_cid, protocol)


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


def storage_formatter_factory(unit_speed=False):
        def storage_formatter(y, pos=None):
            if y < 1024:
                unit = 'B' + ('/s' if unit_speed else '')
                value = y
            elif y < 1024 * 1024:
                unit = 'KB' + ('/s' if unit_speed else '')
                value = y / 1024.
            else:
                unit = 'MB' + ('/s' if unit_speed else '')
                value = y / float(1024 * 1024)
            if round(value) == value:
                return '{0:.0f} {1}'.format(value, unit)
            else:
                return '{0:.1f} {1}'.format(value, unit)
        return storage_formatter
