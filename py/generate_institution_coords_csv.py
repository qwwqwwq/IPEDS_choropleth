import argparse
from ipeds import read_with_column_subset


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('output_file')
    return parser.parse_args()


def extract_data(of):
    institutional_basic_info = read_with_column_subset("hd2013", ['INSTNM', 'LONGITUD', 'LATITUDE', 'UGOFFER', 'HLOFFER', 'INSTSIZE'])
    institutional_basic_info = institutional_basic_info[(institutional_basic_info['Highest level of offering'] >= 5) & (institutional_basic_info['Undergraduate offering'] == 1)]
    del institutional_basic_info['Highest level of offering']
    del institutional_basic_info['Undergraduate offering']

    institutional_basic_info.dropna().to_csv(of, header=False)


def main():
    args = get_args()
    extract_data(args.output_file)

if __name__ == '__main__':
    main()
