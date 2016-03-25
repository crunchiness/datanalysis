import csv

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from accumulated_data import get_time_limits
from shared import make_stream_id, make_storage_ticks, storage_formatter_factory


def generate_chunk_data(input_file, home_ip, website, protocols=None, threshold=0.3):
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


def get_chunk_data_10(is_chrome, threshold):
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


def save_scatter(x_values, y_values, threshold):
    fig, ax = plt.subplots()
    ax.set_ylabel('y label')
    ax.set_xlabel('x label')
    fn, tix = make_storage_ticks(chunk_sizes)
    ax.yaxis.set_major_formatter(fn)
    plt.yticks(tix)
    plt.plot(x_values, y_values, 'bo')
    plt.savefig('scatter-fig-{}0ms.svg'.format(int(threshold * 100)))
    plt.clf()

"""
fig, ax = plt.subplots()
ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
ax.set_ylabel('% Total')
ax.set_xlabel('Chunk size')
ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
ax.set_xticks(map(lambda x: x*1024, [0, 256, 512, 768, 1024, 1024 + 256, 1024 + 512, 1024 + 768, 2048]))
x_values = sorted(list(set(chunks)))
y_values = [len(filter(lambda x: x <= chunk_size, chunks)) for chunk_size in x_values]
y_values = map(lambda x: x / float(len(chunks)), y_values)
plt.plot(x_values, y_values, color=colors[i]))
"""


def save_cdf(x_values, y_values, threshold, show=False):
    fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Chunk size')
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
    ax.set_xticks(map(lambda x: x * 1024, [0, 512, 1024, 1024 + 512, 2048, 2048+512]))

    plt.plot(x_values, y_values, color='blue')

    plt.savefig('cdf-fig-{}0ms.svg'.format(int(threshold * 100)))
    if show:
        plt.show()
    plt.clf()


if __name__ == '__main__':

    for i in range(11, 12):
        threshold = i / 100.
        chunks = get_chunk_data_10(True, threshold=threshold)
        chunk_sizes = map(lambda x: x[0], chunks)
        chunk_times = map(lambda x: x[1], chunks)

        x_values = sorted(list(set(chunk_sizes)))
        y_values = [len(filter(lambda x: x <= chunk_size, chunk_sizes)) for chunk_size in x_values]
        y_values = map(lambda x: x / float(len(chunk_sizes)), y_values)
        print y_values

#        save_scatter(chunk_times, chunk_sizes, threshold)
        save_cdf(x_values, y_values, threshold, show=True)
