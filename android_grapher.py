import argparse
import datetime
import numpy as np
import matplotlib.pyplot as plt
import csv


def plot_cdf(input_file, home_ip, app, filter_incoming=False, filter_outgoing=False, no_save=False, no_display=False, output_file=None, use_log=False, clear=True, plot_params=None):
    lengths = []
    max_length = 0
    matching_entries = 0

    with open(input_file, 'rb') as csv_file:
        data_reader = csv.reader(csv_file, delimiter=';')
        for row in data_reader:
            if app in row[0]:
                if filter_incoming and row[11] == home_ip or \
                   filter_outgoing and row[9] == home_ip:
                    matching_entries += 1
                    if int(row[8]) > max_length:
                        max_length = int(row[8])
                    lengths.append(int(row[8]))

    sorted_data = sorted(lengths)

    # Remove some outliers
    sorted_data = sorted_data[3:-3]

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
            output_file = date + '__' + app + '.svg'
        plt.savefig(output_file)

    if not no_display:
        plt.show()

    if clear:
        plt.clf()

# 0       1          2         3     4     5    6        7       8        9     10      11    12
# appName;ipPROTOCOL;timeStamp;ipTOS;ipTTL;ipID;ipOFFSET;ipFLAGS;ipLENGTH;srcIP;srcPort;dstIP;dstPort

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='AndroidGrapher', description='Produce a graph from Android data.')
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
    parser.add_argument('app', help='App of interest')
    args = parser.parse_args()
    print 'Params', args
    plot_cdf(args.input, args.ip, args.app, args.incoming, args.outgoing, args.no_save, args.no_display)
