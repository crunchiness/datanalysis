import csv
import math

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from shared import GaplessList, scale_data


def generate_flow_plot_data(input_file, home_ip, website='youtube.com', is_incoming=True):
    start_timestamp = None
    byte_rate_list = GaplessList(fill=0)

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            # set start_timestamp if not set
            start_timestamp = float(row['timestamp']) if start_timestamp is None else start_timestamp
            if website in row['website'] and row['protocol'] == 'TCP':
                if row['dst' if is_incoming else 'src'] == home_ip:
                    packet_time = int(float(row['timestamp']) - start_timestamp)
                    byte_rate_list.increment_element(packet_time, int(row['len']))
    return byte_rate_list.get_list()


def cdf_plot(byte_rate_list, color='red', ax=None, is_log=False):
    x_values = [byte_rate for byte_rate in xrange(int(math.ceil(max(byte_rate_list))) + 1)]
    y_values = [len(filter(lambda x: x <= byte_rate, byte_rate_list)) for byte_rate in x_values]
    y_values = map(lambda x: x / float(len(byte_rate_list)), y_values)

    if ax is None:
        fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    if is_log:
        plt.xscale('log')
        ax.set_xticks([0, 10, 100, 1024, 10 * 1024, 100 * 1024, 1024 * 1024, 10 * 1024 * 1024])
    else:
        ax.set_xticks([0, 200 * 1024, 400 * 1024, 600 * 1024, 800 * 1024, 1024 * 1024, 1.2 * 1024 * 1024, 1.4 * 1024 * 1024])

    def storage_formatter(y, pos):
        if y < 1024:
            unit = 'B/s'
            value = y
        elif y < 1024 * 1024:
            unit = 'KB/s'
            value = y / 1024.
        else:
            unit = 'MB/s'
            value = y / float(1024 * 1024)
        if round(value) == value:
            return '{0:.0f} {1}'.format(value, unit)
        else:
            return '{0:.1f} {1}'.format(value, unit)
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter))

    ax.set_ylabel('% Total')
    ax.set_xlabel('Bitrate')
    plt.tight_layout()
    plt.plot(x_values, y_values, color=color)
    plt.ylim(0.5, 1.0)
    return ax


def bitrate_cdf_plot(show=False):
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    website = 'youtube.com'

    chrome_byte_rate_list = generate_flow_plot_data(chrome_file, chrome_ip, website, is_incoming=True)
    android_byte_rate_list = generate_flow_plot_data(android_file, android_ip, website, is_incoming=True)
    # android_byte_rate_list = scale_data(android_byte_rate_list, sum(chrome_byte_rate_list), change=0.9)

    ax = cdf_plot(chrome_byte_rate_list, color='red', is_log=False)
    cdf_plot(android_byte_rate_list, color='blue', ax=ax, is_log=False)
    plt.savefig('youtube_android_bitrate.svg')
    if show:
        plt.show()
    plt.clf()

    ax = cdf_plot(chrome_byte_rate_list, color='red', is_log=True)
    cdf_plot(android_byte_rate_list, color='blue', ax=ax, is_log=True)
    plt.savefig('youtube_android_bitrate.svg')
    if show:
        plt.show()
    plt.clf()

bitrate_cdf_plot()
