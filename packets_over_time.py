import math
import matplotlib.pyplot as plt
import csv
import numpy as np
from matplotlib.ticker import FuncFormatter


def plot_thing(input_file, home_ip, plot_all=True, plot_second=False, plot_rest=False, website='youtube.com', is_down=True, colors=None, chart=None, names=None, sizes=True):
    if names is None:
        names = ['All streams', 'Top stream', 'Rest']
    if colors is None:
        colors = ['r', 'g', 'b']
    # all streams also 1 stream
    window = 1  # seconds

    streams = {}
    # streams = {
    #     1231255: ''
    # }

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if website in row['website'] and row['protocol'] == 'TCP':
                # # incoming
                # if row['dst'] == home_ip and row['is_ack'] == 'False':
                # outgoing
                if row['dst' if is_down else 'src'] == home_ip and row['is_ack'] == 'False':
                    stream_id = '{0}:{1}|{2}:{3}'.format(row['src'], row['src_port'], row['dst'], row['dst_port'])
                    try:
                        streams[stream_id].append((float(row['timestamp']), int(row['len'])))
                    except KeyError:
                        streams[stream_id] = [(float(row['timestamp']), int(row['len']))]

    # sort list of lists by first value of each list
    sorted_streams = sorted(streams.values(), key=lambda tuples: tuples[0][0])
    first_timestamp = sorted_streams[0][0][0]

    # subtract first timestamp from all
    sorted_streams = map(lambda stream: map(lambda tup: (tup[0] - first_timestamp, tup[1]), stream), sorted_streams)

    # merge list of lists
    all_streams = reduce(lambda x, y: x + y, sorted_streams, [])

    def put_in_bins(time_stamps, size=True):
        """
        Puts packets into time bins (e. g. packets of same second)
        :param time_stamps: list of tuples (time_stamp, packet_length)
        :param size: (optional) if True, sums up lengths, otherwise number of packets
        :return:
        """
        time_bins = []
        for time_stamp, length in time_stamps:
            bin_index = int(time_stamp / window)
            try:
                time_bins[bin_index] += length if size else 1
            except IndexError:
                while len(time_bins) != bin_index:
                    time_bins.append(0)
                time_bins.append(length if size else 1)
        return time_bins

    plot_line_list = []
    plot_name_list = []
    if chart is None:
        fig, ax = plt.subplots()
        if sizes:
            ax.set_ylabel('size in KB')
        else:
            ax.set_ylabel('# of packets')
        ax.set_xlabel('time, s')
    else:
        fig, ax, plot_line_list, plot_name_list = chart

    top_stream = sorted(sorted_streams, key=lambda stream: len(stream), reverse=True)[0]
    second_top_stream = reduce(lambda x, y: x + y, sorted(sorted_streams, key=lambda stream: len(stream), reverse=True)[1:], [])

    i = 0
    all_values = []
    if plot_all:
        values = put_in_bins(all_streams, sizes)
        all_values.extend(values)
        red_line = plt.plot(values, colors[i] + '-')
        plot_line_list.append(red_line[0])
        plot_name_list.append(names[i])
        i += 1
    if plot_second:
        values = put_in_bins(top_stream, sizes)
        all_values.extend(values)
        blue_line = plt.plot(values, colors[i] + '-')
        plot_line_list.append(blue_line[0])
        plot_name_list.append(names[i])
        i += 1
    if plot_rest:
        values = put_in_bins(second_top_stream, sizes)
        all_values.extend(values)
        green_line = plt.plot(values, colors[i] + '-')
        plot_line_list.append(green_line[0])
        plot_name_list.append(names[i])
        i += 1
    plt.legend(plot_line_list, plot_name_list)
    if sizes:
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
        while (1.1 * max(all_values) - step_size) / step_size >= 15:
            step_size *= 10
            i += 1
            if i == 3:
                step_size = (step_size / 1000) * 1024
                i = 0
                power += 1
        if (1.1 * max(all_values) - step_size) / step_size < 5:
            step_size /= 5
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, pos: '{0:.0f} {1}'.format(round(y / math.pow(1024, power), 0), units[power])))
        tix = np.arange(step_size, 1.1 * max(all_values), step_size)
        plt.yticks(tix)
    return fig, ax, plot_line_list, plot_name_list


def plot(which, show):
    if 'el_manana' in which:
        android = {
            'file': 'el_manana/android_el_manana.csv',
            'ip': '192.168.0.4'
        }
        chrome = {
            'file': 'el_manana/out.csv',
            'ip': '10.0.2.15'
        }

    if which in 'el_manana_android_over_time_incoming_1':
        plot_thing(android['file'], android['ip'], is_down=True, colors=['r'], names=['All streams'])
        plt.savefig('el_manana_android_over_time_incoming.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_android_over_time_incoming_2':
        plot_thing(android['file'], android['ip'], plot_second=True, is_down=True, colors=['r', 'g'], names=['All streams', 'Top stream'])
        plt.savefig('el_manana_android_over_time_incoming_2.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_android_over_time_incoming_3':
        plot_thing(android['file'], android['ip'], plot_second=True, plot_rest=True, is_down=True, colors=['r', 'g', 'b'], names=['All streams', 'Top stream', 'Rest'])
        plt.savefig('el_manana_android_over_time_incoming_3.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_chrome_over_time_incoming_1':
        plot_thing(chrome['file'], chrome['ip'], is_down=True, colors=['r'], names=['All streams'])
        plt.savefig('el_manana_chrome_over_time_incoming.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_chrome_over_time_incoming_2':
        plot_thing(chrome['file'], chrome['ip'], plot_second=True, is_down=True, colors=['r', 'g'], names=['All streams', 'Top stream'])
        plt.savefig('el_manana_chrome_over_time_incoming_2.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_chrome_over_time_incoming_3':
        plot_thing(chrome['file'], chrome['ip'], plot_second=True, plot_rest=True, is_down=True, colors=['r', 'g', 'b'], names=['All streams', 'Top stream', 'Rest'])
        plt.savefig('el_manana_chrome_over_time_incoming_3.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_both_incoming':
        chart = plot_thing(chrome['file'], chrome['ip'], colors=['r'], is_down=True, names=['YouTube Chrome'])
        plot_thing(android['file'], android['ip'], colors=['b'], is_down=True, chart=chart, names=['YouTube Android'])
        plt.savefig('el_manana_both_incoming.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_both_outgoing':
        chart = plot_thing(android['file'], android['ip'], colors=['b'], is_down=False, names=['YouTube Android'])
        plot_thing(chrome['file'], chrome['ip'], colors=['r'], is_down=False, names=['YouTube Chrome'], chart=chart)

        plt.savefig('el_manana_both_outgoing.svg')
        if show:
            plt.show()
        plt.clf()

plot('el_manana', False)
