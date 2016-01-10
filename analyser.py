import argparse
import numpy as np
import matplotlib.pyplot as plt
import csv


def plot_cdf(file_name, websites):
    lengths = []
    max_length = 0
    COUNT = 0
    with open(file_name, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if row['website'] in websites and row['dst'] == '192.168.0.20':
                COUNT += 1
                if int(row['len']) > max_length:
                    max_length = int(row['len'])
                lengths.append(int(row['len']))
    sorted_data = sorted(lengths)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data))
    print COUNT
    plt.plot(sorted_data, yvals)
    plt.show()


# timestamp,v,hl,tos,len,id,flags,off,ttl,p,sum,src,dst,opt,pad,website,source
# 1448284130.978307,4,5,0,69,58949,0,0,46,17,64767,64.233.167.189,192.168.0.20,,,youtube.com,TIME

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ChromeGrapher', description='Produce a graph from Chrome data.')
    parser.add_argument('input', help='Input file name of CSV')
    parser.add_argument('website', nargs='+', help='Website of interest')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    args = parser.parse_args()
    plot_cdf(args.input, args.website)
