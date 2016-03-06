import matplotlib.pyplot as plt
import numpy as np
import csv


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

    def get_list(self):
        return self.list


def make_stream_id(src, src_port, dst, dst_port, protocol='TCP'):
    return '{0}:{1}-{2}:{3}-{4}'.format(src, src_port, dst, dst_port, protocol)


def generate_flow_plot_data(input_file, home_ip, website='youtube.com', is_incoming=True):
    stream_set = set()
    closed_set = set()
    start_timestamp = None
    connection_list = GaplessList()

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            # set start_timestamp if not set
            start_timestamp = float(row['timestamp']) if start_timestamp is None else start_timestamp
            if website in row['website'] and row['protocol'] == 'TCP':
                if row['dst' if is_incoming else 'src'] == home_ip:
                    stream_id = make_stream_id(row['src'], row['src_port'], row['dst'], row['dst_port'])
                    if row['is_rst'] == 'False' and row['is_fin'] == 'False' and stream_id not in closed_set:
                        stream_set.add(stream_id)
                    else:
                        stream_set.discard(stream_id)
                        closed_set.add(stream_id)
                    packet_time = int(float(row['timestamp']) - start_timestamp)
                    connection_list.set_element(packet_time, len(stream_set))
    return connection_list.get_list()


def flow_plot(input_file, home_ip, website, is_incoming, color='red', ax=None):
    y = generate_flow_plot_data(input_file, home_ip, website, is_incoming)
    if ax is None:
        fig, ax = plt.subplots()
    ax.set_ylabel('# of open connections')
    ax.set_xlabel('time, s')
    plt.tight_layout()
    plt.plot(y, color=color)
    return ax


def cdf_plot(input_file, home_ip, website, is_incoming, color='red', ax=None):
    y = generate_flow_plot_data(input_file, home_ip, website, is_incoming)
    data = sorted(y)
    yvals = np.arange(len(data)) / float(len(data))
    if ax is None:
        fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Number of connections')
    plt.tight_layout()
    plt.plot(data, yvals, color=color)
    return ax


website = 'youtube.com'
everything = {
    'youtube_android_connections': {
        'file': 'el_manana/android_el_manana.csv',
        'ip': '192.168.0.4'
    },
    'youtube_chrome_connections': {
        'file': 'el_manana/out.csv',
        'ip': '10.0.2.15'
    },
    'youtube_chrome_autoplay_connections': {
        'file': 'dataset4/out.csv',
        'ip': '10.0.2.15'
    }
}


def run_all(show=False):
    overlay_flow_plot(show)
    overlay_cdf_plot(show)

    flow_plot(everything['youtube_chrome_autoplay_connections']['file'], everything['youtube_chrome_autoplay_connections']['ip'], website, True)
    plt.savefig('youtube_chrome_autoplay_connections_flow.svg')
    if show:
        plt.show()
    plt.clf()

    cdf_plot(everything['youtube_chrome_autoplay_connections']['file'], everything['youtube_chrome_autoplay_connections']['ip'], website, True)
    plt.savefig('youtube_chrome_autoplay_connections_cdf.svg')
    if show:
        plt.show()
    plt.clf()


def overlay_flow_plot(show=False):
    ax = flow_plot(everything['youtube_chrome_connections']['file'], everything['youtube_chrome_connections']['ip'], website, True, color='red')
    flow_plot(everything['youtube_android_connections']['file'], everything['youtube_android_connections']['ip'], website, True, color='blue', ax=ax)
    plt.savefig('youtube_android_chrome_flow_plot_over_time.svg')
    if show:
        plt.show()
    plt.clf()


def overlay_cdf_plot(show=False):
    ax = cdf_plot(everything['youtube_chrome_connections']['file'], everything['youtube_chrome_connections']['ip'], website, True, color='red')
    cdf_plot(everything['youtube_android_connections']['file'], everything['youtube_android_connections']['ip'], website, True, color='blue', ax=ax)
    plt.savefig('youtube_android_chrome_cdf_plot_over_time.svg')
    if show:
        plt.show()
    plt.clf()


run_all(False)
# overlay_flow_plot(True)
# overlay_cdf_plot(True)
