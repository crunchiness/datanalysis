import csv
import math

import matplotlib.pyplot as plt

from shared import make_stream_id, pretty_name, make_storage_ticks


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

    red_line = plt.plot(map(lambda x: x[1], all_stream_data['time']), color='red')
    blue_line = plt.plot(map(lambda x: x[1], video_stream_data['time']), color='blue')
    green_line = plt.plot(map(lambda x: x[1], audio_stream_data['time']), color='green')
    plt.legend([red_line[0], blue_line[0], green_line[0]], map(pretty_name(website), ['{} combined traffic', '{} video traffic', '{} audio traffic']), loc=4)
    plt.savefig('{}_{}_accumulated_data.svg'.format(website, platform))
    if show:
        plt.show()


def plot_accumulated_data_netflix(input_file, home_ip, website, platform, y_limit, show=False):
    data = generate_data(input_file, home_ip, website=website, protocols=['TCP'])
    all_stream_data = data['all_streams']
    # all_stream_data['time'] = filter(lambda x: x[0] < 50, all_stream_data['time'])
    if platform == 'android':
        first_stream_id, first_stream_data = sorted(data.items(), cmp=lambda x, y: x[1]['total'] - y[1]['total'], reverse=True)[1]
        second_stream_id, second_stream_data = sorted(data.items(), cmp=lambda x, y: x[1]['total'] - y[1]['total'], reverse=True)[2]
        third_stream_id, third_stream_data = sorted(data.items(), cmp=lambda x, y: x[1]['total'] - y[1]['total'], reverse=True)[3]

    fig, ax = plt.subplots()
    ax.set_ylabel('accumulated data')
    ax.set_xlabel('time, s')

    if y_limit is not None:
        fn, tix = make_storage_ticks(filter(lambda x: x < y_limit, map(lambda x: x[1], all_stream_data['time'])))
    else:
        fn, tix = make_storage_ticks(map(lambda x: x[1], all_stream_data['time']))
    ax.yaxis.set_major_formatter(fn)
    plt.yticks(tix)

    red_line = plt.plot(map(lambda x: x[1], all_stream_data['time']), color='red')
    if platform == 'android':
        blue_line = plt.plot(map(lambda x: x[1], first_stream_data['time']), color='blue')
        green_line = plt.plot(map(lambda x: x[1], second_stream_data['time']), color='green')
        orange_line = plt.plot(map(lambda x: x[1], third_stream_data['time']), color='orange')
        plt.legend([red_line[0], blue_line[0], green_line[0], orange_line[0]], map(pretty_name(website), ['{} combined traffic', '{} first stream', '{} second stream', '{} third stream']))
    else:
        plt.legend([red_line[0]], map(pretty_name(website), ['{} combined traffic']))
    if y_limit is not None:
        plt.ylim(0, y_limit)
    plt.savefig('{}_{}_accumulated_data{}.svg'.format(website, platform, '_limited' if y_limit is not None else ''))
    if show:
        plt.show()


def youtube_plot_accumulated_data(show=False):
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_file = 'el_manana/out.csv'
    chrome_ip = '10.0.2.15'
    website = 'youtube.com'
    plot_accumulated_data(chrome_file, chrome_ip, website, platform='chrome', show=show)
    plot_accumulated_data(android_file, android_ip, website, platform='android', show=show)


def netflix_plot_accumulated_data(y_limit=None, show=False):
    android_file = 'hannibal_dump/android.csv'
    android_ip = '192.168.1.6'
    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_ip = '192.168.1.2'
    website = 'netflix.com'
    plot_accumulated_data_netflix(chrome_file, chrome_ip, website, 'chrome', y_limit, show=show)
    plot_accumulated_data_netflix(android_file, android_ip, website, 'android', y_limit, show=show)

if __name__ == '__main__':
    youtube_plot_accumulated_data(show=False)
    netflix_plot_accumulated_data(show=False)
    netflix_plot_accumulated_data(y_limit=320 * 1024 * 1024, show=False)
