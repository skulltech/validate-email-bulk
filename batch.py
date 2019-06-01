import csv
import time
from multiprocessing import Pool

from validate import validate


def parallel(email):
    ret = validate(email)
    return [ret[k] for k in sorted(ret)]


def process(input_file):
    emails = []
    with open(input_file, newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            emails.append(row[0])

    with Pool(5) as p:
        processed = list(p.imap(parallel, emails))

    with open(f'{input_file[:-4]}_processed.csv', mode='w') as processed_file:
        writer = csv.writer(processed_file)
        writer.writerow(['color', 'deliverable', 'email', 'mx', 'normalized', 'syntax'])
        for line in processed:
            writer.writerow(line)


def main():
    input_file = input('[*] Input CSV file: ')
    start = time.time()
    process(input_file)
    end = time.time()
    print(f'[*] Done. Time elapsed: {end - start} seconds.')


if __name__ == '__main__':
    main()
