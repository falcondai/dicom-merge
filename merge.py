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
    if len(sys.argv) < 2:
        print 'Usage: %s <path-to-CT-or-MRI>' % sys.argv[0]
        sys.exit(1)
    dir_path = sys.argv[1]

    output_dir = os.path.join(dir_path, 'dicom')
    if os.path.exists(output_dir):
        # don't overwrite existing dicom directory
        print 'WARNING: output directory %s exists' % output_dir
        sys.exit(1)
    else:
        os.mkdir(output_dir)
        print 'Created directory %s' % output_dir

    raw_fns = glob.glob(os.path.join(dir_path, 'raw', '*.raw'))
    for raw_fn in raw_fns:
        fn = os.path.basename(raw_fn)[:-4]
        with open(os.path.join(dir_path, 'headers', '%s.txt' % fn), 'rb') as header:
            ds = parse_header(header)
        with open(raw_fn, 'rb') as raw:
            output_fn = os.path.join(output_dir, '%s.dcm' % fn)
            print 'writing %s' % output_fn
            merge_header_raw(ds, raw, output_fn)
