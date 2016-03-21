import csv
import math

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from shared import GaplessList, storage_formatter_factory


def generate_bitrate_plot_data(input_file, home_ip, website='youtube.com', is_incoming=True, protocols=None):
    if protocols is None:
        protocols = ['TCP']
    start_timestamp = None
    byte_rate_list = GaplessList(fill=0)

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            # set start_timestamp if not set
            start_timestamp = float(row['timestamp']) if start_timestamp is None else start_timestamp
            if website in row['website'] and (row['protocol'] in protocols):
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
        ax.set_xticks([0, 256 * 1024, 512 * 1024, 768 * 1024, 1024 * 1024, 1.25 * 1024 * 1024, 1.5 * 1024 * 1024, 1.75 * 1024 * 1024, 2 * 1024 * 1024])

    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory(unit_speed=True)))

    ax.set_ylabel('% Total')
    ax.set_xlabel('Bitrate')
    plt.tight_layout()
    line = plt.plot(x_values, y_values, color=color)
    plt.ylim(0.5, 1.0)
    return ax, line


def bitrate_cdf_plot(show=False):
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    quic_file = 'quic-manana/out.csv'
    website = 'youtube.com'

    chrome_byte_rate_list = generate_bitrate_plot_data(chrome_file, chrome_ip, website, is_incoming=True)
    android_byte_rate_list = generate_bitrate_plot_data(android_file, android_ip, website, is_incoming=True)
    quic_byte_rate_list = generate_bitrate_plot_data(quic_file, chrome_ip, website, is_incoming=True, protocols=['TCP', 'UDP'])

    ax, line1 = cdf_plot(chrome_byte_rate_list, color='red', is_log=False)
    ax, line2 = cdf_plot(quic_byte_rate_list, color='green', ax=ax, is_log=False)
    ax, line3 = cdf_plot(android_byte_rate_list, color='blue', ax=ax, is_log=False)

    plt.legend([line1[0], line2[0], line3[0]], ['YouTube Chrome (TCP)', 'YouTube Chrome (QUIC)', 'YouTube Android (TCP)'], loc=4)
    plt.savefig('youtube_android_bitrate.svg')
    if show:
        plt.show()
    plt.clf()

    ax, line1 = cdf_plot(chrome_byte_rate_list, color='red', is_log=True)
    ax, line2 = cdf_plot(quic_byte_rate_list, color='green', ax=ax, is_log=True)
    ax, line3 = cdf_plot(android_byte_rate_list, color='blue', ax=ax, is_log=True)
    plt.legend([line1[0], line2[0], line3[0]], ['YouTube Chrome (TCP)', 'YouTube Chrome (QUIC)', 'YouTube Android (TCP)'], loc=4)
    plt.savefig('youtube_android_bitrate_log.svg')
    if show:
        plt.show()
    plt.clf()


def bitrate_quic_tcp():
    pass

if __name__ == '__main__':
    bitrate_cdf_plot(show=False)
