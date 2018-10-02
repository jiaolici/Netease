# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy import Request
from selenium import webdriver
from scrapy.http import HtmlResponse
from scrapy.exceptions import IgnoreRequest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.common.keys import Keys


class NeteaseSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

# Browser=webdriver.Chrome()

class PageDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        self.browser=webdriver.Chrome()
        self.wait=WebDriverWait(self.browser,timeout=5)

    def __del__(self):
        self.browser.close()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        if request.callback==spider.parse_search and request.meta['page']==1 and spider.max_page==0:
            self.browser.get(request.url)
            self.browser.switch_to.frame('contentFrame')
            try:
                self.browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div[3]/div/span')
                spider.max_page = int(self.browser.find_element_by_xpath(
                    '/html/body/div[3]/div/div[2]/div[3]/div/a[last()-1]').text)  # 下一页前面的a节点也就是最大页数
            except NoSuchElementException:
                xpath='/html/body/div[3]/div/div[2]/div[3]/div/a[last()-%s]'
                for i in range(0,9):
                    try:
                        spider.max_page = int(self.browser.find_element_by_xpath(xpath % i).text)
                        break
                    except ValueError:
                        continue
            try:
                self.wait.until(expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, '/html/body/div[3]/div/div[2]/div[2]/div/table/tbody/tr')))
            except TimeoutException:
                print('重新请求第一页')
                return Request(url=self.browser.current_url, callback=spider.parse_search, dont_filter=True,
                               meta={'page': request.meta['page']})
            return HtmlResponse(url=self.browser.current_url,body=self.browser.page_source,request=request,encoding='utf-8',status=200)
        elif request.callback==spider.parse_search and spider.max_page>request.meta['page']>1:
            self.browser.get(request.url)
            self.browser.switch_to.frame('contentFrame')
            for i in range(request.meta['page']-1):#点击这么多次下一页
                try:
                    nxt=self.wait.until(expected_conditions.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div/div[2]/div[3]/div/a[last()]')))
                    nxt.send_keys(Keys.ENTER)
                except TimeoutException:
                    print('重新请求第%s页' % request.meta['page'])
                    return Request(url=self.browser.current_url, callback=spider.parse_search,dont_filter=True,meta={'page':request.meta['page']})
                    # raise IgnoreRequest
            try:
                self.wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH,'/html/body/div[3]/div/div[2]/div[2]/div/table/tbody/tr')))
            except TimeoutException:
                print('重新请求第%s页'%request.meta['page'])
                return Request(url=self.browser.current_url, callback=spider.parse_search, dont_filter=True,
                               meta={'page': request.meta['page']})
                # raise IgnoreRequest
            return HtmlResponse(url=self.browser.current_url, body=self.browser.page_source, request=request,encoding='utf-8', status=200)
        elif request.callback==spider.parse_search and spider.max_page==request.meta['page']:
            self.browser.get(request.url)
            self.browser.switch_to.frame('contentFrame')
            try:
                last=self.wait.until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/div[3]/div/div[2]/div[3]/div/a[last()-1]')))
                self.wait.until(expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, '/html/body/div[3]/div/div[2]/div[2]/div/table/tbody/tr')))
                last.send_keys(Keys.ENTER)
            except TimeoutException:
                print('重新请求最后一页')
                return Request(url=self.browser.current_url, callback=spider.parse_search,dont_filter=True,meta={'page':spider.max_page})
                # raise IgnoreRequest
            return HtmlResponse(url=self.browser.current_url, body=self.browser.page_source, request=request,
                                encoding='utf-8', status=200)
        elif request.callback==spider.parse_musiclist:
            self.browser.get(request.url)
            self.browser.switch_to.frame('contentFrame')
            try:
                self.wait.until(expected_conditions.presence_of_all_elements_located(
                    (By.XPATH,'/html/body/div[3]/div[1]/div/div/div[2]/div[2]/div/div[1]/table/tbody/tr')))
                btn = self.browser.find_element(By.ID, 'album-desc-spread')
                btn.send_keys(Keys.ENTER)
            except TimeoutException:
                # return Request(url=self.browser.current_url,callback=spider.parse_musiclist,dont_filter=True)
                print('忽略这个歌单')
                raise IgnoreRequest
            except:
                print('没有过多介绍,%s'%self.browser.title)
            return HtmlResponse(url=self.browser.current_url, body=self.browser.page_source, request=request,
                                encoding='utf-8', status=200)
        elif request.callback==spider.parse_music:
            self.browser.get(request.url)
            self.browser.switch_to.frame('contentFrame')
            try:
                self.wait.until(expected_conditions.presence_of_element_located((By.XPATH,'//*[@id="lyric-content"]')))
                btn=self.browser.find_element(By.ID,'flag_ctrl')
                btn.send_keys(Keys.ENTER)
            except TimeoutException:
                # return Request(url=self.browser.current_url,callback=spider.parse_music,dont_filter=True)#重新request
                print('忽略这首歌:',self.browser.title)
                raise IgnoreRequest
            except:
                print('没有更多歌词')
            return HtmlResponse(url=self.browser.current_url, body=self.browser.page_source, request=request,
                                encoding='utf-8', status=200)
        else:
            return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
