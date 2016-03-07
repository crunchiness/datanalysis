import csv
import numpy as np

import matplotlib.pyplot as plt

from shared import make_stream_id, make_storage_ticks


def generate_data(input_file, home_ip, website='youtube.com', is_incoming=True, num_values=5):
    packet_sums = {}
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if website in row['website'] and row['protocol'] == 'TCP':
                if row['dst' if is_incoming else 'src'] == home_ip:
                    stream_id = make_stream_id(row['src'], row['src_port'], row['dst'], row['dst_port'])
                    try:
                        packet_sums[stream_id] += int(row['len'])
                    except KeyError:
                        packet_sums[stream_id] = int(row['len'])
    values = sorted(packet_sums.values(), reverse=True)
    shortened = False
    if num_values < len(values):
        values = values[0:num_values - 1] + [sum(values[num_values - 1:])]
        shortened = True
    return values, shortened


def scale_data(data, total, change=1.):
    return map(lambda x: x * change * total / float(sum(data)), data)


def top_flows_chart(chrome_input_file, android_input_file, chrome_home_ip, android_home_ip, website, is_incoming, chrome_color='red', android_color='blue', ax=None):
    """
    Draws a plot of how much traffic transferred per flow.
    :return:
    """
    chrome_data, chrome_shortened = generate_data(chrome_input_file, chrome_home_ip, website, is_incoming)
    android_data, android_shortened = generate_data(android_input_file, android_home_ip, website, is_incoming)
    android_data = scale_data(android_data, sum(chrome_data), 0.9)
    num_values = max(len(chrome_data), len(android_data))
    shortened = chrome_shortened if len(chrome_data) > len(android_data) else android_shortened

    labels = ['Conn. {0}'.format(i + 1) for i in xrange(num_values)]
    if shortened:
        labels[-1] = 'Rest'
    ind = np.array(map(lambda x: x + 0.15, np.arange(num_values)))  # the x locations for the groups

    width = 0.35  # the width of the bars

    if ax is None:
        fig, ax = plt.subplots()
    chrome_bars = ax.bar(ind, chrome_data, width, color=chrome_color)
    android_bars = ax.bar(ind + width, android_data, width, color=android_color)

    ax.legend((chrome_bars[0], android_bars[0]), ('YouTube Chrome', 'YouTube Android'))

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Data transferred')
    ax.set_xlabel('Connection')

    fn, tix = make_storage_ticks(chrome_data)
    ax.yaxis.set_major_formatter(fn)
    plt.yticks(tix)

    ax.set_xticks(ind + width)
    ax.set_xticklabels(labels)

    plt.tight_layout()

chrome_ip = '10.0.2.15'
android_ip = '192.168.0.4'
website = 'youtube.com'
chrome_file = 'el_manana/out.csv'
android_file = 'el_manana/android_el_manana.csv'
top_flows_chart(chrome_file, android_file, chrome_ip, android_ip, website, True)
plt.savefig('top_flows_both.svg')
plt.show()
