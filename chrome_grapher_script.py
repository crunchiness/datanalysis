from chrome_grapher import plot_cdf, length_bar_chart
input_file = 'dataset1/out.csv'
home_ip = '192.168.0.20'
website = ['youtube.com']
no_display = True

print 'youtube.com incoming traffic'
plot_cdf(input_file, home_ip, website, filter_incoming=True, no_display=no_display, output_file='chrome_youtube.com_incoming_dataset1.svg')
print 'youtube.com incoming traffic logarithmic'
_, lengths_dict = plot_cdf(input_file, home_ip, website, filter_incoming=True, no_display=no_display, output_file='chrome_youtube.com_incoming_log_dataset1.svg', use_log=True)
length_bar_chart(lengths_dict, no_display=no_display, output_file='chrome_youtube.com_incoming_chart_dataset1.svg')


print 'youtube.com outgoing traffic'
plot_cdf(input_file, home_ip, website, filter_outgoing=True, no_display=no_display, output_file='chrome_youtube.com_outgoing_dataset1.svg')
print 'youtube.com outgoing traffic logarithmic'
_, lengths_dict = plot_cdf(input_file, home_ip, website, filter_outgoing=True, no_display=no_display, output_file='chrome_youtube.com_outgoing_log_dataset1.svg', use_log=True)
length_bar_chart(lengths_dict, no_display=no_display, output_file='chrome_youtube.com_outgoing_chart_dataset1.svg')


print 'youtube.com incoming/outgoing log combined'
ax, _ = plot_cdf(input_file, home_ip, website, filter_incoming=True, no_display=no_display, no_save=True, use_log=True, plot_params='g-', clear=False)
plot_cdf(input_file, home_ip, website, filter_outgoing=True, no_display=no_display, output_file='chrome_youtube.com_combined_log_dataset1.svg', use_log=True, plot_params='r-', ax=ax)
