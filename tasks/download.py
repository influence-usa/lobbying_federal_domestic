import json
import zipfile,StringIO
import os
import subprocess
import logging
import threading
import collections

import requests

from settings import CACHE_DIR
from tasks.utils import mkdir_p

class Downloader(object):
    """
    Downloads from `url` to `destination`

    Downloader from some HTTP `url` to some `destination` on the
    filesystem, which is relative to the `CACHE_DIR` value in `settings.py`

    ### Args ###

    `url` (string)
    :   usually an HTTP url

    `destination` (string)
    :   a file path, assumed to be relative to the CACHE_DIR in settings, 
        specifying the directory where downloaded file should be placed.

    ### Keyword Args ###

    `force` (boolean)
    :   if `True`, download without checking cache first, overwriting 
        anything that might currently reside at `destination`. if not 
        specified, assumed to be `False`.

    ### Example Usage ###

        zip_url = 'http://soprweb.senate.gov/downloads/1999_1.zip'
        output_dir = 'sopr/1999'
        d = Downloader(zip_url, output_dir)
        d.download()

        options = {'force': True}
        d2 = Downloader(zip_url, output_dir, options)
        d2.download()
    """
    
    def __init__(self, url, destination, **options):
        self.fname = requests.utils.urlparse(url).path.split('/')[-1]
        self.url = url
        self.output_dir = os.path.join(CACHE_DIR, destination)
        self.output_loc = os.path.join(self.output_dir, self.fname)

        if not os.path.exists(self.output_dir):
            mkdir_p(self.output_dir)

        if options['force']:
            self._download = self._download_file
        else:
            self._download = self._check_cache_first

    def download(self):
        """
        Actually performs the download. Will check cache unless `Downloader` was
        initialized with `options['force'] == True`

        ### Example Usage ###

            zip_url = 'http://soprweb.senate.gov/downloads/1999_1.zip'
            output_dir = 'sopr/1999'
            d = Downloader(zip_url, output_dir)
            d.download()
        """

        self._download()

    def _download_file(self):
        """
        Download file and write to disk
        """
        if not self.request:
            self.request = requests.get(self.url, stream=True)
        if self.request.ok:
            self._write_file()
            return
        else:
            logging.error('{status_code}: "{reason}", ({url})'.format(
                          status_code=self.request.status_code, 
                          reason=self.request.reason, 
                          url=self.url
                          )
                    )
    
    def _write_file(self):
        """
        Write file to disk
        """
        if os.path.exists(self.output_loc):
            logging.debug('overwriting file at {loc}'.format(self.output_loc))
        with open(self.output_loc,'wb') as output_file:
            for chunk in self.request.iter_content: 
                output_file.write(chunk)

    def _check_cache_first(file):
        """
        Check to see if file already exists and whether it is the same size as
        file to be downloaded. If both are true, call `_download_file`
        """
        self.request = requests.get(self.url, stream=True)
        if os.path.exists(self.output_loc):
            downloaded_size = os.path.getsize(self.output_loc)
            logging.debug(
                'found {output_loc}: {size}'.format(
                        url=self.url,
                        size=downloaded_size
                        )
                    )
            size_on_server = self.request.headers['content-length']
            if cached_size != size_on_server:
                logging.debug(
                    're-downloaded {url}: {size}'.format(
                            url=self.url,
                            size=size_on_server
                            )
                        )
                self._download_file()
            else:
                return
        else:
            self._download_file()


class DownloaderThread(threading.Thread):
    """
    Worker thread for multithreaded downloading with `MultipleDownloader`. Runs
    in daemon mode.

    ### Args ###
    `deque` (collections.deque)
    :    deque of `(url, destination)` tuples

    ### Keyword Args ###

    None used.

    """
    
    def __init__(self, deque, **options):
        super(DownloaderThread, self).__init__()
        self.deque = deque
        self.options = options
        self.daemon = True
    def run(self):
        """
        pop a tuple off of the deque, initialize a downloader, and download.
        """
        while True:
            url, destination  = self.deque.popleft()
            downloader = Downloader(url, destination, **self.options)
            downloader.run()


class MultipleDownloader(object):
    """
    Container for downloading multiple files, either synchronously or using
    multithreading.

    ### Args ###

    `path_destination_pairs` (iterable)
    :    iterable of `(url, destination)` tuples

    ### Keyword Args ###

    `threaded` (boolean)
    :    if `True`, perform downloades using multiple threads

    `base_url` (string)
    :   base url to prepend to all download paths

    `worker_num` (int)
    :   number of worker threads to use

    ### Example Usage ###

        pdp = [ ('1999_1.zip', 'sopr/1999/Q1'),
                ('1999_2.zip', 'sopr/1999/Q2'),
                ('1999_3.zip', 'sopr/1999/Q3'),
                ('1999_4.zip', 'sopr/1999/Q4') ]
        bu = 'http://soprweb.senate.gov/downloads/'
        md = MultipleDownloader(pdp, base_url=bu, threaded=True, worker_num=10)
        md.run()
    """

    def __init__(self, path_destination_pairs, **options):
        
        self.options = options
        self.base_url = self.options.get('base_url', False)
        self.worker_num = self.options.get('worker_num', 5)
        
        if self.base_url:
            if not self.base_url[-1] == '/':
                self.base_url += '/'
        else:
            self.base_url = ''

        self._build_deque(path_destination_pairs)

        if self.options['threaded']:
            self._run = self._run_threaded()
        else:
            self._run = self._run_synchronous()

    def run(self):
        """
        Perform all downloads.
        """
        logging.info('downloading {num_paths} files from {base_url}'.format(
                     num_paths=len(path),
                     base_url=base_url
                     )
                )
        self._run()

    def _build_deque(self, path_destination_pairs): 
        """
        Append `path_destination_pairs` to a `collections.deque`
        """
        self.deque = collections.deque()
        for p,d in path_destination_pairs:
            self.deque.append((self.base_url+p, d))

    def _run_threaded(self):
        """
        Perform threaded download of all files, with `worker_num` workers.
        """
        for i in range(worker_num):
            t = DownloaderThread(self.deque, **self.options)
            t.start()

    def _run_synchronous(self):
        """
        Perform download of all files, sequentially.
        """
        for i in xrange(len(self.deque)):
            url, destination = self.deque.popleft()
            downloader = Downloader(url, destination, **self.options)
            downloader.run()
