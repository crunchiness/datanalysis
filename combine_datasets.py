import csv


def get_fieldnames(file_name):
    with open(file_name, 'rb') as csv_file:
        data_reader = csv.DictReader(csv_file, delimiter=',')
        return data_reader.fieldnames


def combine_files(out_name, inputs):

    if len(inputs) < 1:
        raise Exception('No inputs.')

    combined_csv = open(out_name, 'w')
    writer = csv.DictWriter(combined_csv, fieldnames=get_fieldnames(inputs[0]))
    writer.writeheader()

    for input_file in inputs:
        with open(input_file, 'rb') as csv_file:
            data_reader = csv.DictReader(csv_file, delimiter=',')
            for row in data_reader:
                writer.writerow(row)

combine_files('android_combined_dataset.csv', ['videos-10/android-10/video-{}/out.csv'.format(i) for i in range(1, 11)])
