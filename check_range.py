import argparse, re, os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    parser.add_argument('lower_bound')
    parser.add_argument('upper_bound')
    args = parser.parse_args()

    if args.folder[-1] != '/':
        args.folder += '/'


    return args

def main(args):
    r = re.compile('(.*)h(.*)m')
    matchl = r.match(args.lower_bound)
    
    tl = int(matchl.group(1)) * 60 + int(matchl.group(2))

    match2 = r.match(args.upper_bound)

    tu = int(match2.group(1)) * 60 + int(match2.group(2))

    for t in range(tl, tu+1):
        if not os.path.isfile(args.folder + '{0:02d}h{1:02d}m.fit'.format(t/60, t%60)):
            print('{0:02d}h{1:02d}m.fit'.format(t/60, t%60))


if __name__ == '__main__':
    args = get_args()
    main(args)
