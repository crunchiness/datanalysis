import matplotlib.pyplot as plt
import csv

website = 'youtube.com'
# input_file = 'el_manana/android_el_manana.csv'
# input_file = 'el_manana/out.csv'
input_file = 'dataset4/out2.csv'
home_ip = '10.0.2.15'
# home_ip = '192.168.0.4'


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


def flow_plot(input_file, home_ip, website='youtube.com', is_incoming=True):
    stream_set = set()
    start_timestamp = None
    connection_list = GaplessList()

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            # set start_timestamp if not set
            start_timestamp = float(row['timestamp']) if start_timestamp is None else start_timestamp
            if website in row['website'] and row['protocol'] == 'TCP':
                key = 'dst' if is_incoming else 'src'
                if row[key] == home_ip and row['is_ack'] == 'False':
                    stream_id = make_stream_id(row['src'], row['src_port'], row['dst'], row['dst_port'])
                    stream_set.add(stream_id)
                    packet_time = int(float(row['timestamp']) - start_timestamp)
                    connection_list.set_element(packet_time, len(stream_set))
    return connection_list.get_list()

y = flow_plot(input_file, home_ip)
print y

fig, ax = plt.subplots()
ax.set_ylabel('TCP stream number')
ax.set_xlabel('time, s')

# print len(streams_list)
# print map(lambda x: len(x[1]), streams_list)

plt.plot(y, color='red')

plt.show()
