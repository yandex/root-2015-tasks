#!/usr/bin/env python

from HTMLParser import HTMLParser
import codecs, sys

class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.content = ''
        self.capturing = False
        self.level = 0
        self.target_level = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.level += 1
            if ('class', u'referats__text') in attrs:
                self.target_level = self.level
                self.capturing = True

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.target_level == self.level:
                self.capturing = False
            self.level -= 1

    def handle_data(self, data):
        if self.capturing:
            self.content += (data + '\n')

def main():
    parser = Parser()
    parser.feed(codecs.getreader('utf-8')(sys.stdin).read())
    print >> codecs.getwriter('utf-8')(sys.stdout), parser.content.strip()

if __name__ == '__main__':
    main()
