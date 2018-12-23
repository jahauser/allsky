import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('star_file_name')
    
    args = parser.parse_args()
    return args


def main(args):
    data = pd.read_table(args.star_file_name, sep='\s+', names=['n', 'mag', 'x', 'y', 'ra', 'dec', 'a', 'b', 'theta', 'fwhm', 'elong', 'ellip'])
    plt.scatter(range(len(data['fwhm'])), data['mag'])
    plt.show()


if __name__ == '__main__':
    args = get_args()
    main(args)
