import matplotlib.pyplot as plt
import csv


def plot_thing(input_file, home_ip, plot_all=True, plot_second=False, plot_rest=False, website='youtube.com', is_down=True, colors=None, chart=None, names=None):
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
                    stream_id = row['src'] + row['src_port'] + row['dst'] + row['dst_port']
                    try:
                        streams[stream_id].append(float(row['timestamp']))
                    except KeyError:
                        streams[stream_id] = [float(row['timestamp'])]

    sorted_streams = sorted(streams.values(), key=lambda timestamps: timestamps[0])
    first_timestamp = sorted_streams[0][0]
    sorted_streams = map(lambda stream: map(lambda ts: ts - first_timestamp, stream), sorted_streams)
    all_streams = reduce(lambda x, y: x + y, sorted_streams, [])

    def put_in_bins(time_stamps):
        time_bins = []
        for time_stamp in time_stamps:
            bin_index = int(time_stamp / window)
            try:
                time_bins[bin_index] += 1
            except IndexError:
                while len(time_bins) != bin_index:
                    time_bins.append(0)
                time_bins.append(1)
        return time_bins

    plot_line_list = []
    plot_name_list = []
    if chart is None:
        fig, ax = plt.subplots()
        ax.set_ylabel('# of packets')
        ax.set_xlabel('time, s')
    else:
        fig, ax, plot_line_list, plot_name_list = chart

    top_stream = sorted(sorted_streams, key=lambda stream: len(stream), reverse=True)[0]
    second_top_stream = reduce(lambda x, y: x + y, sorted(sorted_streams, key=lambda stream: len(stream), reverse=True)[1:], [])

    i = 0
    if plot_all:
        red_line = plt.plot(put_in_bins(all_streams), colors[i] + '-')
        plot_line_list.append(red_line[0])
        plot_name_list.append(names[i])
        i += 1
    if plot_second:
        blue_line = plt.plot(put_in_bins(top_stream), colors[i] + '-')
        plot_line_list.append(blue_line[0])
        plot_name_list.append(names[i])
        i += 1
    if plot_rest:
        green_line = plt.plot(put_in_bins(second_top_stream), colors[i] + '-')
        plot_line_list.append(green_line[0])
        plot_name_list.append(names[i])
        i += 1
    plt.legend(tuple(plot_line_list), tuple(plot_name_list))
    return fig, ax, plot_line_list, plot_name_list

# input_file = 'el_manana/out.csv'
# input_file = 'dataset4/out2.csv'
android = {
    'file': 'el_manana/android_el_manana.csv',
    'ip': '192.168.0.4'
}
chrome = {
    'file': 'el_manana/out.csv',
    'ip': '10.0.2.15'
}

chart = plot_thing(chrome['file'], chrome['ip'], colors=['r'], is_down=False, names=['YouTube Chrome'])
plot_thing(android['file'], android['ip'], colors=['b'], is_down=False, chart=chart, names=['YouTube Android'])

plt.show()
