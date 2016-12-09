#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
import re
import urlparse
import robotparser
import datetime
import time


def download(url, user_agent='wswp', proxy=None, num_retries=2):
    print "Downloading:", url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)

    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))

    try:
        # html = urllib2.urlopen(request).read()
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, user_agent, proxy, num_retries-1)
    return html


def crawl_sitemap(url):
    # download the sitemap file
    sitemap = download(url)
    # extract the sitemap links
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    # download each link
    for link in links:
        html = download(link)
        # scrape html here
        # ...


def link_crawler(seed_url, link_regex):
    """Crawl from the given seed url following links matched by link_regex"""
    rp = robotparser.RobotFileParser()
    user_agent = 'wswp'
    crawl_queue = [seed_url]
    seen = set(crawl_queue)
    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            html = download(url)
            for link in get_links(html):
                if re.match(link_regex, link):
                    link = urlparse.urljoin(seed_url, link)
                    if link not in seen:
                        seen.add(link)
                        crawl_queue.append(link)
        else:
            print 'Blocked by robots.txt: ', url


def get_links(html):
    """Return a list of links from html"""
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


class Throttle:
    """Add a delay between downloads for each domain"""
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.datetime.now()

if __name__ == '__main__':
    # result = download('http://www.baidu.com')
    # print result
    # print type(result)
    # crawl_sitemap('http://example.webscraping.com/sitemap.xml')
    link_crawler('http://example.webscraping.com', '/(index|view)')