import csv
from urlparse import urlparse, parse_qs
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from shared import storage_formatter_factory


def get_chunk_size_data(input_file):
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
                    itags[itag].append(chunk_size)
                except KeyError:
                    itags[itag] = [chunk_size]
    return itags


def plot_chunk_sizes(show=False):
    input_file = 'chrome_combined_dataset.csv'
    itags = get_chunk_size_data(input_file)

    fig, ax = plt.subplots()
    ax.set_yticklabels(['{:3}%'.format(x * 100) for x in ax.get_yticks()])
    ax.set_ylabel('% Total')
    ax.set_xlabel('Chunk size')
    ax.get_xaxis().set_major_formatter(FuncFormatter(storage_formatter_factory()))
    ax.set_xticks(map(lambda x: x*1024, [0, 256, 512, 768, 1024, 1024 + 256, 1024 + 512, 1024 + 768, 2048]))

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
    if show:
        plt.show()
    plt.savefig('chunk_sizes.svg')
    plt.clf()

if __name__ == '__main__':
    plot_chunk_sizes(show=False)
