# coding=utf-8

import os
import urllib
import urllib2
import urlparse
import re
import logging
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler

_STORAGE_ROOT = '/home/yaolu/Desktop'

_LOG_FORMAT = '%(asctime)s %(levelname)s %(module)s.%(funcName)s:%(lineno)d %(message)s'
_LOG_FILE_NAME = 'template-downloader.log'
_LOG_FILE_BASE = _STORAGE_ROOT
_LOG_FILE_SUFFIX = '%Y%m%d'

_PROCESSED_URLS = []


def create_log():
    """
    Create a log handler
    """
    log = logging.getLogger('download.log')
    if len(log.handlers) > 0:
        return log

    logging.basicConfig(format=_LOG_FORMAT)
    formatter = Formatter(_LOG_FORMAT)
    handler = TimedRotatingFileHandler(_LOG_FILE_BASE + '/' + _LOG_FILE_NAME, 'midnight', 1, 365)
    handler.setFormatter(formatter)
    handler.suffix = _LOG_FILE_SUFFIX
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log

_LOG = create_log()


def http_get(url):
    """
    Download HTTP content via get method.
    """
    req = urllib2.Request(url)
    res = None
    try:
        res = urllib2.urlopen(req).read()
    except urllib2.HTTPError as err:
        if err.code == 404:
            _LOG.error('Not found ' + url)
        else:
            _LOG.error('HTTP error %d: %s' % (err.code, url))
    finally:
        return res


def create_dir(pathname):
    """
    Create a local directory by the parsed result of a HTTP URL, if not exists.
    """
    complete_path = _STORAGE_ROOT + pathname
    if not os.path.isdir(complete_path):
        _LOG.info('Creating new directory %s ' % complete_path)
        os.makedirs(complete_path)


def get_filename(url):
    """
    Extract the filename from a HTTP URL, usually the last part.
    This function will remove any additional arguments appended after the question symbol.
    """
    last_slash_pos = url.rfind('/')
    if last_slash_pos < 0:
        last_slash_pos = 0
    else:
        last_slash_pos += 1
    question_pos = url.rfind('?')
    if question_pos < 0:
        question_pos = len(url)
    return url[last_slash_pos:question_pos]


def get_pathname(url):
    """
    Extract the pathname from a HTTP URL.
    """
    path = urlparse.urlparse(url).path
    last_slash_pos = path.rfind('/')
    if last_slash_pos < 0:
        last_slash_pos = len(path)
    return path[0:last_slash_pos]


def get_root_url(url):
    """
    Extract the context path from a URL
    """
    if url.endswith('.htm') or url.endswith('.html'):
        return url[0:url.rfind('/')+1]

    if not url.endswith('/'):
        url += '/'
    return url


def save_res_file(url, filename=None):
    """
    Saving a static resource file from a HTTP URL.
    """
    final_filename = filename if filename else get_filename(url)

    pathname = get_pathname(url)
    create_dir(pathname)

    filepath = _STORAGE_ROOT + pathname + '/' + final_filename
    if not os.path.exists(filepath):
        _LOG.info('Downloading ' + url)

        try:
            opener = urllib.URLopener()
            opener.retrieve(url, filepath)
        except IOError as err:
            _LOG.error(err)


def get_absolute_url(root_url, relative_url):
    """
    Construct an absolute URL from a relative url.
    This function assumes that the relative URL has a valid suffix.
    """
    parts = relative_url.split('/')
    if not parts:
        return ''

    absolute_url = root_url
    if not absolute_url.endswith('/'):
        absolute_url += '/'

    parts = parts[:-1]
    for part in parts:
        if part == '..':
            if absolute_url.endswith('/'):
                absolute_url = absolute_url[:-1]
            absolute_url = absolute_url[0:absolute_url.rfind('/')+1]
        else:
            absolute_url += part + '/'
    return absolute_url + get_filename(relative_url)


def get_res_urls(html_content, root_url, suffix_list):
    """
    Extract all URLs with all given suffixes from the html content under the same domain.
    """
    raw_urls = re.compile(r'[src|href]="(.*?)"').findall(html_content)
    relative_urls = []
    for url in raw_urls:
        filename = get_filename(url)
        for suffix in suffix_list:
            if filename.endswith(suffix):
                relative_urls.append(url)
    urls = [get_absolute_url(root_url, relative_url) for relative_url in relative_urls]
    return urls


def process_html_page(url, custom_filename=None):
    """
    Process a single HTML page.
    """
    if url not in _PROCESSED_URLS:
        _PROCESSED_URLS.append(url)
    else:
        return

    _LOG.info('Processing ' + url)

    html_content = http_get(url)
    if html_content is None or len(html_content) is 0:
        _LOG.error('Content is empty!')
        return

    pathname = get_pathname(url)
    create_dir(pathname)

    filename = custom_filename if custom_filename is not None else get_filename(url)
    save_res_file(url, filename)

    root_url = get_root_url(url)

    _LOG.info('Saving static resources...')
    res_urls = get_res_urls(html_content, root_url, ['.js', '.css', '.jpeg', '.jpg', '.png', '.ico'])
    for res_url in res_urls:
        save_res_file(res_url)

    html_urls = get_res_urls(html_content, root_url, ['.html', '.htm'])
    _LOG.info('Preparing to process %d URLs from current page...' % len(html_urls))

    for html_url in html_urls:
        process_html_page(html_url)


if __name__ == '__main__':
    index_url = 'http://getbootstrapadmin.com/remark/topbar/'
    process_html_page(index_url, 'index.html')
