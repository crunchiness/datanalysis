import matplotlib.pyplot as plt
import csv

website = 'youtube.com'
# input_file = 'el_manana/android_el_manana.csv'
# input_file = 'el_manana/out.csv'
input_file = 'dataset4/out2.csv'
home_ip = '10.0.2.15'
# home_ip = '192.168.0.4'


streams = {}
# streams = {
#     1231255: ''
# }
# streams = [(123123, 'stream id')]

with open(input_file, 'rb') as csv_file:
    data_reader = csv.DictReader(csv_file, delimiter=',')
    for row in data_reader:
        if 'youtube.com' in row['website'] and row['protocol'] == 'TCP':
            # incoming
            if row['dst'] == home_ip and row['is_ack'] == 'False':
            # # outgoing
            # if row['src'] == home_ip and row['is_ack'] == 'False':
                stream_id = row['src'] + row['src_port'] + row['dst'] + row['dst_port']
                try:
                    streams[stream_id].append(float(row['timestamp']))
                except KeyError:
                    streams[stream_id] = [float(row['timestamp'])]
fig, ax = plt.subplots()
ax.set_ylabel('TCP stream number')
ax.set_xlabel('time, s')


def make_lists(streams_dict):
    list_of_tuples = []
    sorted_streams = sorted(streams_dict.values(), key=lambda timestamps: timestamps[0])
    first_timestamp = sorted_streams[0][0]
    i = 0
    for stream in sorted_streams:
        if len(stream) > 5:
            indices = [i] * len(stream)
            list_of_tuples.append((indices, map(lambda x: x - first_timestamp, stream)))
            i += 1
    return list_of_tuples

streams_list = make_lists(streams)

# print len(streams_list)
# print map(lambda x: len(x[1]), streams_list)

for indices, stream in streams_list:
    plt.plot(stream, indices, 'ro')
    plt.plot(stream, indices, 'r-')

plt.show()
