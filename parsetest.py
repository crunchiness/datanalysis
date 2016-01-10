import re

fn = 'test.dat'
file_name = 'asdffff.txt'

with open(file_name, 'r') as f:
    obj = {}
    old = ''
    print_t = False
    for line in f:
        if 'ICMP' in line and 'IP6' not in line:
            print line[:-1]
        # # 13:45:46.567058 IP (tos 0x0, ttl 246, id 18484, offset 0, flags [DF], proto TCP (6), length 40)
        # #     31.186.225.27.80 > 192.168.0.17.47596: Flags [.], cksum 0xc6ce (correct), ack 2921, win 24820, length 0
        # regex_line1 = r'[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+ IP '
        # m1 = re.match(regex_line1, line)
        # regex_line2 = r'^ {4}'
        # m2 = re.match(regex_line2, line)
        #
        # # first line
        # if m1:
        #     print_t = True
        #     print line.replace("\n", '')
        #     old = m1.group(0)
        #     obj = {'time': m1.group(0)}
        # elif line[0] == '\t' or line[0] == ' ':
        #     if False:
        #         print line.replace('\n', '')
        # else:
        #     print_t = False
        # # elif m2:
        # #     regex = r'    ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+) > ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+).*'
        # #     match_ips = re.match(regex, line)
        # #     src_ip = match_ips.group(1)
        # #     src_port = match_ips.group(2)
        # #     dst_ip = match_ips.group(3)
        # #     dst_port = match_ips.group(4)
        # # else:
        # #     regex = r'^ *'
        # #     num_spaces = len(re.match(regex, line).group(0))
        # #     if num_spaces > 0:
        # #         old += ' s' + str(num_spaces)
        # #     regex = r'^\t*'
        # #     num_tabs = len(re.match(regex, line).group(0))
        # #     if num_tabs > 0:
        # #         old += ' t' + str(num_tabs)
