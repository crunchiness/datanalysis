import numpy as np
import csv
import datetime

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from shared import storage_formatter_factory


def remove_outliers(lengths_dict, low_end=3, high_end=3):
    elements = sorted(lengths_dict.items(), key=lambda x: x[0])
    while low_end != 0:
        if elements[0][1] > 1:
            elements[0] = (elements[0][0], elements[0][1] - 1)
        else:
            elements = elements[1:]
        low_end -= 1
    while high_end != 0:
        if elements[-1][1] > 1:
            elements[-1] = (elements[-1][0], elements[-1][1] - 1)
        else:
            elements = elements[:-1]
        high_end -= 1
    return dict(elements)


def length_bar_chart(lengths_dict, no_save=False, show=False, output_file=None):

    output_list = []

    # count packets
    total_packets = 0
    for key in lengths_dict.keys():
        total_packets += lengths_dict[key]

    threshold = total_packets / 100  # 1 percent

    # group counts
    current_key = []
    current_value = 0
    for key in sorted(lengths_dict.keys()):
        if lengths_dict[key] > threshold and current_value > 0:
            label = '-'.join(map(str, current_key))
            output_list.append((label, current_value))
            current_key = []
            current_value = 0
        if len(current_key) == 2:
            current_key.pop()
        current_key.append(key)
        current_value += lengths_dict[key]
        if current_value > threshold:
            label = '-'.join(map(str, current_key))
            output_list.append((label, current_value))
            current_key = []
            current_value = 0
    if current_value > 0:
        label = '-'.join(map(str, current_key))
        output_list.append((label, current_value))

    # draw the chart
    packets_counts = map(lambda x: x[1], output_list)
    labels = map(lambda x: x[0], output_list)
    ind = np.arange(len(output_list))  # the x locations for the groups

    width = 0.4  # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(ind, packets_counts, width, color='b')
    # add some text for labels, title and axes ticks
    ax.set_ylabel('Number of packets')
    ax.set_xlabel('Packet size in bytes')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(labels)

    plt.setp(plt.xticks()[1], rotation=-30)
    plt.tight_layout()

    if not no_save:
        if output_file is None:
            output_file = datetime.datetime.now().isoformat().replace(':', '_') + '__bar_chart.svg'
        plt.savefig(output_file)

    if show:
        plt.show()
    plt.clf()


def get_packet_length_data(input_file, home_ip, websites, is_incoming=True, ignore_acks=True, tso=False):
    lengths_dict = {}
    lengths = []

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if ignore_acks and row['is_ack'] == 'True':
                continue
            if row['protocol'] != 'TCP':
                continue
            if websites[0] in row['website']:
                if row['dst' if is_incoming else 'src'] == home_ip:
                    lengths.append(int(row['len']))
                    try:
                        lengths_dict[int(row['len'])] += 1
                    except KeyError:
                        lengths_dict[int(row['len'])] = 1

    # Remove some outliers
    lengths_dict = remove_outliers(lengths_dict)

    if tso:
        lengths = mock_tso(lengths)

    return sorted(lengths), lengths_dict


def mock_tso(data, mtu=1500, mss=1460):
    ip_overhead = 20
    new_data = []
    for element in data:
        if element > mtu:
            while element > mtu:
                new_data.append(mss + ip_overhead)
                element -= mss
            if element > 0:
                new_data.append(mss + ip_overhead)
        else:
            new_data.append(element)
    return new_data


def plot_packet_length(sorted_data, color='red', ax=None, use_log=False, storage_units=False):
    y_values = np.arange(len(sorted_data)) / float(len(sorted_data))
    if ax is None:
        fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Packet size in bytes')

    if use_log:
        plt.xscale('log')
        ax.set_xticks([0, 10, 100, 1024, 10 * 1024, 64 * 1024])

    if storage_units:
        ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))

    plt.tight_layout()

    plt.plot(sorted_data, y_values, color=color)
    return ax


def android_in_out(show=False):
    android_ip = '192.168.0.4'
    website = 'youtube.com'
    android_file = 'android_combined_dataset.csv'
    output_file = 'android_packet_length_in_out.svg'

    data_points_in, lengths_dict_in = get_packet_length_data(android_file, android_ip, website, is_incoming=True)
    ax = plot_packet_length(data_points_in, color='red')

    data_points_out, lengths_dict_out = get_packet_length_data(android_file, android_ip, website, is_incoming=False)
    plot_packet_length(data_points_out, color='blue', ax=ax)
    plt.savefig(output_file)
    if show:
        plt.show()


def chrome_in_out(show=False):
    chrome_ip = '10.0.2.15'
    website = 'youtube.com'
    chrome_file = 'dataset3/out.csv'
    output_file = 'chrome_packet_length_in_out.svg'

    data_points_in, lengths_dict_in = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=True)
    ax = plot_packet_length(data_points_in, color='red')

    data_points_out, lengths_dict_out = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=False)
    plot_packet_length(data_points_out, color='blue', ax=ax)
    plt.savefig(output_file)
    if show:
        plt.show()


def in_out_android_chrome(tso, is_incoming=True, show=False):
    android_ip = '192.168.0.4'
    android_file = 'android_combined_dataset.csv'
    chrome_ip = '10.0.2.15'
    chrome_file = 'dataset3/out.csv'
    output_file = '{}_packet_length_android_chrome{}.svg'.format('in' if is_incoming else 'out', '_tso' if tso else '')
    website = 'youtube.com'
    use_log = is_incoming and not tso

    data_points_android, lengths_dict_android = get_packet_length_data(android_file, android_ip, website, is_incoming=is_incoming, tso=tso)
    ax = plot_packet_length(data_points_android, color='blue', use_log=use_log, storage_units=use_log)

    data_points_chrome, lengths_dict_chrome = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=is_incoming, tso=tso)
    plot_packet_length(data_points_chrome, color='red', ax=ax, use_log=use_log, storage_units=use_log)
    plt.savefig(output_file)
    if show:
        plt.show()


# android_in_out()
# chrome_in_out()
in_out_android_chrome(True, is_incoming=True)
in_out_android_chrome(True, is_incoming=False)
in_out_android_chrome(False, is_incoming=True)
in_out_android_chrome(False, is_incoming=False)
