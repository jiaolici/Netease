# -*- coding: utf-8 -*-
import scrapy
from .. import items


class SearchSpider(scrapy.Spider):
    name = 'search'
    allowed_domains = ['music.163.com']
    start_urls = ['http://music.163.com/']
    search_url='https://music.163.com/#/search/m/?s={key_word}&type=1000'
    base_url='https://music.163.com/#'
    max_page=0
    def start_requests(self):
        url=self.search_url.format(key_word=self.settings.get('KEY_WORD'))
        yield scrapy.Request(url,callback=self.parse_search,meta={'page':1})

    def parse_search(self, response):
        music_lists=response.xpath('/html/body/div[3]/div/div[2]/div[2]/div/table/tbody/tr')
        for music_list in music_lists:
            url=self.base_url+music_list.xpath('./td[3]/div/div[2]/div/span/a/@href').extract_first(default='')
            print(url)
            yield scrapy.Request(url,callback=self.parse_musiclist,dont_filter=True)
        if response.meta['page']<self.max_page:
            url = self.search_url.format(key_word=self.settings.get('KEY_WORD'))
            yield scrapy.Request(url,callback=self.parse_search,dont_filter=True,meta={'page':response.meta['page']+1})

    def parse_musiclist(self, response):
        musiclist_item=items.MusicListItem()
        musiclist_item['name']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[1]/div/h2/text()').extract_first(default='')
        musiclist_item['url']=response.url
        musiclist_item['cover_url']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/img/@src').extract_first(default='')
        musiclist_item['cover_url']=musiclist_item['cover_url'].split('?param')[0] if musiclist_item['cover_url'] else None
        musiclist_item['author']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[1]/a/text()').extract_first(default='')
        musiclist_item['play_count']=response.xpath('//*[@id="play-count"]/text()').extract_first(default='')
        musiclist_item['fav_count']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[3]/a[3]/i/text()').extract_first(default='').strip('()')
        musiclist_item['fav_count']='0' if musiclist_item['fav_count']=='收藏' else musiclist_item['fav_count']
        musiclist_item['share_count']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[3]/a[4]/i/text()').extract_first(default='').strip('()')
        musiclist_item['share_count']='0' if musiclist_item['share_count']=='分享' else musiclist_item['share_count']
        musiclist_item['comment_count']=response.xpath('//*[@id="cnt_comment_count"]/text()').extract_first(default='')
        musiclist_item['music_count']=response.xpath('//*[@id="playlist-track-count"]/text()').extract_first(default='')
        musiclist_item['time']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[2]/text()').extract_first(default='').rstrip(' 创建')
        musiclist_item['introduction']=response.xpath('//*[@id="album-desc-more"]/text()').extract_first(default='').strip()
        musiclist_item['introduction']='无' if musiclist_item['introduction']=='' else musiclist_item['introduction']
        musiclist_item['tags'] = ''
        tags=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[4]/a')
        for tag in tags:
            musiclist_item['tags']+=tag.xpath('./i/text()').extract_first(default='')
            musiclist_item['tags']+='、'
        musiclist_item['tags']='无'if musiclist_item['tags']==''else musiclist_item['tags']
        yield musiclist_item
        music_urls=response.xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[2]/div/div[1]/table/tbody/tr')
        for music_url in music_urls:
            url=self.base_url+music_url.xpath('./td[2]/div/div/div/span/a/@href').extract_first(default='')
            print(url)
            yield scrapy.Request(url,callback=self.parse_music,dont_filter=True,meta={'musiclistname':musiclist_item['name'],'musiclistauthor':musiclist_item['author']})

    def parse_music(self, response):
        music_item=items.MusicItem()
        music_item['musiclistname']=response.meta['musiclistname']
        music_item['musiclistauthor'] = response.meta['musiclistauthor']
        music_item['name']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/div[1]/div/em/text()').extract_first(default='')
        music_item['url']=response.url
        music_item['singer']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/p[1]/span/a/text()').extract_first(default='')
        music_item['album']=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/p[2]/a/text()').extract_first(default='')
        music_item['comment_count']=response.xpath('//*[@id="cnt_comment_count"]/text()').extract_first(default='')
        lyric=response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/p/text()').extract_first(default='')
        lyric_content=response.xpath('//*[@id="lyric-content"]/text()').extract()
        for i in lyric_content:
            lyric+=i
            lyric+='\n'
        lyric_more=response.xpath('//*[@id="flag_more"]/text()').extract()
        for j in lyric_more:
            lyric+=j
            lyric+='\n'
        music_item['lyric']=lyric
        yield music_item
