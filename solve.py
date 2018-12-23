# sanitize to lowercase extension first
# collect folder of images to solve
import shutil
try:
    import sidereal
except SyntaxError:
    pass
import argparse, subprocess, os, time, re, math
from astropy.io import fits
from astropy.time import Time
try:
    from pyraf.iraf import immatch
    from pyraf.iraf import imutil
except ImportError:
    pass

client_path = '/Users/jake/Desktop/sextraction/astrometry.net/net/client/client.py'

allowance = 1.25

def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='mode')

    ref_solve_parser = subparsers.add_parser('ref')
    mass_solve_parser = subparsers.add_parser('mass')
    stat_parser = subparsers.add_parser('stat')
    sex_parser = subparsers.add_parser('sex')

    ref_solve_parser.add_argument('im_folder', help='folder of images to solve')
    ref_solve_parser.add_argument('-threads', type=int, help='number of threads')
    ref_solve_parser.add_argument('-sterile', action='store_true')
    
    mass_solve_parser.add_argument('im_folder', help='folder of images to solve')
    mass_solve_parser.add_argument('ref_folder', help='folder of solved ref images')
    mass_solve_parser.add_argument('lower_sid_bound', type=float, help='lower bound on sid range to solve')
    mass_solve_parser.add_argument('upper_sid_bound', type=float, help='upper bound on sid range to solve')
    mass_solve_parser.add_argument('stem')

    stat_parser.add_argument('im_folder', help='folder of images to solve')
    stat_parser.add_argument('data_file_name')
    stat_parser.add_argument('stem')
   
    sex_parser.add_argument('im_folder', help='folder of images to solve')
    sex_parser.add_argument('index_filename')
    sex_parser.add_argument('stem')

    args = parser.parse_args()
    
    if args.im_folder[-1] != '/':
        args.im_folder += '/'

    if args.mode == 'mass' and args.ref_folder[-1] != '/':
        args.ref_folder += '/'

    if args.mode == 'ref' and not args.threads:
        args.threads = 5
    
    return args

class SidTime():
    def __init__(self, st):
        self._st = st
        
    def rounded_mins(self):
        return round(self._st.hours * 60) / 60

    def rounded_str(self):
        decimal_mins = self._st.hours * 60
        mins = int(decimal_mins % 60)
        hours = int(((decimal_mins - mins)/60) % 24)
        
        return '{0:02d}h{1:02d}m'.format(hours, mins)

    def __str__(self):
        return str(self._st)

'''
def sid_round(sid_time):
    print(sid_time)
    sid_time = re.split(r'[^0-9.]+', sid_time[1:-1])
    decimal_mins = round(int(sid_time[0]) * 60 + int(sid_time[1]) + float(sid_time[2]) / 60.0)
    mins = int(decimal_mins % 60)
    hours = int(((decimal_mins - mins)/60) % 24)

    return '{0:02d}h{1:02d}m'.format(hours, mins)
'''
def mass_stat(args):
    files = os.listdir(args.im_folder)
    with open(args.data_file_name, 'a') as data_file:
        for filename in files:
            if filename.startswith(args.stem) and (filename.endswith(".fit") or filename.endswith(".fits")):
                im_path = args.im_folder + filename
                image = fits.open(im_path)
                date = image[0].header['DATE-OBS']
                dt = sidereal.parseDatetime(date)
                st = SidTime(sidereal.SiderealTime.fromDatetime(dt).lst(-2.05393104))
                data_file.write(date + '     ' + str(st) +  imutil.imstat(im_path, Stdout=1)[1] + '\n')

def star_indexed(index_file, line):
    data = line.split()
    ra = float(data[4])
    dec = float(data[5])
    j = 0
    for line in index_file.readlines():
        star = line.split()
        if ra - allowance <= float(star[1]) <= ra + allowance and dec - allowance <= float(star[2]) <= dec + allowance:
            return int(star[0]), None
        else:
            j = int(star[0])
    return None, j+1

