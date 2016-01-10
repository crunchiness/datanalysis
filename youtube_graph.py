import numpy as np
import matplotlib.pyplot as plt
import csv


def plot_cdf(file_name, website):
    lengths = []
    max_length = 0
    with open(file_name, 'rb') as csv_file:
        data_reader = csv.reader(csv_file, delimiter=';')

        i = 0
        for row in data_reader:
            if 'android.youtube' in row[0] and row[11] == '192.168.0.17':
                lengths.append(int(row[8]))
                print row[9]
            # i += 1
            # if i ==20:
            #     break
            # if row['website'] == website:
            #     if int(row['len']) > max_length:
            #         max_length = int(row['len'])
            #     lengths.append(int(row['len']))
    # return
    sorted_data = sorted(lengths)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data))
    plt.plot(sorted_data, yvals)
    plt.show()


# timestamp,v,hl,tos,len,id,flags,off,ttl,p,sum,src,dst,opt,pad,website,source
# 1448284130.978307,4,5,0,69,58949,0,0,46,17,64767,64.233.167.189,192.168.0.20,,,youtube.com,TIME

if __name__ == '__main__':
    plot_cdf('phone_log.txt', 'android.youtube')
