import csv

import math
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from shared import make_stream_id, pretty_name, storage_formatter_factory, make_storage_ticks


def generate_data(input_file, home_ip, website='youtube.com', protocols=None):
    if protocols is None:
        protocols = ['TCP']
    data_sums = {'all_streams': {'time': [], 'total': 0}}
    first_timestamp, duration = get_time_limits(input_file, website, home_ip, protocols)
    interval = 1  # second
    current_time = 0
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if website in row['website'] and (row['protocol'] in protocols):
                if row['dst'] == home_ip:
                    this_stream_id = make_stream_id(row)
                    if this_stream_id not in data_sums:
                        data_sums[this_stream_id] = {'time': map(lambda x: (x, 0), range(0, current_time)), 'total': 0}
                    timestamp = float(row['timestamp']) - first_timestamp
                    pkt_size = int(row['len'])
                    if timestamp < current_time + interval:
                        data_sums[this_stream_id]['total'] += pkt_size
                        data_sums['all_streams']['total'] += pkt_size
                    else:
                        for stream_id in data_sums.keys():
                            data_sums[stream_id]['time'].append((current_time, data_sums[stream_id]['total']))
                        current_time += interval
                        while timestamp > current_time:
                            for stream_id in data_sums.keys():
                                data_sums[stream_id]['time'].append((current_time, data_sums[stream_id]['total']))
                            current_time += interval
    return data_sums


def get_time_limits(input_file, website, home_ip, protocols):
    """
    Returns (first_time_stamp, duration)
    """
    first_time_stamp = 0
    last_time_stamp = 0
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if website in row['website'] and (row['protocol'] in protocols):
                if row['dst'] == home_ip:
                    if first_time_stamp == 0:
                        first_time_stamp = float(row['timestamp'])
                    last_time_stamp = float(row['timestamp'])
    return first_time_stamp, math.ceil(last_time_stamp - first_time_stamp)


def plot_accumulated_data(input_file, home_ip, website, platform, show=False):
    data = generate_data(input_file, home_ip, website=website, protocols=['TCP'])
    all_stream_data = data['all_streams']
    video_stream_id, video_stream_data = sorted(data.items(), cmp=lambda x, y: x[1]['total'] - y[1]['total'], reverse=True)[1]
    audio_stream_id, audio_stream_data = sorted(data.items(), cmp=lambda x, y: x[1]['total'] - y[1]['total'], reverse=True)[2]

    fig, ax = plt.subplots()
    ax.set_ylabel('accumulated data')
    ax.set_xlabel('time, s')

    fn, tix = make_storage_ticks(map(lambda x: x[1], all_stream_data['time']))
    ax.yaxis.set_major_formatter(fn)
    plt.yticks(tix)

    plt.xlim((0, 200))
    red_line = plt.plot(map(lambda x: x[1], all_stream_data['time']), color='red')
    blue_line = plt.plot(map(lambda x: x[1], video_stream_data['time']), color='blue')
    green_line = plt.plot(map(lambda x: x[1], audio_stream_data['time']), color='green')
    plt.legend([red_line[0], blue_line[0], green_line[0]], map(pretty_name(website), ['{} combined traffic', '{} video traffic', '{} audio traffic']), loc=4)
    plt.savefig('{}_{}_accumulated_data.svg'.format(website, platform))
    if show:
        plt.show()


def youtube_plot_accumulated_data():
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    website = 'youtube.com'
    plot_accumulated_data(chrome_file, chrome_ip, website, platform='chrome')
    plot_accumulated_data(android_file, android_ip, website, platform='android')

youtube_plot_accumulated_data()
