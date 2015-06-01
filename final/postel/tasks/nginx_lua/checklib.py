#!/usr/bin/env python3

import logging
import random
import re
import sys
import traceback

__all__ = ['STATUS_OK', 'STATUS_NOT_OK', 'STATUS_INTERNAL_ERROR', 'Checker', 'run_checker', 'InternalException']

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

IPV4_RE = re.compile(r'^\d{1,3}\.\d{,3}\.\d{,3}\.\d{,3}(:\d{,5})?$')

class Checker:
    '''
    Run check functions one by one. 

    Example:
    return inline_checks(
        (check_drupal, host),
        (check_wordpress, host),
        (check_oldbrowser, host)
        )

    runs
    check_drupal(host). If it returned not `STATUS_OK`, `inline_checks` will stop and return this result.
    If check_drupal(host) returned `STATUS_OK`, `inline_checkes` will run check_wordpress and so on...
    '''
    def inline_checks(self, *checks):
        for check in checks:
            if type(check) is not tuple or len(check) < 1:
                raise ValueError('Invalid check: %s. Need a tuple (func, *args)' % str(check))
            func, *args = check
            result = func(*args)
            if result == None:
                raise ValueError('Check function in `inline_checks` can\'t return None, it should return one of statuses')
            if result != STATUS_OK:
                return result
        return STATUS_OK

        
'''
Main function for running your checker.
>>> checklib.run_checker(MyOwnChecker())
'''
def run_checker(checker):
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d.%m.%Y %H:%M:%S', level=logging.DEBUG)
    logging.info('Starting checker with arguments: ' + ', '.join(sys.argv))
    
    if len(sys.argv) < 2:
        exit_code = STATUS_INTERNAL_ERROR
    else:
        host = sys.argv[1]
        if not IPV4_RE.match(host):
            logging.error('Invalid address. My regexp doesn\'t allow it!')
            exit_code = STATUS_INTERNAL_ERROR
        else:
            try:
                exit_code = checker.check(host)
            except Exception as e:
                logging.error('Internal exception in checker: %s', e)
                logging.error(traceback.format_exc())
                exit_code = STATUS_NOT_OK

    logging.info('Exiting with code %s', exit_code)
    sys.exit(exit_code)


'''
Base of all internal in-checker exceptions
'''
class InternalException(Exception):
    pass


if __name__ == "__main__":
    print('''
You can\'t run checklib.py directly. Create your own checker from the template:

import checklib

class MyOwnChecker(checklib.Checker):
    def check(self, host):
        return checklib.STATUS_OK

if __name__ == "__main__":
    checklib.run_checker(MyOwnChecker())

''')