def sex(args):
    if not os.path.isfile(args.index_filename):
        f = open(args.index_filename, 'w')
        f.close()
    
    files = os.listdir(args.im_folder)
    for filename in files:
        if filename.startswith(args.stem) and (filename.endswith(".fit") or filename.endswith(".fits")):
            im_path = args.im_folder + filename
            image = fits.open(im_path)
            date = image[0].header['DATE-OBS']
            output_filename = filename + '.cat'
            
            sex_arg = 'sex {image} -c default.sex -CATALOG_NAME {cat_name}'.format(image=im_path,
                                                                                   cat_name=output_filename)
            subprocess.call([sex_arg],shell=True)

            with open(output_filename, 'r') as output_file:
                for line in output_file.readlines()[12:]:
                    with open(args.index_filename, 'r+') as index_file:
                        i, j = star_indexed(index_file, line)
                        if i:
                            with open(str(i) + '.star', 'a') as star_file:
                                star_file.write(line)
                        else:
                            data = line.split()
                            index_file.write(str(j) + '\t' + data[4] + '\t' + data[5] + '\n')
                            with open(str(j) + '.star', 'w') as star_file:
                                star_file.write(line)

def mass_solve(args):
    if not os.path.isdir(args.im_folder + '/solved'):
        os.mkdir(args.im_folder + '/solved')
    files = os.listdir(args.im_folder)
    for filename in files:
        if filename.startswith(args.stem) and (filename.endswith(".fit") or filename.endswith(".fits")):
            im_path = args.im_folder + filename
            image = fits.open(im_path)
            date = image[0].header['DATE-OBS']
            dt = sidereal.parseDatetime(date)
            st = SidTime(sidereal.SiderealTime.fromDatetime(dt).lst(-2.05393104))
            
            if args.lower_sid_bound <= st.rounded_mins() <= args.upper_sid_bound:
                ref_path = args.ref_folder + st.rounded_str() + '.fit'
                if os.path.isfile(ref_path): 
                    immatch.wcscopy(im_path, ref_path)
                    shutil.copy2(im_path, args.im_folder + '/solved/' + filename)
                    #os.rename(im_path, args.im_folder + '/solved/' + filename)
'''
def sextract():
    arg = 'sex {file} -c default.sex'.format{file=file_name}
    subprocess.Popen([arg],shell=True)



'''


def main(args):
    if args.mode == 'sex':
        sex(args)
        return
    if args.mode == 'mass':
        mass_solve(args)
        return
    if args.mode == 'stat':
        mass_stat(args)
        return
    
    key = 'vsrjqdfgoomarrpf'
    ra = -117.68158
    dec = 34.38183

    #solve_arg = 'python {client} --apikey {key} --parity 0 --downsample 1 --ra {{ra}} --dec {dec} --upload {{file}} --wcs {{new_file}}'.format(client=client_path, key=key, dec=dec)
    solve_arg = 'python {client} --apikey {key} --downsample 1  --upload {{file}} --wcs {{new_file}}'.format(client=client_path, key=key, dec=dec)
    if not os.path.isdir(args.im_folder + 'wcs/'):
        os.mkdir(args.im_folder + 'wcs/')
    processes = []
    files = os.listdir(args.im_folder)

    while files:
        filename = files.pop()
        print(filename)
        if filename.endswith(".fit") or filename.endswith(".fits"):
            path = args.im_folder + filename
            wcs_folder = args.im_folder + 'wcs/'
            image = fits.open(path)
            date = image[0].header['DATE-OBS']
            dt = sidereal.parseDatetime(date)
            st = SidTime(sidereal.SiderealTime.fromDatetime(dt).lst(-2.05393104))
            wcs_path = wcs_folder+st.rounded_str()+'.fit'
            if not os.path.isfile(wcs_path):
                #full_arg = solve_arg.format(ra=sidereal, file=path, new_file='wcs-'+filename)
                full_arg = solve_arg.format(file=path, new_file=wcs_path)
                print(full_arg) 
                print(processes) 
                while len(processes) >= args.threads:
                    processes = [p for p in processes if p.poll() == None]
                    time.sleep(1)
                if not args.sterile:
                    p = subprocess.Popen([full_arg], shell=True)
                    processes.append(p)
    for p in processes:
        p.wait()

if __name__ == '__main__':
    args = get_args()
    main(args)
