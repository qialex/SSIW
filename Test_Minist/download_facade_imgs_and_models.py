import sys
import requests
import zipfile
import shutil
import filecmp
import os

def download_file(link, file_name):
    with open(file_name, "wb") as f:
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')
        total_size_mb = int(total_length) / (1024 * 1024)
        print("Downloading %s, size %.2fMB" % (file_name, total_size_mb))    

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                dl_size_mb = int(dl) / (1024 * 1024)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s] %.2fMB / %.2fMB" % ('=' * done, ' ' * (50-done), dl_size_mb, total_size_mb) )    
            sys.stdout.write('\n')

# source
facades = {
    'source': 'https://cmp.felk.cvut.cz/~tylecr1/facade/',
    'link': 'https://cmp.felk.cvut.cz/~tylecr1/facade/',
    'zip_file_name': 'CMP_facade_DB',
    'db_types': ['base', 'extended'],
    'directory_to_extract_to': 'CMP_facade_DB',
}

sys.stdout.write("\nProcessing facades images from %s \n" % (facades['source']) )
for db_type in facades['db_types']:
    zip_file_name = '%s_%s.zip' % (facades['zip_file_name'], db_type)
    link = '%s%s' % (facades['link'], zip_file_name)
    download_file('%s%s' % (facades['link'], zip_file_name), zip_file_name)
    extract_to = facades['directory_to_extract_to']    
    sys.stdout.write("Extracting to %s\n" % (extract_to) )
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    copy_from = "label_names.txt"
    copy_to = "label_names_%s.txt" % (db_type)
    sys.stdout.write('Copying labels file from %s to %s \n' % (copy_from, copy_to))
    shutil.copyfile("%s/%s" % (extract_to, copy_from), "%s/%s" % (extract_to, copy_to))
    os.remove(zip_file_name)
    sys.stdout.write('\n')

are_labels_identical = filecmp.cmp("%s/label_names_%s.txt" % (facades['directory_to_extract_to'], facades['db_types'][0]), "%s/label_names_%s.txt" % (facades['directory_to_extract_to'], facades['db_types'][1]))
sys.stdout.write("Making sure labels files are identical: %s \n" % (str(are_labels_identical)))

# source
models = [
        {
            "source": "https://cloudstor.aarnet.edu.au/plus/s/gXaGsZyvoUwu97t/download",
            "filename": "universal_cat2vec.npy",
        },
        {
            "source": "https://cloudstor.aarnet.edu.au/plus/s/AtYYaVSVVAlEwve/download",
            "filename": "segformer_7data.pth",
        },
]

sys.stdout.write("\nDownloading models\n")
for model in models:
    filename = "models/%s" % (model["filename"])
    if (os.path.isfile(filename)):
        print("model file %s already exist" % (filename))
    else:
        download_file(model["source"], filename)
    sys.stdout.write('\n')

sys.stdout.write('\nDone\n')    