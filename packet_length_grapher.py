import numpy as np
import csv
import datetime

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from shared import make_stream_id, storage_formatter_factory, pretty_name


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


def make_dict(lengths):
    length_dict = {}
    for length in lengths:
        try:
            length_dict[length] += 1
        except KeyError:
            length_dict[length] = 1
    return length_dict


def length_bar_chart(lengths, no_save=False, show=False, output_file=None):
    triple_values = []
    triple_colors = ['purple', 'green', 'yellow']
    triple_labels = ['video', 'audio', 'rest']

    # count packets
    total_packets = sum(map(lambda x: sum(x[1].values()), lengths))

    # threshold = total_packets / 20  # 5 percent
    threshold = total_packets / 100  # 1 percent

    # group counts
    current_key = []
    current_values = {'video': 0, 'audio': 0, 'rest': 0}
    for length, details in lengths:
        if sum(details.values()) > threshold and sum(current_values.values()) > 0:
            label = '-'.join(map(str, current_key))
            triple_values.append((label, current_values))
            current_key = []
            current_values = {'video': 0, 'audio': 0, 'rest': 0}
        if len(current_key) == 2:
            current_key.pop()
        current_key.append(length)
        current_values['video'] += details['video'] if 'video' in details else 0
        current_values['audio'] += details['audio'] if 'audio' in details else 0
        current_values['rest'] += details['rest'] if 'rest' in details else 0
        if sum(current_values.values()) > threshold:
            label = '-'.join(map(str, current_key))
            triple_values.append((label, current_values))
            current_key = []
            current_values = {'video': 0, 'audio': 0, 'rest': 0}
    if sum(current_values.values()) > 0:
        label = '-'.join(map(str, current_key))
        triple_values.append((label, current_values))
    matrix = np.column_stack(tuple(map(lambda x: x[1].values(), triple_values)))

    # draw the chart
    # packets_counts = map(lambda x: x[1], triple_values)
    labels = map(lambda x: x[0], triple_values)
    ind = np.arange(len(triple_values))  # the x locations for the groups

    width = 0.5  # the width of the bars

    fig, ax = plt.subplots()
    # add some text for labels, title and axes ticks
    ax.set_ylabel('Number of packets')
    ax.set_xlabel('Packet size in bytes')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(labels)

    bar_properties = create_subplot(matrix, triple_colors, ax, width)

    plt.setp(plt.xticks()[1], rotation=-30)
    plt.tight_layout()

    fig.legend(bar_properties,
               triple_labels,
               bbox_to_anchor=(0.5, 0),
               loc='lower center',
               ncol=4)
    if not no_save:
        if output_file is None:
            output_file = datetime.datetime.now().isoformat().replace(':', '_') + '__bar_chart.svg'
        plt.savefig(output_file)

    if show:
        plt.show()
    plt.clf()


def get_packet_length_data(input_file, home_ip, website, is_incoming=True, ignore_acks=True, tso=False, need_ids=False, protocols=None):
    # lengths_dict = {}
    if protocols is None:
        protocols = ['TCP']
    lengths = []
    ids = [] if need_ids else None

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if ignore_acks and row['is_ack'] == 'True':
                continue
            if website in row['website'] and (row['protocol'] in protocols):
                if row['dst' if is_incoming else 'src'] == home_ip:
                    # if 40 < int(row['len']) < 1458:
                    lengths.append(int(row['len']))
                    if need_ids:
                        ids.append(make_stream_id(row))

    if tso:
        lengths, ids = mock_tso(lengths, ids)

    return sorted(lengths), ids


def mock_tso(data, ids=None, mtu=1500, mss=1460):
    ip_overhead = 20
    new_data = []
    new_ids = None if ids is None else []
    for i, element in enumerate(data):
        if element > mtu:
            while element > mtu:
                new_data.append(mss + ip_overhead)
                element -= mss
                if ids is not None:
                    new_ids.append(ids[i])
            if element > 0:
                new_data.append(mss + ip_overhead)
                if ids is not None:
                    new_ids.append(ids[i])
        else:
            new_data.append(element)
            if ids is not None:
                    new_ids.append(ids[i])
    return new_data, new_ids


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


def make_length_triples(lengths, ids, video_id, audio_id):
    length_dict = {}
    for i, length in enumerate(lengths):
        if ids[i] == video_id:
            id = 'video'
        elif ids[i] == audio_id:
            id = 'audio'
        else:
            id = 'rest'
        if length in length_dict:
            try:
                length_dict[length][id] += 1
            except KeyError:
                length_dict[length][id] = 1
        else:
            length_dict[length] = {id: 1}
    return length_dict


def get_two_common(ids):
    x = {}
    for id in ids:
        try:
            x[id] += 1
        except KeyError:
            x[id] = 1
    elems = sorted(x.items(), cmp=lambda x, y: x[1] - y[1], reverse=True)
    return elems[0][0], elems[1][0]


