import csv

from shared import make_stream_id, storage_formatter_factory


def is_ad(url):
    ad_strings = ['instream_ad', 'pagead', 'doubleclick.net', 'ad_data_204', 'stats/ads', 'fwmrm.net/ad', 'api/ads']
    return reduce(lambda x, y: x or y, map(lambda x: x in url, ad_strings), False)


def get_ad_streams(input_file, home_ip, website='youtube.com', is_incoming=False):
    ad_dict = {}
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if row['is_ack'] == 'True':
                continue
            if row['protocol'] != 'TCP':
                continue
            if website in row['website']:
                if row['dst' if is_incoming else 'src'] == home_ip:
                    if row['url'] != '':
                        stream_id = make_stream_id(row)
                        try:
                            ad_dict[stream_id].append(row['url'])
                        except KeyError:
                            ad_dict[stream_id] = [row['url']]
    return ad_dict


def get_stream_sizes(input_file, home_ip, stream_ids, is_incoming=False):
    sizes = [0] * len(stream_ids)
    all_sizes = 0
    with open(input_file, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        for row in data_reader:
            if row['is_ack'] == 'True':
                continue
            if row['protocol'] != 'TCP':
                continue
            if row['dst' if is_incoming else 'src'] == home_ip:
                all_sizes += int(row['len'])
                this_stream_id = make_stream_id(row)
                for i, stream_id in enumerate(stream_ids):
                    if stream_id == this_stream_id:
                        sizes[i] += int(row['len'])
                        break
    return sizes, all_sizes


def get_ad_sizes(print_urls=False):
    input_file = 'chrome_combined_dataset.csv'
    home_ip = '10.0.2.15'
    ad_dict = get_ad_streams(input_file, home_ip, is_incoming=False)

    qu = []
    for stream_id, url_list in ad_dict.items():
        if reduce(lambda x, y: x and y, map(is_ad, url_list), True):
            qu.append(stream_id)
            if print_urls:
                print stream_id, len(url_list)
                for url in url_list:
                    print '\t', url

    sizes, total = get_stream_sizes(input_file, home_ip, qu)

    print 'Total ad data sent:', storage_formatter_factory(unit_speed=False)(sum(sizes))
    print 'Total data sent:', storage_formatter_factory(unit_speed=False)(total)
    print 'Percentage ad data {0:0.1f}%'.format(sum(sizes) * 100 / float(total))


if __name__ == '__main__':
    get_ad_sizes(print_urls=True)
