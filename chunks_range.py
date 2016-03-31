import csv
from urlparse import urlparse, parse_qs
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from shared import storage_formatter_factory, make_storage_ticks


# YouTube
def youtube_get_chunk_size_data(input_file):
    itags = {}
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if 'videoplayback' in row['url'] and 'range' in row['url']:
                a_range = parse_qs(urlparse(row['url']).query)['range'][0]
                from_byte, to_byte = a_range.split('-')
                from_byte = int(from_byte)
                to_byte = int(to_byte)
                chunk_size = to_byte - from_byte
                itag = parse_qs(urlparse(row['url']).query)['itag'][0]

                try:
                    itags[itag].append((chunk_size, float(row['timestamp'])))
                except KeyError:
                    itags[itag] = [(chunk_size, float(row['timestamp']))]
    return itags


def youtube_plot_chunk_sizes(show=False):
    input_file = 'chrome_combined_dataset.csv'
    itags = youtube_get_chunk_size_data(input_file)

    fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Chunk size')
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
    ax.set_xticks(map(lambda x: x * 1024, [0, 256, 512, 768, 1024, 1024 + 256, 1024 + 512, 1024 + 768, 2048]))

    tag_dict = {
        '243': 'video @ 524k',
        '244': 'video @ 798k',
        '251': 'audio @ 160k'
    }
    colors = ['orange', 'red', 'brown', 'green', 'blue']
    types = []
    averages = []
    lines = []
    for i, (itag, chunks) in enumerate(itags.items()):
        chunks = map(lambda x: x[0], chunks)
        if itag == '278' or itag == '250':
            continue
        x_values = sorted(list(set(chunks)))
        y_values = [len(filter(lambda x: x <= chunk_size, chunks)) for chunk_size in x_values]
        y_values = map(lambda x: x / float(len(chunks)), y_values)
        types.append(itag)
        average = sum(chunks) / float(len(chunks))
        print itag, tag_dict[itag], average
        averages.append(average)
        lines.append(plt.plot(x_values, y_values, color=colors[i]))

    plt.legend(map(lambda x: x[0], lines), map(lambda x: tag_dict[x], types), loc=4)
    plt.tight_layout()
    plt.savefig('youtube_chunk_sizes_range.svg')
    if show:
        plt.show()
    plt.clf()


# Netflix
def netflix_extract_range(url):
    fragment = 'nflxvideo.net/range/'
    if fragment in url:
        start_pos = url.find(fragment) + len(fragment)
        video_range = ''
        for ch in url[start_pos:]:
            if ch == '?':
                break
            else:
                video_range += ch
        return tuple(map(int, video_range.split('-')))
    else:
        return None


def netflix_chrome_get_chunk_size_data(input_file):
    chunks = []
    first_timestamp = None
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            try:
                from_byte, to_byte = netflix_extract_range(row['url'])
                if first_timestamp is None:
                    first_timestamp = float(row['timestamp'])
                timestamp = float(row['timestamp']) - first_timestamp
                chunks.append((to_byte - from_byte, timestamp))
            except TypeError:
                continue
    return chunks


def netflix_plot_interarrival_time(is_log=False, show=False):
    android_file = 'netflix_chunks.csv'
    android_timestamps = map(lambda x: x[1], netflix_android_get_chunk_size_data(android_file))
    android_inter_arrival_times = map(lambda x: x[0]-x[1], zip(android_timestamps[1:], android_timestamps[:-1]))
    android_inter_arrival_times = filter(lambda x: 0 <= x < 30, android_inter_arrival_times)
    android_x_values = sorted(android_inter_arrival_times)
    android_y_values = [len(filter(lambda x: x <= time, android_inter_arrival_times)) for time in android_x_values]
    android_y_values = map(lambda x: x / float(len(android_inter_arrival_times)), android_y_values)

    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_timestamps = map(lambda x: x[1], netflix_chrome_get_chunk_size_data(chrome_file))
    chrome_inter_arrival_times = map(lambda x: x[0] - x[1], zip(chrome_timestamps[1:], chrome_timestamps[:-1]))
    chrome_inter_arrival_times = filter(lambda x: 0 <= x < 30, chrome_inter_arrival_times)
    chrome_x_values = sorted(chrome_inter_arrival_times)
    chrome_y_values = [len(filter(lambda x: x <= time, chrome_inter_arrival_times)) for time in chrome_x_values]
    chrome_y_values = map(lambda x: x / float(len(chrome_inter_arrival_times)), chrome_y_values)

    fig, ax = plt.subplots()
    ax.set_ylabel('CDF')
    ax.set_xlabel('Interarrival time (s)')
    if is_log:
        ax.set_xscale('log')

    android_line = plt.plot(android_x_values, android_y_values, color='blue')
    chrome_line = plt.plot(chrome_x_values, chrome_y_values, color='red')

    loc = 2 if is_log else 4
    plt.legend([android_line[0], chrome_line[0]], ['Netflix Android', 'Netflix Chrome'], loc=loc)

    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])

    plt.savefig('netflix_inter_arrival_times{}.svg'.format('_log' if is_log else ''))
    if show:
        plt.show()
    plt.clf()


