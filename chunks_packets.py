import csv

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from accumulated_data import get_time_limits
from chunks_range import get_chunk_size_data
from shared import make_stream_id, make_storage_ticks, storage_formatter_factory


def generate_chunk_data(input_file, home_ip, website, protocols=None, threshold=0.11):
    ignore_init = 25
    if protocols is None:
        protocols = ['TCP']
    chunks = {}
    first_timestamp, duration = get_time_limits(input_file, website, home_ip, protocols)
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if website in row['website'] and (row['protocol'] in protocols):
                if row['dst'] == home_ip:
                    timestamp = float(row['timestamp']) - first_timestamp
                    if timestamp < ignore_init:
                        continue
                    stream_id = make_stream_id(row)
                    if stream_id not in chunks:
                        chunks[stream_id] = {'chunks': [], 'current_chunk': 0, 'current_time': timestamp}
                    if timestamp < chunks[stream_id]['current_time'] + threshold:
                        chunks[stream_id]['current_time'] = timestamp
                        chunks[stream_id]['current_chunk'] += int(row['len'])
                    else:
                        chunk = chunks[stream_id]['current_chunk']
                        chunks[stream_id]['chunks'].append((chunk, timestamp))
                        chunks[stream_id]['current_chunk'] = 0
                        chunks[stream_id]['current_time'] = timestamp
    return chunks


def get_chunk_data_10(is_chrome, threshold=0.11):
    website = 'youtube.com'
    chrome_ip = '10.0.2.15'
    android_ip = '192.168.0.4'
    android_base = 'videos-10/android-10/video-{}/out.csv'
    chrome_base = 'videos-10/chrome-10/video-{}/out.csv'
    base = chrome_base if is_chrome else android_base
    home_ip = chrome_ip if is_chrome else android_ip

    all_chunks = []

    for i in range(0, 8 if is_chrome else 10):
        stream_id, chunks = sorted(generate_chunk_data(base.format(i + 1), home_ip, website, threshold=threshold).items(), cmp=lambda x, y: sum(map(lambda a: a[0], x[1]['chunks'])) - sum(map(lambda a: a[0], y[1]['chunks'])), reverse=True)[0]

        # make sure videos are consecutively on the timeline
        if len(all_chunks) > 0:
            _, last_time = all_chunks[-1]
            last_time += 1
        else:
            last_time = 0

        all_chunks.extend(map(lambda x: (x[0], x[1] + last_time), chunks['chunks']))
    return all_chunks


def save_scatter(x_values, y_values, threshold, is_chrome, show=False):
    fig, ax = plt.subplots()
    ax.set_ylabel('chunk size')
    ax.set_xlabel('time, s')
    fn, tix = make_storage_ticks(y_values)
    ax.yaxis.set_major_formatter(fn)
    plt.yticks(tix)
    plt.plot(x_values, y_values, 'bo')
    plt.savefig('scatter-fig-{}0ms-{}.svg'.format(int(threshold * 100), 'chrome' if is_chrome else 'android'))
    if show:
        plt.show()
    plt.clf()


def save_cdf(x_values, y_values, threshold, is_chrome, show=False):
    fig, ax = plt.subplots()

    ax.set_ylabel('% Total')
    ax.set_xlabel('Chunk size')
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
    ax.set_xticks(map(lambda x: x * 1024, [0, 512, 1024, 1024 + 512, 2048, 2048 + 512, 3072]))

    plt.plot(x_values, y_values, color='blue')

    plt.ylim(0., 1.)
    plt.xlim(0, 3072 * 1024)
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    plt.savefig('cdf-fig-{}0ms-{}.svg'.format(int(threshold * 100), 'chrome' if is_chrome else 'android'))
    if show:
        plt.show()
    plt.clf()


