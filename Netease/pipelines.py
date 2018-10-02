# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from . import items
import os,re
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

class SavePipeline(object):
    def process_item(self, item, spider):
        data=dict(item)
        if isinstance(item,items.MusicListItem):
            musiclistdir='G:\\歌单\\'+ re.sub('[\\\/:*?"<>|]', '-', data['name'])+'by.'+re.sub('[\\\/:*?"<>|]', '-', data['author'])
            if(not os.path.exists(musiclistdir)):
                os.mkdir(musiclistdir)
            with open(musiclistdir+'\歌单.txt','wt',encoding='utf-8') as f:
                txt='名称：' + data['name'] + '\n' \
                  + '歌单地址：' + data['url'] + '\n' \
                  + '封面地址：' + data['cover_url'] + '\n' \
                  + '作者：' + data['author'] + '\n' \
                  + '播放量：' + data['play_count'] + '\n' \
                  + '收藏量：' + data['fav_count'] + '\n' \
                  + '分享次数：' + data['share_count'] + '\n' \
                  + '评论数：' + data['comment_count'] + '\n' \
                  + '歌曲数：' + data['music_count']+'\n'\
                  + '日期：'+data['time']+'\n' \
                  + '标签：'+data['tags']+'\n'  \
                  + '介绍：'+data['introduction']
                print('歌单内容：',txt)
                f.write(txt)
            return item
        elif isinstance(item,items.MusicItem):
            musiclistdir = 'G:\\歌单\\' + re.sub('[\\\/:*?"<>|]', '-', data['musiclistname'])+'by.'+re.sub('[\\\/:*?"<>|]', '-', data['musiclistauthor'])
            if(not os.path.exists(musiclistdir)):
                raise DropItem
            with open(musiclistdir+'\\'+re.sub('[\\\/:*?"<>|]', '-', data['name'])+'.txt','wt',encoding='utf-8') as f:
                txt='歌曲名称：'+data['name']+'\n'\
                +'地址：'+data['url']+'\n'\
                +'歌手：'+data['singer']+'\n'\
                +'专辑：'+data['album']+'\n'\
                +'评论数：'+data['comment_count']+'\n'\
                +'歌词：'+data['lyric']
                f.write(txt)
            return item

class DownloadCoverPipeline(ImagesPipeline):
    headers={'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection':'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
            }
    def get_media_requests(self, item, info):
        if item.get('cover_url')!=None:
            print('下载封面,',item['cover_url'])
            yield Request(item['cover_url'],meta={'musiclistname':item['name'],'musiclistauthor':item['author']},headers=self.headers,dont_filter=True)
    def file_path(self, request, response=None, info=None):
        path='G:\\歌单\\' + re.sub('[\\\/:*?"<>|]', '-', request.meta['musiclistname'])+\
             'by.'+re.sub('[\\\/:*?"<>|]', '-', request.meta['musiclistauthor'])+'\封面.jpg'
        return path