def netflix_plot_chunk_sizes(show=False):
    android_file = 'netflix_chunks.csv'
    android_chunks = map(lambda x: x[0], netflix_android_get_chunk_size_data(android_file))
    android_x_values = sorted(list(set(android_chunks)))
    android_y_values = [len(filter(lambda x: x <= chunk_size, android_chunks)) for chunk_size in android_x_values]
    android_y_values = map(lambda x: x / float(len(android_chunks)), android_y_values)

    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_chunks = map(lambda x: x[0], netflix_chrome_get_chunk_size_data(chrome_file))
    chrome_x_values = sorted(list(set(chrome_chunks)))
    chrome_y_values = [len(filter(lambda x: x <= chunk_size, chrome_chunks)) for chunk_size in chrome_x_values]
    chrome_y_values = map(lambda x: x / float(len(chrome_chunks)), chrome_y_values)

    fig, ax = plt.subplots()
    ax.set_ylabel('% Total')
    ax.set_xlabel('Chunk size')
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
    ax.set_xticks(map(lambda x: x * 1024, [0, 256, 512, 768, 1024, 1024 + 256, 1024 + 512, 1024 + 768, 2048]))

    android_line = plt.plot(android_x_values, android_y_values, color='blue')
    chrome_line = plt.plot(chrome_x_values, chrome_y_values, color='red')

    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])

    plt.legend([android_line[0], chrome_line[0]], ['Netflix Android', 'Netflix Chrome'], loc=4)
    plt.savefig('netflix_chunk_sizes_range.svg')
    if show:
        plt.show()
    plt.clf()


def netflix_android_get_chunk_size_data(input_file):
    chunks = []
    first_timestamp = None
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file)
        for row in data_reader:
            chunk = int(row['chunk'])
            if first_timestamp is None:
                first_timestamp = float(row['timestamp'])
            timestamp = float(row['timestamp']) - first_timestamp
            chunks.append((chunk, timestamp))
    return chunks


def netflix_chunks_over_time(show=False):
    android_file = 'netflix_chunks.csv'
    android_chunks = netflix_android_get_chunk_size_data(android_file)
    android_chunks = filter(lambda x: 100 < x[1] < 400, android_chunks)
    android_x_values = map(lambda x: x[1], android_chunks)
    android_y_values = map(lambda x: x[0], android_chunks)

    chrome_file = 'hannibal_dump/chrome.csv'
    chrome_chunks = netflix_chrome_get_chunk_size_data(chrome_file)
    chrome_chunks = filter(lambda x: 100 < x[1] < 400, chrome_chunks)
    chrome_x_values = map(lambda x: x[1], chrome_chunks)
    chrome_y_values = map(lambda x: x[0], chrome_chunks)

    fig, ax = plt.subplots()
    ax.set_ylabel('chunk size')
    ax.set_xlabel('time, s')
    fn, tix = make_storage_ticks(android_y_values + chrome_y_values)
    ax.yaxis.set_major_formatter(fn)
    plt.yticks(tix)

    chrome_line = plt.plot(chrome_x_values, chrome_y_values, 'r-')
    plt.plot(chrome_x_values, chrome_y_values, 'ro')
    android_line = plt.plot(android_x_values, android_y_values, 'b-')

    plt.legend([android_line[0], chrome_line[0]], ['Netflix Android', 'Netflix Chrome'])

    plt.savefig('netflix_chunks_over_time.svg')
    if show:
        plt.show()
    plt.clf()


if __name__ == '__main__':
    # youtube_plot_chunk_sizes(show=False)
    # netflix_plot_chunk_sizes(show=False)
    # netflix_chunks_over_time(show=False)
    netflix_plot_interarrival_time(is_log=False, show=False)
    netflix_plot_interarrival_time(is_log=True, show=False)

