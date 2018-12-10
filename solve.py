# sanitize to lowercase extension first
# collect folder of images to solve

import argparse, subprocess, os, time, re
from astropy.io import fits
from astropy.time import Time

client_path = '/Users/jake/Desktop/sextraction/astrometry.net/net/client/client.py'

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help='folder of images to solve')
    parser.add_argument('-threads', help='number of threads')
    parser.add_argument('-sterile', action='store_true')
    args = parser.parse_args()
    
    if args.folder[-1] != '/':
        args.folder += '/'

    if not args.threads:
        args.threads = 5
    
    return args

def sid_round(sid_time):
    print(sid_time)
    sid_time = re.split(r'[^0-9.]+', sid_time)
    decimal_mins = round(int(sid_time[0]) * 60 + int(sid_time[1]) + float(sid_time[2]) / 60.0)
    mins = int(decimal_mins % 60)
    hours = int(((decimal_mins - mins)/60) % 24)

    return '{0:02d}h{1:02d}m'.format(hours, mins)

def main(args):
    key = 'vsrjqdfgoomarrpf'
    dec = '34.38183'
    #solve_arg = 'python {client} --apikey {key} --parity 0 --downsample 1 --ra {{ra}} --dec {dec} --upload {{file}} --wcs {{new_file}}'.format(client=client_path, key=key, dec=dec)
    solve_arg = 'python {client} --apikey {key} --downsample 1  --upload {{file}} --wcs {{new_file}}'.format(client=client_path, key=key, dec=dec)
    if not os.path.isdir(args.folder + 'wcs/'):
        os.mkdir(args.folder + 'wcs/')
    processes = []
    files = os.listdir(args.folder)
    while files:
        filename = files.pop()
        print(filename)
        if filename.endswith(".fit") or filename.endswith(".fits"):
            path = args.folder + filename
            wcs_folder = args.folder + 'wcs/'
            image = fits.open(path)
            date = image[0].header['DATE-OBS']
            time = Time(date, scale='utc', location=(-117.68158,34.38183,0))
            #sidereal = time.sidereal_time('apparent').degree
            rounded_sidereal = sid_round(str(time.sidereal_time('apparent')))

            #full_arg = solve_arg.format(ra=sidereal, file=path, new_file='wcs-'+filename)
            full_arg = solve_arg.format(file=path, new_file=wcs_folder+rounded_sidereal+'.fit')
            print(full_arg) 
            
            while len(processes) >= args.threads:
                processes = [p for p in processes if not p.poll()]
                time.sleep(1)
            if not args.sterile:
                p = subprocess.Popen([full_arg], shell=True)
                processes.append(p)
    for p in processes:
        p.wait()

if __name__ == '__main__':
    args = get_args()
    main(args)
