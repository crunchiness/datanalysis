import csv
import numpy as np

import matplotlib.pyplot as plt

from shared import make_stream_id, make_storage_ticks, scale_data


def generate_data(input_file, home_ip, website='youtube.com', is_incoming=True, num_values=5, protocols=None):
    if protocols is None:
        protocols = ['TCP']
    packet_sums = {}
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if website in row['website'] and (row['protocol'] in protocols):
                if row['dst' if is_incoming else 'src'] == home_ip:
                    try:
                        stream_id = make_stream_id(row)
                    except KeyError:
                        stream_id = make_stream_id(row)
                    try:
                        packet_sums[stream_id] += int(row['len'])
                    except KeyError:
                        packet_sums[stream_id] = int(row['len'])

    values = sorted(packet_sums.items(), cmp=lambda x, y: x[1]-y[1], reverse=True)
    values = map(lambda x: (x[0].split('-')[-1], x[1]), values)

    shortened = False
    if num_values < len(values):
        values = values[0:num_values - 1] + [('MIX', sum(map(lambda x: x[1], values[num_values - 1:])))]
        shortened = True
    return values, shortened


def top_flows_chart(chrome_input_file, android_input_file, chrome_home_ip, android_home_ip, website, is_incoming,
                    chrome_color='red', android_color='blue', ax=None):
    """
    Draws a plot of how much traffic transferred per flow.
    :return:
    """
    chrome_data, chrome_shortened = generate_data(chrome_input_file, chrome_home_ip, website, is_incoming)
    chrome_data = map(lambda x: x[1], chrome_data)
    android_data, android_shortened = generate_data(android_input_file, android_home_ip, website, is_incoming)
    android_data = map(lambda x: x[1], android_data)
    # android_data = scale_data(android_data, sum(chrome_data), 0.9)
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


def top_charts_mixed_protocols(input_file, home_ip, website, is_incoming=True):
    num_values = 5
    quic_data, shortened = generate_data(input_file, home_ip, website=website, is_incoming=True, num_values=num_values, protocols=['TCP', 'UDP'])

    # separate data and protocol names
    top_labels = map(lambda x: x[0], quic_data)
    data = map(lambda x: x[1], quic_data)

    # make labels
    labels = ['Conn. {0}'.format(i + 1) for i in xrange(num_values)]
    if shortened:
        labels[-1] = 'Rest'

    ind = np.array(map(lambda x: x, np.arange(num_values)))  # the x locations for the groups

    width = 0.5  # the width of the bars

    fig, ax = plt.subplots()
    chrome_bars = ax.bar(ind, data, width, color='red')

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Data transferred')
    ax.set_xlabel('Connection')

    fn, tix = make_storage_ticks(data)
    ax.yaxis.set_major_formatter(fn)
    plt.yticks(tix)

    ax.set_xticks(ind + width)
    ax.set_xticklabels(labels)

    def autolabel(bars, data):
        # attach some text labels
        for j, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    data[j], ha='center', va='bottom')

    autolabel(chrome_bars, top_labels)
    plt.tight_layout()


def do_quic_flows(show=False):
    chrome_ip = '10.0.2.15'
    quic_file = 'quic-manana/out.csv'
    website = 'youtube.com'
    top_charts_mixed_protocols(quic_file, chrome_ip, website, is_incoming=True)
    plt.savefig('quic_top_flows.svg')
    if show:
        plt.show()
    plt.clf()


def do_top_flows(show=False):
    chrome_ip = '10.0.2.15'
    android_ip = '192.168.0.4'
    website = 'youtube.com'
    chrome_file = 'el_manana/out.csv'
    android_file = 'el_manana/android_el_manana.csv'
    top_flows_chart(chrome_file, android_file, chrome_ip, android_ip, website, True)
    plt.savefig('top_flows_both.svg')
    if show:
        plt.show()
    plt.clf()


if __name__ == '__main__':
    do_top_flows()
    do_quic_flows(show=True)