def create_subplot(matrix, colors, axis, width=0.5):
    bar_renderers = []
    ind = np.arange(matrix.shape[1])
    bottoms = np.cumsum(np.vstack((np.zeros(matrix.shape[1]), matrix)), axis=0)[:-1]
    for i, row in enumerate(matrix):
        r = axis.bar(ind, row, width=width, color=colors[i], bottom=bottoms[i])
        bar_renderers.append(r)
    return bar_renderers


def android_in_out(show=False):
    android_ip = '192.168.0.4'
    website = 'youtube.com'
    android_file = 'android_combined_dataset.csv'
    output_file = 'android_packet_length_in_out.svg'

    data_points_in, _ = get_packet_length_data(android_file, android_ip, website, is_incoming=True, need_ids=False)
    ax = plot_packet_length(data_points_in, color='red')

    data_points_out, _ = get_packet_length_data(android_file, android_ip, website, is_incoming=False, need_ids=False)
    plot_packet_length(data_points_out, color='blue', ax=ax)
    plt.savefig(output_file)
    if show:
        plt.show()


def chrome_in_out(show=False):
    chrome_ip = '10.0.2.15'
    website = 'youtube.com'
    chrome_file = 'dataset3/out.csv'
    output_file = 'chrome_packet_length_in_out.svg'

    data_points_in, _ = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=True, need_ids=False)
    ax = plot_packet_length(data_points_in, color='red')

    data_points_out, _ = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=False, need_ids=False)
    plot_packet_length(data_points_out, color='blue', ax=ax)
    plt.savefig(output_file)
    if show:
        plt.show()


def in_out_android_chrome(android_file, android_ip, chrome_file, chrome_ip, website, tso, is_incoming, show):
    use_log = is_incoming and not tso
    data_points_android, _ = get_packet_length_data(android_file, android_ip, website, is_incoming=is_incoming, tso=tso, need_ids=False)
    ax = plot_packet_length(data_points_android, color='blue', use_log=use_log, storage_units=use_log)

    data_points_chrome, _ = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=is_incoming, tso=tso, need_ids=False)
    plot_packet_length(data_points_chrome, color='red', ax=ax, use_log=use_log, storage_units=use_log)

    name = pretty_name(website)('{}')
    output_file = '{}_{}_packet_length_android_chrome{}.svg'.format(name, 'in' if is_incoming else 'out', '_tso' if tso else '')
    plt.savefig(output_file)
    if show:
        plt.show()
    plt.clf()


def in_out_android_chrome_el_manana(tso, is_incoming=True, show=False):
    chrome_file = 'el_manana/out.csv'
    android_file = 'el_manana/android_el_manana.csv'
    android_ip = '192.168.0.4'
    chrome_ip = '10.0.2.15'
    output_file = '{}_packet_length_android_chrome{}.svg'.format('in' if is_incoming else 'out', '_tso' if tso else '')
    website = 'youtube.com'
    use_log = is_incoming and not tso

    data_points_android, _ = get_packet_length_data(android_file, android_ip, website, is_incoming=is_incoming, tso=tso, need_ids=False)
    ax = plot_packet_length(data_points_android, color='blue', use_log=use_log, storage_units=use_log)

    data_points_chrome, _ = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=is_incoming, tso=tso, need_ids=False)
    plot_packet_length(data_points_chrome, color='red', ax=ax, use_log=use_log, storage_units=use_log)
    plt.savefig(output_file)
    if show:
        plt.show()


def youtube_count(is_incoming=True):
    android_ip = '192.168.0.4'
    android_file = 'android_combined_dataset.csv'
    chrome_ip = '10.0.2.15'
    chrome_file = 'dataset3/out.csv'
    website = 'youtube.com'
    data_points_android, _ = get_packet_length_data(android_file, android_ip, website, is_incoming=is_incoming, tso=True, need_ids=False)
    data_points_chrome, _ = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=is_incoming, tso=True, need_ids=False)
    print (len(filter(lambda x: x < 200, data_points_android)) / float(len(data_points_android))) * 100, '% Android below 200'
    print (len(filter(lambda x: x < 200, data_points_chrome)) / float(len(data_points_chrome))) * 100, '% Chrome below 200'
    print (len(filter(lambda x: 1400 < x < 1480, data_points_android)) / float(len(data_points_android))) * 100, '% Android below 1400 to 1480'
    print (len(filter(lambda x: 1400 < x < 1480, data_points_chrome)) / float(len(data_points_chrome))) * 100, '% Chrome below 1400 to 1480'


