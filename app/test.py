# coding=utf-8

import unittest
from app.main import *


class TestFunctions(unittest.TestCase):

    def test_get_filename(self):
        self.assertEqual('apple-touch-icon.png', get_filename('apple-touch-icon.png'))
        self.assertEqual('apple-touch-icon.png', get_filename('/apple-touch-icon.png'))
        self.assertEqual('apple-touch-icon.png', get_filename('../assets/images/apple-touch-icon.png'))
        self.assertEqual('bootstrap.min.css', get_filename('../../global/css/bootstrap.min.css?v2.2.0'))
        self.assertEqual('skintools.min.js', get_filename('../assets/js/sections/skintools.min.js'))
        self.assertEqual('logo.png', get_filename('http://abc.com/assets/images/logo.png'))

    def test_get_pathname(self):
        self.assertEqual('/assets/images', get_pathname('http://abc.com/assets/images/apple-touch-icon.png'))
        self.assertEqual('/global/css', get_pathname('http://abc.com/global/css/bootstrap.min.css?v2.2.0'))
        self.assertEqual('/assets/js/sections', get_pathname('http://abc.com/assets/js/sections/skintools'))

    def test_get_absolute_url(self):
        self.assertEqual('http://abc.com/home/b.html', get_absolute_url('http://abc.com/home', 'b.html'))
        self.assertEqual('http://abc.com/home/a/b.html', get_absolute_url('http://abc.com/home', 'a/b.html'))
        self.assertEqual('http://abc.com/home/a/b.html', get_absolute_url('http://abc.com/home/', 'a/b.html'))
        self.assertEqual('http://abc.com/a/b.html', get_absolute_url('http://abc.com/home', '../a/b.html'))
        self.assertEqual('http://abc.com/a/b.html', get_absolute_url('http://abc.com/home/', '../a/b.html'))
        self.assertEqual('http://abc.com/a/b.html', get_absolute_url('http://abc.com/ho/me', '../../a/b.html'))
        self.assertEqual('http://abc.com/a/b.html', get_absolute_url('http://abc.com/ho/me/', '../../a/b.html'))

    def test_get_res_urls(self):
        root_url = 'http://abc.com/theme/abc'
        suffix_list = ['.jpg', '.js', '.html']
        html_content = '''
            <html>
                <a href="uikit/colors.html">Colors</a>
                <script src="../global/vendor/s/s.min.js"></script>
                <script src="../../global/vendor/aaa/aaa.min.js"></script>
                <link rel="stylesheet" href="../global/vendor/c-js/c.min.css?v2.2.0">
                <img class="width-full" src="../global/photos/view-1-150x100.jpg" alt="..." />
            </html>
        '''
        res_urls = get_res_urls(html_content, root_url, suffix_list)

        self.assertEqual(4, len(res_urls))
        self.assertEqual('http://abc.com/theme/abc/uikit/colors.html', res_urls[0])
        self.assertEqual('http://abc.com/theme/global/vendor/s/s.min.js', res_urls[1])
        self.assertEqual('http://abc.com/global/vendor/aaa/aaa.min.js', res_urls[2])
        self.assertEqual('http://abc.com/theme/global/photos/view-1-150x100.jpg', res_urls[3])

    def test_get_root_url(self):
        self.assertEqual('http://abc.com/home/', get_root_url('http://abc.com/home'))
        self.assertEqual('http://abc.com/home/', get_root_url('http://abc.com/home/'))
        self.assertEqual('http://abc.com/home/', get_root_url('http://abc.com/home/something.htm'))
        self.assertEqual('http://abc.com/home/', get_root_url('http://abc.com/home/something.html'))


if __name__ == '__main__':
    unittest.main()
