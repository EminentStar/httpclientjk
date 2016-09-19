import requests
import unittest
from unittest import mock


header_ok_naver = {'Server': 'nginx', 
        'P3P': 'CP="CAO DSP CURa ADMa TAIa PSAa OUR LAW' +
        'STP PHY ONL UNI PUR FIN COM NAV INT DEM STA PRE"', 
        'X-Frame-Options': 'SAMEORIGIN',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Transfer-Encoding':'chunked', 
        'Content-Type': 'text/html; charset=UTF-8',
        'Connection': 'close',
        'Date': 'Mon, 19 Sep 2016 17:11:37 GMT',
        'Pragma': 'no-cache'}

def is_correct_get_response():
    try:
        status_line = requests.get('www.naver.com')
    except IOError:
        pass
    else:
        return status_line == 'HTTP/1.1 200 OK'


def get_fake_get(status_line):
    m = mock.Mock()
    m.status_line = status_line
    def fake_get(url):
        return m.status_line
    return fake_get


def are_same_dict(dict_1, dict_2):
    if len(dict_1) != len(dict_2):
        return False
    for k, v in dict_1.items():
        if k not in dict_2:
            return False
        elif dict_2[k] != v:
            return False
    return True


class TestRequests(unittest.TestCase):
    @mock.patch('requests.get', get_fake_get('HTTP/1.1 200 OK'))
    def test_get_ok(self):
        self.assertTrue(is_correct_get_response())


if __name__ == '__main__':
    unittest.main()
