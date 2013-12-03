dicom-merge
===========

merge serialized DICOM headers (as outputted by dcm4che's dcm2txt) with its raw pixel back into a DICOM file

usage
-----

Suppose `dcm2txt` peeled off headers from the original DICOM file `some-dicom.dcm` into `subject/CT/headers/some-dicom.txt` and raw pixels into `subject/CT/raw/some-dicom.raw`. You can merge the headers with their corresponding raw pixels into a DICOM file at `subject/CT/dicom/some-dicom.dcm` by pointing `merge.py` to `subject/CT`:

```bash
$ python merge.py subject/CT
```

So you should end up with a directory structure like this:
```
subject\
  CT\
    headers\
    raw\
    dicom\  
```

license
-------
MIT License

author
------
Falcon Dai