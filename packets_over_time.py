import csv

import matplotlib.pyplot as plt

from shared import make_storage_ticks, make_stream_id


def plot_thing(input_file, home_ip, plot_all=True, plot_first=False, plot_second=False, plot_rest=False, website='youtube.com', is_incoming=True, colors=None, chart=None, names=None, sizes=True, protocols=None, window=1):
    if protocols is None:
        protocols = ['TCP']
    if names is None:
        names = ['All streams', 'Top stream', 'Rest']
    if colors is None:
        colors = ['r', 'g', 'b']

    streams = {}

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if website in row['website'] and (row['protocol'] in protocols):
                if row['dst' if is_incoming else 'src'] == home_ip and row['is_ack'] == 'False':
                    stream_id = make_stream_id(row)
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
    second_stream = sorted(sorted_streams, key=lambda stream: len(stream), reverse=True)[1]
    rest_start_index = 2 if plot_second else 1
    rest_streams = reduce(lambda x, y: x + y, sorted(sorted_streams, key=lambda stream: len(stream), reverse=True)[rest_start_index:], [])

    i = 0
    all_values = []
    if plot_all:
        values = put_in_bins(all_streams, sizes)
        all_values.extend(values)
        red_line = plt.plot(values, colors[i] + '-')
        plot_line_list.append(red_line[0])
        plot_name_list.append(names[i])
        i += 1
    if plot_first:
        values = put_in_bins(top_stream, sizes)
        all_values.extend(values)
        blue_line = plt.plot(values, colors[i] + '-')
        plot_line_list.append(blue_line[0])
        plot_name_list.append(names[i])
        i += 1
    if plot_second:
        values = put_in_bins(second_stream, sizes)
        all_values.extend(values)
        magenta_line = plt.plot(values, colors[i] + '-')
        plot_line_list.append(magenta_line[0])
        plot_name_list.append(names[i])
        i += 1
    if plot_rest:
        values = put_in_bins(rest_streams, sizes)
        all_values.extend(values)
        green_line = plt.plot(values, colors[i] + '-')
        plot_line_list.append(green_line[0])
        plot_name_list.append(names[i])
        i += 1
    plt.legend(plot_line_list, plot_name_list)
    if sizes:
        fn, tix = make_storage_ticks(all_values)
        ax.yaxis.set_major_formatter(fn)
        plt.yticks(tix)
    ax.set_xticklabels([int(x * window) for x in ax.get_xticks()])
    return fig, ax, plot_line_list, plot_name_list


def plot(which, show=False):
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
        plot_thing(android['file'], android['ip'], is_incoming=True, colors=['r'], names=['All streams'])
        plt.savefig('el_manana_android_over_time_incoming.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_android_over_time_incoming_2':
        plot_thing(android['file'], android['ip'], plot_first=True, is_incoming=True, colors=['r', 'g'], names=['All streams', 'Top stream'])
        plt.savefig('el_manana_android_over_time_incoming_2.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_android_over_time_incoming_3':
        plot_thing(android['file'], android['ip'], plot_first=True, plot_rest=True, is_incoming=True, colors=['r', 'g', 'b'], names=['All streams', 'Top stream', 'Rest'])
        plt.savefig('el_manana_android_over_time_incoming_3.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_chrome_over_time_incoming_1':
        plot_thing(chrome['file'], chrome['ip'], is_incoming=True, colors=['r'], names=['All streams'])
        plt.savefig('el_manana_chrome_over_time_incoming.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_chrome_over_time_incoming_2':
        plot_thing(chrome['file'], chrome['ip'], plot_first=True, is_incoming=True, colors=['r', 'g'], names=['All streams', 'Top stream'])
        plt.savefig('el_manana_chrome_over_time_incoming_2.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_chrome_over_time_incoming_3':
        plot_thing(chrome['file'], chrome['ip'], plot_first=True, plot_rest=True, is_incoming=True, colors=['r', 'g', 'b'], names=['All streams', 'Top stream', 'Rest'])
        plt.savefig('el_manana_chrome_over_time_incoming_3.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_both_incoming':
        chart = plot_thing(chrome['file'], chrome['ip'], colors=['r'], is_incoming=True, names=['YouTube Chrome'])
        plot_thing(android['file'], android['ip'], colors=['b'], is_incoming=True, chart=chart, names=['YouTube Android'])
        plt.savefig('el_manana_both_incoming.svg')
        if show:
            plt.show()
        plt.clf()
    if which in 'el_manana_both_outgoing':
        chart = plot_thing(android['file'], android['ip'], colors=['b'], is_incoming=False, names=['YouTube Android'])
        plot_thing(chrome['file'], chrome['ip'], colors=['r'], is_incoming=False, names=['YouTube Chrome'], chart=chart)
        plt.savefig('el_manana_both_outgoing.svg')
        if show:
            plt.show()
        plt.clf()


def plot_audio_video(show=False):
    # android_file = 'el_manana/android_el_manana.csv',
    # android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    plot_thing(chrome_file, chrome_ip, colors=['b', 'r'], plot_all=False, plot_first=True, plot_second=True, plot_rest=False, is_incoming=True, names=['YouTube Chrome video stream', 'YouTube Chrome audio stream'])
    plt.savefig('el_manana_chrome_over_time_audio_video.svg')
    if show:
        plt.show()
    plt.clf()


def netflix_plot(is_incoming=True, show=False):
    android_file = 'hannibal_dump/android.csv'
    android_ip = '192.168.1.6'
    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_ip = '192.168.1.2'
    website = 'netflix.com'

    plot_thing(android_file, android_ip, website=website, is_incoming=is_incoming, plot_all=True, colors=['r'], names=['All streams'], window=10)
    plt.savefig('{}_android_over_time_{}.svg'.format(website, 'incoming' if is_incoming else 'outgoing'))
    if show:
        plt.show()
    plt.clf()

    plot_thing(chrome_file, chrome_ip, website=website, is_incoming=is_incoming, plot_all=True, colors=['r'], names=['All streams'], window=10)
    plt.savefig('{}_chrome_over_time_{}.svg'.format(website, 'incoming' if is_incoming else 'outgoing'))
    if show:
        plt.show()
    plt.clf()


def netflix_plot_outgoing(show=False):
    android_file = 'hannibal_dump/android.csv'
    android_ip = '192.168.1.6'
    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_ip = '192.168.1.2'
    website = 'netflix.com'

    chart = plot_thing(android_file, android_ip, website=website, colors=['b'], is_incoming=False, names=['Netflix Android'])
    plot_thing(chrome_file, chrome_ip, website=website, colors=['r'], is_incoming=False, names=['Netflix Chrome'], chart=chart)

    plt.savefig('{}_over_time_outgoing.svg'.format(website))

    if show:
        plt.show()
    plt.clf()


if __name__ == '__main__':
    # plot('el_manana', show=False)
    # plot_quic(show=False)
    # plot_audio_video(show=False)
    # netflix_plot(show=False)
    netflix_plot_outgoing(show=False)
