import matplotlib.pyplot as plt
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


def flow_plot(input_file, home_ip, website, is_incoming):
    y = generate_flow_plot_data(input_file, home_ip, website, is_incoming)
    fig, ax = plt.subplots()
    ax.set_ylabel('# of open connections')
    ax.set_xlabel('time, s')
    plt.plot(y, color='red')


def run_all(show=False):
    website = 'youtube.com'
    everything = {
        # 'youtube_android_connections': {
        #     'file': 'el_manana/android_el_manana.csv',
        #     'ip': '192.168.0.4'
        # },
        'youtube_chrome_connections': {
            'file': 'el_manana/out.csv',
            'ip': '10.0.2.15'
        },
        'youtube_chrome_autoplay_connections': {
            'file': 'dataset4/out.csv',
            'ip': '10.0.2.15'
        }
    }

    for key in everything:
        flow_plot(everything[key]['file'], everything[key]['ip'], website, True)
        plt.savefig('{}.svg'.format(key))
        if show:
            plt.show()
        plt.clf()

run_all(True)
