import csv
import math

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from shared import GaplessList, storage_formatter_factory, pretty_name


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


def cdf_plot(x_values, y_values, color='red', ax=None, is_log=False):
    if ax is None:
        fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    if is_log:
        plt.xscale('log')
        ax.set_xticks([0, 10, 100, 1024, 10 * 1024, 100 * 1024, 1024 * 1024, 10 * 1024 * 1024])
    else:
        ax.set_xticks([0, 256 * 1024, 512 * 1024, 768 * 1024, 1024 * 1024, 1.25 * 1024 * 1024, 1.5 * 1024 * 1024, 1.75 * 1024 * 1024, 2 * 1024 * 1024])
        # ax.set_xticks([0, 512 * 1024, 1024 * 1024, 1.5 * 1024 * 1024, 2 * 1024 * 1024, 2.5 * 1024 * 1024, 3 * 1024 * 1024, 3.5 * 1024 * 1024, 4 * 1024 * 1024])

    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory(unit_speed=True, decimal_places=2)))

    ax.set_ylabel('% Total')
    ax.set_xlabel('Bitrate')
    plt.tight_layout()
    line = plt.plot(x_values, y_values, color=color)
    plt.ylim(0, 1.0)
    return ax, line


def get_x_y_values(byte_rate_list):
    x_values = [byte_rate for byte_rate in xrange(int(math.ceil(max(byte_rate_list))) + 1)]
    y_values = [len(filter(lambda x: x <= byte_rate, byte_rate_list)) for byte_rate in x_values]
    y_values = map(lambda x: x / float(len(byte_rate_list)), y_values)
    return x_values, y_values


def bitrate_cdf_plot(android_file, chrome_file, android_ip, chrome_ip, website, quic_file=None, show=False):
    with_quic = quic_file is not None

    # generate data
    chrome_byte_rate_list = generate_bitrate_plot_data(chrome_file, chrome_ip, website, is_incoming=True)
    android_byte_rate_list = generate_bitrate_plot_data(android_file, android_ip, website, is_incoming=True)
    if with_quic:
        quic_byte_rate_list = generate_bitrate_plot_data(quic_file, chrome_ip, website, is_incoming=True, protocols=['TCP', 'UDP'])

    chrome_x_values, chrome_y_values = get_x_y_values(chrome_byte_rate_list)
    ax, line1 = cdf_plot(chrome_x_values, chrome_y_values, color='red', is_log=False)

    if with_quic:
        quic_x_values, quic_y_values = get_x_y_values(quic_byte_rate_list)
        ax, line2 = cdf_plot(quic_x_values, quic_y_values, color='green', ax=ax, is_log=False)

    android_x_values, android_y_values = get_x_y_values(android_byte_rate_list)
    ax, line3 = cdf_plot(android_x_values, android_y_values, color='blue', ax=ax, is_log=False)

    if with_quic:
        plt.legend([line1[0], line2[0], line3[0]], map(pretty_name(website), ['{} Chrome (TCP)', '{} Chrome (QUIC)', '{} Android (TCP)']), loc=4)
    else:
        plt.legend([line1[0], line3[0]], map(pretty_name(website), ['{} Chrome (TCP)', '{} Android (TCP)']), loc=4)
    plt.savefig('{}_android_bitrate.svg'.format(website))
    if show:
        plt.show()
    plt.clf()

    ax, line1 = cdf_plot(chrome_x_values, chrome_y_values, color='red', is_log=True)
    if with_quic:
        ax, line2 = cdf_plot(quic_x_values, quic_y_values, color='green', ax=ax, is_log=True)
    ax, line3 = cdf_plot(android_x_values, android_y_values, color='blue', ax=ax, is_log=True)
    if with_quic:
        plt.legend([line1[0], line2[0], line3[0]], map(pretty_name(website), ['{} Chrome (TCP)', '{} Chrome (QUIC)', '{} Android (TCP)']), loc=4)
    else:
        plt.legend([line1[0], line3[0]], map(pretty_name(website), ['{} Chrome (TCP)', '{} Android (TCP)']), loc=4)
    plt.savefig('{}_android_bitrate_log.svg'.format(website))
    if show:
        plt.show()
    plt.clf()


def youtube_cdf_plot(show=False):
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    quic_file = 'quic-manana/out.csv'
    website = 'youtube.com'
    bitrate_cdf_plot(android_file, chrome_file, android_ip, chrome_ip, website, quic_file, show)


def netflix_cdf_plot(show=False):
    android_file = 'hannibal_dump/android.csv'
    android_ip = '192.168.1.6'
    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_ip = '192.168.1.2'
    website = 'netflix.com'
    bitrate_cdf_plot(android_file, chrome_file, android_ip, chrome_ip, website, show=show)


if __name__ == '__main__':
    youtube_cdf_plot(show=False)
    netflix_cdf_plot(show=False)
