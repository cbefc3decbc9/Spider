# -*- coding: utf-8 -*-
import scrapy
from zhihu.items import ZhihuItem
import json


class ZhyhmSpider(scrapy.Spider):
    name = 'zhyhm'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    start_user = 'excited-vczh'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,included_answers_count,included_articles_count,included_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,is_org_createpin_white_user,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    following_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    following_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    follower_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    follower_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield scrapy.Request(self.user_url.format(user=self.start_user,include=self.user_query),
                             callback=self.parse_user)
        yield scrapy.Request(self.following_url.format(user=self.start_user,include=self.following_query,offset=0,limit=20),
                             callback=self.parse_following)
        yield scrapy.Request(self.follower_url.format(user=self.start_user,include=self.follower_query,offset=0,limit=20),
                             callback=self.parse_followers)

    def parse_user(self, response):
        item = ZhihuItem()
        result = json.loads(response.text)
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield scrapy.Request(
            self.following_url.format(user=result.get('url_token'), include=self.following_query, offset=0, limit=20),
            callback=self.parse_following)
        yield scrapy.Request(
            self.follower_url.format(user=result.get('url_token'), include=self.follower_query, offset=0, limit=20),
            callback=self.parse_followers)

    def parse_following(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),
                                     callback=self.parse_user)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == 'false':
            next_page = results.get('paging').get('next')
            yield scrapy.Request(next_page, callback=self.parse_following)


    def parse_followers(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                                     callback=self.parse_user)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == 'false':
            next_page = results.get('paging').get('next')
            yield scrapy.Request(next_page, callback=self.parse_followers)