def count_size(is_incoming=True):
    android_ip = '192.168.0.4'
    android_file = 'android_combined_dataset.csv'
    chrome_ip = '10.0.2.15'
    chrome_file = 'dataset3/out.csv'
    website = 'youtube.com'
    android_in, _ = get_packet_length_data(android_file, android_ip, website, is_incoming=is_incoming, tso=True, need_ids=False)
    android_out, _ = get_packet_length_data(android_file, android_ip, website, is_incoming=False, tso=True, need_ids=False)
    chrome_in, _ = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=is_incoming, tso=True, need_ids=False)
    chrome_out, _ = get_packet_length_data(chrome_file, chrome_ip, website, is_incoming=False, tso=True, need_ids=False)
    print sum(android_in), 'in Android'
    print sum(chrome_in), 'in Chrome'
    print sum(android_out), 'out Android'
    print sum(chrome_out), 'out Chrome'


def get_small_big_source(is_chrome=True, show=False):
    chrome_ip = '10.0.2.15'
    android_ip = '192.168.0.4'
    website = 'youtube.com'
    # chrome_file = 'el_manana/out.csv'
    # android_file = 'el_manana/android_el_manana.csv'

    android_base = 'videos-10/android-10/video-{}/out.csv'
    chrome_base = 'videos-10/chrome-10/video-{}/out.csv'

    base = chrome_base if is_chrome else android_base
    home_ip = chrome_ip if is_chrome else android_ip

    length_dicts = []

    for i in range(0, 18 if is_chrome else 10):
        lengths, ids = get_packet_length_data(base.format((i % 10) + 1), home_ip, website, is_incoming=True, tso=True, need_ids=True)
        video_id, audio_id = get_two_common(ids)
        length_dicts.append(make_length_triples(lengths, ids, video_id, audio_id))

    length_dict = sum_length_dicts(length_dicts)
    length_list = sorted(length_dict.items(), cmp=lambda x, y: x[0] - y[0], reverse=False)
    # print length_list, sum(map(lambda x: sum(x[1].values()), length_list))
    length_bar_chart(length_list, show=show, output_file='small_big_source_{}.svg'.format('chrome' if is_chrome else 'android'))


def sum_length_dicts(length_dicts):
    if len(length_dicts) == 1:
        return length_dicts[0]

    merged_dicts = length_dicts[0]
    length_dicts = length_dicts[1:]

    for length_dict in length_dicts:
        for length, details in length_dict.items():
            for key, value in details.items():
                if length in merged_dicts:
                    if key in merged_dicts[length]:
                        merged_dicts[length][key] += value
                    else:
                        merged_dicts[length][key] = value
                else:
                    merged_dicts[length] = {key: value}
    return merged_dicts


# TODO
def do_quic_lengths():
    home_ip = '10.0.2.15'
    quic_file = 'quic-manana/out.csv'
    website = 'youtube.com'
    lengths, _ = get_packet_length_data(quic_file, home_ip, website, is_incoming=True, tso=False, protocols=['UDP'])

    length_dict = {}
    total = 0
    for length in lengths:
        try:
            length_dict[length] += 1
        except KeyError:
            length_dict[length] = 1
        total += 1
    print length_dict
    # asdf = sorted(length_dict.items(), cmp=lambda x, y: x[1] - y[1], reverse=True)
    # asdf = map(lambda x: (x[0], '{0:.2f}%'.format(x[1] * 100 / float(total))), asdf)
    # ax = plot_packet_length(lengths, color='blue', use_log=False, storage_units=False)
    # plt.savefig('gaidys.svg')
    # if True:
    #     plt.show()
    # plt.clf()


# Netflix
def netflix_in_out_android_chrome(tso, is_incoming=True, show=False):
    android_file = 'hannibal_dump/android.csv'
    android_ip = '192.168.1.6'
    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_ip = '192.168.1.2'
    website = 'netflix.com'

    in_out_android_chrome(android_file, android_ip, chrome_file, chrome_ip, website, tso, is_incoming, show)


# YouTube
def youtube_in_out_android_chrome(tso, is_incoming=True, show=False):
    android_ip = '192.168.0.4'
    android_file = 'android_combined_dataset.csv'
    chrome_ip = '10.0.2.15'
    chrome_file = 'dataset3/out.csv'
    # chrome_file = 'chrome_combined_dataset.csv'
    website = 'youtube.com'
    in_out_android_chrome(android_file, android_ip, chrome_file, chrome_ip, website, tso, is_incoming, show)


if __name__ == '__main__':
    # android_in_out()
    # chrome_in_out()
    # youtube_in_out_android_chrome(True, is_incoming=True, show=False)
    # youtube_in_out_android_chrome(True, is_incoming=False, show=False)
    # youtube_in_out_android_chrome(False, is_incoming=True, show=False)
    # youtube_in_out_android_chrome(False, is_incoming=False, show=False)
    # count_size()
    # in_out_android_chrome_el_manana(True, is_incoming=True)
    # in_out_android_chrome_el_manana(True, is_incoming=False)
    # get_small_big_source(is_chrome=True)
    # get_small_big_source(is_chrome=False)
    do_quic_lengths()
    # netflix_in_out_android_chrome(True, is_incoming=True, show=True)
    # netflix_in_out_android_chrome(False, is_incoming=True, show=True)