def chunks_both_real_fake(show=False):
    input_file = 'chrome_combined_dataset.csv'
    fake_chunks = get_chunk_data_10(True)
    fake_chunk_sizes = map(lambda x: x[0], fake_chunks)

    fake_x_values = sorted(list(set(fake_chunk_sizes)))
    fake_y_values = [len(filter(lambda x: x <= chunk_size, fake_chunk_sizes)) for chunk_size in fake_x_values]
    fake_y_values = map(lambda x: x / float(len(fake_chunk_sizes)), fake_y_values)

    real_chunks = get_chunk_size_data(input_file)
    real_chunks = reduce(lambda x, y: x + y, map(lambda x: x[1], real_chunks.items()), [])

    real_x_values = sorted(list(set(real_chunks)))
    real_y_values = [len(filter(lambda x: x <= chunk_size, real_chunks)) for chunk_size in real_x_values]
    real_y_values = map(lambda x: x / float(len(real_chunks)), real_y_values)

    fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Chunk size')
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
    ax.set_xticks(map(lambda x: x * 1024, [0, 512, 1024, 1024 + 512, 2048, 2048 + 512]))

    fake_line = plt.plot(fake_x_values, fake_y_values, color='blue')
    real_line = plt.plot(real_x_values, real_y_values, color='red')

    plt.legend([fake_line[0], real_line[0]], ['Clustering', 'From URLs'], loc=4)

    plt.savefig('chunk_sizes_both.svg')
    if show:
        plt.show()
    plt.clf()


def chunks_both_android_chrome(show=False):
    threshold = 0.11
    android_chunks = get_chunk_data_10(is_chrome=False, threshold=threshold)
    android_chunk_sizes = map(lambda x: x[0], android_chunks)
    android_x_values = sorted(list(set(android_chunk_sizes)))
    android_y_values = [len(filter(lambda x: x <= chunk_size, android_chunk_sizes)) for chunk_size in android_x_values]
    android_y_values = map(lambda x: x / float(len(android_chunk_sizes)), android_y_values)

    chrome_chunks = get_chunk_data_10(is_chrome=True, threshold=threshold)
    chrome_chunk_sizes = map(lambda x: x[0], chrome_chunks)
    chrome_x_values = sorted(list(set(chrome_chunk_sizes)))
    chrome_y_values = [len(filter(lambda x: x <= chunk_size, chrome_chunk_sizes)) for chunk_size in chrome_x_values]
    chrome_y_values = map(lambda x: x / float(len(chrome_chunk_sizes)), chrome_y_values)

    fig, ax = plt.subplots()

    ax.set_ylabel('% Total')
    ax.set_xlabel('Chunk size')
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
    ax.set_xticks(map(lambda x: x * 1024, [0, 512, 1024, 1024 + 512, 2048, 2048 + 512, 3072]))

    android_line = plt.plot(android_x_values, android_y_values, color='blue')
    chrome_line = plt.plot(chrome_x_values, chrome_y_values, color='red')

    plt.ylim(0., 1.)
    plt.xlim(0, 3072 * 1024)
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])

    plt.legend([android_line[0], chrome_line[0]], ['YouTube Android', 'YouTube Chrome'], loc=4)

    plt.savefig('chunk_sizes_android_chrome.svg')
    if show:
        plt.show()
    plt.clf()


def find_threshold(is_chrome):
    for i in range(1, 100):
        threshold = i / 100.
        chunks = get_chunk_data_10(is_chrome, threshold=threshold)
        chunk_sizes = map(lambda x: x[0], chunks)
        chunk_times = map(lambda x: x[1], chunks)

        x_values = sorted(list(set(chunk_sizes)))
        y_values = [len(filter(lambda x: x <= chunk_size, chunk_sizes)) for chunk_size in x_values]
        y_values = map(lambda x: x / float(len(chunk_sizes)), y_values)

        save_scatter(chunk_times, chunk_sizes, threshold, is_chrome, show=False)
        save_cdf(x_values, y_values, threshold, is_chrome, show=False)

if __name__ == '__main__':
    # find_threshold(is_chrome=True)
    # find_threshold(is_chrome=False)
    # chunks_both_real_fake(show=True)
    chunks_both_android_chrome(show=True)
