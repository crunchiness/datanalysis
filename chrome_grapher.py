import argparse
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime


def plot_cdf(input_file, home_ip, websites, filter_incoming=False, filter_outgoing=False, no_save=False, no_display=False, output_file=None, use_log=False, clear=True, plot_params=None):
    lengths_dict = {}
    lengths = []
    max_length = 0
    matching_entries = 0

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if row['website'] in websites:
                if filter_incoming and row['dst'] == home_ip or \
                   filter_outgoing and row['src'] == home_ip:
                    matching_entries += 1
                    if int(row['len']) > max_length:
                        max_length = int(row['len'])
                    lengths.append(int(row['len']))
                    try:
                        lengths_dict[int(row['len'])] += 1
                    except KeyError:
                        lengths_dict[int(row['len'])] = 1

    sorted_data = sorted(lengths)

    # Remove some outliers
    sorted_data = sorted_data[3:-3]
    remove_outliers(lengths_dict)


    if use_log:
        plt.xscale('log')

    yvals = np.arange(len(sorted_data)) / float(len(sorted_data))
    print matching_entries, 'matching entries'
    print 'max_length:', max_length

    if plot_params is None:
        plot_params = 'r-' if use_log else 'b-'
    plt.plot(sorted_data, yvals, plot_params)

    if not no_save:
        if output_file is None:
            date = datetime.datetime.now().isoformat().replace(':', '_')
            websites_str = ';'.join(websites)
            output_file = date + '__' + websites_str + '.svg'
        plt.savefig(output_file)

    if not no_display:
        plt.show()

    if clear:
        plt.clf()
    return lengths_dict


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


def length_bar_chart(lengths_dict, no_save=False, no_display=False, output_file=None):

    output_list = []

    # count packets
    total_packets = 0
    for key in lengths_dict.keys():
        total_packets += lengths_dict[key]

    threshold = total_packets / 100  # 1 percent

    # group counts
    current_key = []
    current_value = 0
    for key in sorted(lengths_dict.keys()):
        if lengths_dict[key] > threshold and current_value > 0:
            label = '-'.join(map(str, current_key))
            output_list.append((label, current_value))
            current_key = []
            current_value = 0
        if len(current_key) == 2:
            current_key.pop()
        current_key.append(key)
        current_value += lengths_dict[key]
        if current_value > threshold:
            label = '-'.join(map(str, current_key))
            output_list.append((label, current_value))
            current_key = []
            current_value = 0
    if current_value > 0:
        label = '-'.join(map(str, current_key))
        output_list.append((label, current_value))

    # draw the chart
    packets_counts = map(lambda x: x[1], output_list)
    labels = map(lambda x: x[0], output_list)
    ind = np.arange(len(output_list))  # the x locations for the groups

    width = 0.4  # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(ind, packets_counts, width, color='b')
    # add some text for labels, title and axes ticks
    ax.set_ylabel('Number of packets')
    ax.set_xlabel('Packet size in bytes')
    ax.set_title('Scores by group and gender')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(labels)

    plt.setp(plt.xticks()[1], rotation=-30)
    plt.tight_layout()

    if not no_save:
        if output_file is None:
            output_file = datetime.datetime.now().isoformat().replace(':', '_') + '__bar_chart.svg'
        plt.savefig(output_file)

    if not no_display:
        plt.show()


# timestamp,v,hl,tos,len,id,flags,off,ttl,p,sum,src,dst,opt,pad,website,source
# 1448284130.978307,4,5,0,69,58949,0,0,46,17,64767,64.233.167.189,192.168.0.20,,,youtube.com,TIME

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ChromeGrapher', description='Produce a graph from Chrome data.')
    parser.add_argument('input', help='Input file name of CSV')
    parser.add_argument('ip', help='Home IP address')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--incoming', action='store_true', help='Filter incoming packets')
    group.add_argument('--outgoing', action='store_true', help='Filter outgoing packets')
    parser.add_argument('--no_save', action='store_true', help='Don\'t save graph to file')
    parser.add_argument('--no_display', action='store_true', help='Don\'t display graph')
    parser.add_argument('--log', action='store_true', help='Use logarithmic scale')
    parser.add_argument('--plot_params', help='Set color and line type of plot (pyplot syntax)')
    parser.add_argument('website', nargs='+', help='Website of interest')
    args = parser.parse_args()
    print 'Params', args
    plot_cdf(args.input, args.ip, args.website, args.incoming, args.outgoing, args.no_save, args.no_display)
