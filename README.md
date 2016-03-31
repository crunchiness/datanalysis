The purpose of this set of scripts is to generate graphs from data produces with NETCRUNCHs. 

All of the script files are runnable except for "shared.py".

What graphs are generated can be controlled by commenting out appropriate lines under
"if __name__ == '__main__':" at the bottom of each script. All functions that are service
specific are named with prefix "netflix_" or "youtube_". All other functions are generic
and can be reused for any other service. 


accumulated_data.py         accumulated data charts
bitrate_graph.py            bitrate charts
chunks_packets.py           chunk sizes and interarrival times (clustered packets)
chunks_range.py             chunk sizes and interarrival times (chunks from range parameter)
combine_datasets.py         combines CSV datasets
flow_plot.py                parallel connections charts
packet_length_grapher.py    packet length charts
packets_over_time.py        packets over time charts
top_flows.py                top flows charts
uploaded_ad_data.py         YouTube upstream traffic statistics
shared.py                   shared functions
