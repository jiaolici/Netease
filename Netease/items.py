# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class MusicListItem(Item):
    name=Field()
    url=Field()
    cover_url=Field()
    author=Field()
    play_count=Field()
    fav_count=Field()
    share_count=Field()
    comment_count=Field()
    music_count=Field()
    time=Field()
    introduction=Field()
    tags=Field()

class MusicItem(Item):
    musiclistname=Field()
    musiclistauthor=Field()
    name=Field()
    url=Field()
    singer=Field()
    album=Field()
    comment_count=Field()
    lyric=Field()
