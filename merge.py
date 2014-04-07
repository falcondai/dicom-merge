#!/usr/bin/env python

import sys, re, glob, os

import dicom

header_pattern = re.compile(r'\((\w+),(\w+)\) +[^ ]+ +(\w\w) \[(.+)\]')

def tag_from_str(g_str, e_str):
    return (int(g_str, 16), int(e_str, 16))

def parse_header(fp, pattern=header_pattern):
    header_text = fp.read()
    headers = pattern.findall(header_text)
    
    ds = dicom.dataset.Dataset()
    for gs, es, vr, val in headers:
        if '\\' in val:
            # value is a sequence
            val = val.split('\\')
        elif ',' in val and vr == 'US':
            val = val.split(',')
            
        de = dicom.dataelem.DataElement(tag_from_str(gs, es), vr, val)
        #if de.tag != (0x02, 0x00):
            # the meta element group length is not going to be correct
        ds[de.tag] = de
    return ds


def merge_header_raw(dataset, raw, filename):
    fds = dicom.dataset.FileDataset(filename, dataset)
    fds.PixelData = raw.read()
    fds.save_as(filename)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to CT/MR directory')
    parser.add_argument('-f', '--force', action='store_true', help='overwrite dicom folder if it already exists')
    parser.add_argument('-s', '--skip', action='store_true', help='skip raw files without corresponding header files')

    args = parser.parse_args()

    dir_path = args.path
    output_dir = os.path.join(dir_path, 'dicom')
    if os.path.exists(output_dir) and not args.force:
        # don't overwrite existing dicom directory
        print 'WARNING: output directory %s exists' % output_dir
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        print 'Created directory %s' % output_dir

    raw_fns = glob.glob(os.path.join(dir_path, 'raw', '*.raw'))
    for raw_fn in raw_fns:
        fn = os.path.basename(raw_fn)[:-4]

        if os.path.exists(os.path.join(dir_path, 'headers', '%s.txt' % fn)):
            header_path = os.path.join(dir_path, 'headers', '%s.txt' % fn)
        elif os.path.exists(os.path.join(dir_path, 'headers', '%s.dcm.txt' % fn)):
            header_path = os.path.join(dir_path, 'headers', '%s.dcm.txt' % fn)
        else:
            print 'WARNING: no corresponding header file found for %s' % raw_fn
            if args.skip:
                continue
            else:
                sys.exit(1)
        with open(header_path, 'rb') as header:
            ds = parse_header(header)

        with open(raw_fn, 'rb') as raw:
            output_fn = os.path.join(output_dir, '%s.dcm' % fn)
            print 'writing %s' % output_fn
            merge_header_raw(ds, raw, output_fn)
