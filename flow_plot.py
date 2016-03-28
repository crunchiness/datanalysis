import numpy as np
import csv

import matplotlib.pyplot as plt

from shared import GaplessList, make_stream_id, pretty_name


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
                    stream_id = make_stream_id(row)
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


def flow_plot_both(android_file, android_ip, chrome_file, chrome_ip, website, is_incoming=True, show=False):
    android_y = generate_flow_plot_data(android_file, android_ip, website, is_incoming)
    chrome_y = generate_flow_plot_data(chrome_file, chrome_ip, website, is_incoming)
    fig, ax = plt.subplots()
    ax.set_ylabel('# of open connections')
    ax.set_xlabel('time, s')
    plt.tight_layout()
    android_line = plt.plot(android_y, color='blue')
    chrome_line = plt.plot(chrome_y, color='red')
    plt.legend([android_line[0], chrome_line[0]], map(pretty_name(website), ['{} Android connections', '{} Chrome connections']))
    plt.savefig(pretty_name(website)('{}_android_chrome_flow_plot_over_time.svg'))
    if show:
        plt.show()
    plt.clf()


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


def cdf_plot_both(android_file, android_ip, chrome_file, chrome_ip, website, is_incoming=True, show=False):
    android_y_values = generate_flow_plot_data(android_file, android_ip, website, is_incoming)
    android_x_values = sorted(android_y_values)
    android_y_values = np.arange(len(android_x_values)) / float(len(android_x_values))

    chrome_y_values = generate_flow_plot_data(chrome_file, chrome_ip, website, is_incoming)
    chrome_x_values = sorted(chrome_y_values)
    chrome_y_values = np.arange(len(chrome_x_values)) / float(len(chrome_x_values))

    fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Number of connections')
    plt.tight_layout()

    android_line = plt.plot(android_x_values, android_y_values, color='blue')
    chrome_line = plt.plot(chrome_x_values, chrome_y_values, color='red')

    loc = 2 if website == 'youtube.com' else 4
    plt.legend([android_line[0], chrome_line[0]], map(pretty_name(website), ['{} Android', '{} Chrome']), loc=loc)
    plt.savefig(pretty_name(website)('{}_android_chrome_connections_cdf.svg'))
    if show:
        plt.show()
    plt.clf()


def overlay_flow_plot(android_file, chrome_file, android_ip, chrome_ip, website, show=False):
    ax = flow_plot(chrome_file, chrome_ip, website, True, color='red')
    flow_plot(android_file, android_ip, website, True, color='blue', ax=ax)
    plt.savefig('{}_android_chrome_flow_plot_over_time.svg'.format(website))
    if show:
        plt.show()
    plt.clf()


def overlay_cdf_plot(android_file, chrome_file, android_ip, chrome_ip, website, show=False):
    ax = cdf_plot(chrome_file, chrome_ip, website, True, color='red')
    cdf_plot(android_file, android_ip, website, True, color='blue', ax=ax)
    plt.savefig('{}_android_chrome_cdf_plot_over_time.svg'.format(website))
    if show:
        plt.show()
    plt.clf()


def netflix_overlay_flow_plot(show=False):
    android_file = 'hannibal_dump/android.csv'
    android_ip = '192.168.1.6'
    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_ip = '192.168.1.2'
    website = 'netflix.com'
    flow_plot_both(android_file, android_ip, chrome_file, chrome_ip, website, show=show)


def netflix_overlay_cdf_plot(show=False):
    android_file = 'hannibal_dump/android.csv'
    android_ip = '192.168.1.6'
    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_ip = '192.168.1.2'
    website = 'netflix.com'
    cdf_plot_both(android_file, android_ip, chrome_file, chrome_ip, website, show=show)


# YouTube
def youtube_videos_10(show=False):
    chrome_ip = '10.0.2.15'
    chrome_file_name = 'videos-10/chrome-10/video-{0}/out.csv'
    website = 'youtube.com'
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


def youtube_overlay_flow_plot(show=False):
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    website = 'youtube.com'
    flow_plot_both(android_file, android_ip, chrome_file, chrome_ip, website, show=show)


def youtube_overlay_cdf_plot(show=False):
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    website = 'youtube.com'
    cdf_plot_both(android_file, android_ip, chrome_file, chrome_ip, website, show=show)


def youtube_autoplay_cdf(show=False):
    chrome_autoplay_file = 'dataset4/out.csv'
    chrome_autoplay_ip = '10.0.2.15'
    website = 'youtube.com'
    cdf_plot(chrome_autoplay_file, chrome_autoplay_ip, website, True)
    plt.savefig('YouTube_chrome_autoplay_connections_cdf.svg')
    if show:
        plt.show()
    plt.clf()


def youtube_autoplay_flow_plot(show=False):
    chrome_autoplay_file = 'dataset4/out.csv'
    chrome_autoplay_ip = '10.0.2.15'
    website = 'youtube.com'
    flow_plot(chrome_autoplay_file, chrome_autoplay_ip, website, True)
    plt.savefig('YouTube_chrome_autoplay_connections_flow.svg')
    if show:
        plt.show()
    plt.clf()

if __name__ == '__main__':
    netflix_overlay_flow_plot(show=False)
    netflix_overlay_cdf_plot(show=False)
    youtube_overlay_cdf_plot(show=False)
    youtube_overlay_flow_plot(show=False)
    youtube_autoplay_flow_plot(show=False)
    youtube_autoplay_cdf(show=False)
    youtube_videos_10(show=False)
