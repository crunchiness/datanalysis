import matplotlib.pyplot as plt
import numpy as np
import csv
import math
from shared import GaplessList, make_stream_id


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


def flow_plot(input_file, home_ip, website, is_incoming, color='red', ax=None):
    y = generate_flow_plot_data(input_file, home_ip, website, is_incoming)
    if ax is None:
        fig, ax = plt.subplots()
    ax.set_ylabel('# of open connections')
    ax.set_xlabel('time, s')
    plt.tight_layout()
    plt.plot(y, color=color)
    return ax


def cdf_plot(input_file, home_ip, website, is_incoming, color='red', ax=None):
    y = generate_flow_plot_data(input_file, home_ip, website, is_incoming)
    data = sorted(y)
    yvals = np.arange(len(data)) / float(len(data))
    if ax is None:
        fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Number of connections')
    plt.tight_layout()
    plt.plot(data, yvals, color=color)
    return ax


website = 'youtube.com'
everything = {
    'youtube_android_connections': {
        'file': 'el_manana/android_el_manana.csv',
        'ip': '192.168.0.4'
    },
    'youtube_chrome_connections': {
        'file': 'el_manana/out.csv',
        'ip': '10.0.2.15'
    },
    'youtube_chrome_autoplay_connections': {
        'file': 'dataset4/out.csv',
        'ip': '10.0.2.15'
    }
}


def run_all(show=False):
    overlay_flow_plot(show)
    overlay_cdf_plot(show)

    flow_plot(everything['youtube_chrome_autoplay_connections']['file'], everything['youtube_chrome_autoplay_connections']['ip'], website, True)
    plt.savefig('youtube_chrome_autoplay_connections_flow.svg')
    if show:
        plt.show()
    plt.clf()

    cdf_plot(everything['youtube_chrome_autoplay_connections']['file'], everything['youtube_chrome_autoplay_connections']['ip'], website, True)
    plt.savefig('youtube_chrome_autoplay_connections_cdf.svg')
    if show:
        plt.show()
    plt.clf()


def overlay_flow_plot(show=False):
    ax = flow_plot(everything['youtube_chrome_connections']['file'], everything['youtube_chrome_connections']['ip'], website, True, color='red')
    flow_plot(everything['youtube_android_connections']['file'], everything['youtube_android_connections']['ip'], website, True, color='blue', ax=ax)
    plt.savefig('youtube_android_chrome_flow_plot_over_time.svg')
    if show:
        plt.show()
    plt.clf()


def overlay_cdf_plot(show=False):
    ax = cdf_plot(everything['youtube_chrome_connections']['file'], everything['youtube_chrome_connections']['ip'], website, True, color='red')
    cdf_plot(everything['youtube_android_connections']['file'], everything['youtube_android_connections']['ip'], website, True, color='blue', ax=ax)
    plt.savefig('youtube_android_chrome_cdf_plot_over_time.svg')
    if show:
        plt.show()
    plt.clf()


# def videos_10(show=False):
#     chrome_ip = '10.0.2.15'
#     chrome_file_name = 'videos-10/chrome-10/video-{0}/out.csv'
#     chrome_numbers = []
#     for i in range(1, 11):
#         file_name = chrome_file_name.format(i)
#         chrome_data = generate_flow_plot_data(file_name, chrome_ip, website, True)
#         chrome_numbers.append(sum(chrome_data) / float(len(chrome_data)))
#         cdf_plot(file_name, chrome_ip, website, True, color='red')
#         plt.savefig('chrome_video-{0}.svg'.format(i))
#         if show:
#             plt.show()
#         plt.clf()
#     print sorted(chrome_numbers)
#     android_ip = '192.168.0.4'
#     android_file_name = 'videos-10/android-10/video-{0}/out.csv'
#     android_numbers = []
#     for i in range(1, 11):
#         file_name = android_file_name.format(i)
#         android_data = generate_flow_plot_data(file_name, android_ip, website, True)
#         android_numbers.append(sum(android_data) / float(len(android_data)))
#         cdf_plot(file_name, android_ip, website, True, color='red')
#         plt.savefig('android_video-{0}.svg'.format(i))
#         if show:
#             plt.show()
#         plt.clf()
#     print sorted(android_numbers)


def videos_10(show=False):
    chrome_ip = '10.0.2.15'
    chrome_file_name = 'videos-10/chrome-10/video-{0}/out.csv'
    chrome_numbers = []
    for i in range(1, 11):
        file_name = chrome_file_name.format(i)
        chrome_data = generate_flow_plot_data(file_name, chrome_ip, website, True)
        chrome_numbers.append(sum(chrome_data) / float(len(chrome_data)))
    chrome_numbers = sorted(chrome_numbers)

    android_ip = '192.168.0.4'
    android_file_name = 'videos-10/android-10/video-{0}/out.csv'
    android_numbers = []
    for i in range(1, 11):
        file_name = android_file_name.format(i)
        android_data = generate_flow_plot_data(file_name, android_ip, website, True)
        android_numbers.append(sum(android_data) / float(len(android_data)))
    android_numbers = sorted(android_numbers)

    chrome_y_values = [len(filter(lambda x: x <= element, chrome_numbers)) for element in chrome_numbers]
    chrome_y_values = map(lambda x: x / float(len(chrome_y_values)), chrome_y_values)

    android_y_values = [len(filter(lambda x: x <= element, android_numbers)) for element in android_numbers]
    android_y_values = map(lambda x: x / float(len(android_y_values)), android_y_values)

    fig, ax = plt.subplots()
    ax.set_ylabel('% Total')
    ax.set_xlabel('# of connections per video (average over duration)')
    plt.plot(chrome_numbers, chrome_y_values, color='red')
    plt.plot(android_numbers, android_y_values, color='blue')
    plt.ylim(0, 1)
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    plt.tight_layout()
    plt.savefig('android_chrome_connections_10_videos.svg')

    if show:
        plt.show()
    plt.clf()

# run_all(False)
# overlay_flow_plot(True)
# overlay_cdf_plot(True)
# videos_10()
videos_10()
