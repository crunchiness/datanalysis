from android_grapher import plot_cdf
input_file = 'dataset1/phone_log.txt'
home_ip = '192.168.0.17'
app = 'android.youtube'
no_display = True

print 'youtube.com incoming traffic'
plot_cdf(input_file, home_ip, app, filter_incoming=True, no_display=no_display, output_file='android_youtube_incoming_dataset1.svg')
print 'youtube.com incoming traffic logarithmic'
plot_cdf(input_file, home_ip, app, filter_incoming=True, no_display=no_display, output_file='android_youtube_incoming_log_dataset1.svg', use_log=True)


print 'youtube.com outgoing traffic'
plot_cdf(input_file, home_ip, app, filter_outgoing=True, no_display=no_display, output_file='android_youtube_outgoing_dataset1.svg')
print 'youtube.com outgoing traffic logarithmic'
plot_cdf(input_file, home_ip, app, filter_outgoing=True, no_display=no_display, output_file='android_youtube_outgoing_log_dataset1.svg', use_log=True)

print 'youtube.com incoming/outgoing log combined'
plot_cdf(input_file, home_ip, app, filter_incoming=True, no_display=no_display, no_save=True, use_log=True, plot_params='g-', clear=False)
plot_cdf(input_file, home_ip, app, filter_outgoing=True, no_display=no_display, output_file='android_youtube_combined_log_dataset1.svg', use_log=True, plot_params='r-')
