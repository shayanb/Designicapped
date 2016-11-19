#!/usr/bin/env python
# -*- coding: utf8 -*-
import re
import urllib
import urllib2
import cookielib
import cStringIO
import gzip
import sys
import pdb
import json
import time


class PinterestPinata(object):

    def __init__(self, email=None, password=None, username=None, proxies=None):
        if not email or not password or not username:
            raise PinterestPinataException('Illegal arguments email={email}, password={password}, username={username}'.format(
                email=email, password=password, username=username))

        self.email = email
        self.password = password
        self.username = username
        self.logged_in = False
        self.csrf_token = None
        self.cookie_jar = cookielib.CookieJar()
        self.cookie_handler = urllib2.HTTPCookieProcessor(self.cookie_jar)
        urllib2.HTTPRedirectHandler.max_redirections = 2

        if proxies:
            self.proxy = urllib2.ProxyHandler({
                'http': proxies['http'],
                'https': proxies['https']
            })
        else:
            self.proxy = None

    def login_if_needed(self):
        if self.logged_in:
            return

        login_url = 'https://pinterest.com/login/'
        self._request(login_url)

        data = urllib.urlencode({
            'source_url': '/login/',
            'data': json.dumps({'options': {'username_or_email': self.email,
                                            'password': self.password}})
        })

        res, headers, cookies = self._request('http://www.pinterest.com/resource/UserSessionResource/create/',
                                              data=data, referrer=login_url, ajax=True)

        if self.email in res:
            self.logged_in = True

    def boards(self, username):
        """
        :param username:
        :return: [{u'id': u'xxxx'}]
        """
        if not username:
            raise PinterestPinataException('Illegal arguments username={username}'.format(username=username))

        res = self._request('http://www.pinterest.com/' + username + '/', ajax=True)

        boards = [re.findall("\d+", board)[0] for board in re.findall(r'"board_id":\s"\d*"', res[0])]
        unique = list(set(boards))
        boards = [{'id': board} for board in unique]

        return boards

    def create_board(self, name, category, description, privacy='public', layout='default'):
        if not name or not category or not description:
            raise PinterestPinataException('Illegal arguments name={name}, category={category}, '
                                           'description={description}, privacy={privacy}, layout={layout}'.format(
                name=name, category=category, description=description, privacy=privacy, layout=layout))

        self.login_if_needed()

        url = 'http://www.pinterest.com/' + self.username + '/'

        data = urllib.urlencode({
            'source_url': url,
            'data': json.dumps({'options': {'name': name,
                                            'category': category,
                                            'description': description,
                                            'privacy': privacy,
                                            'layout': layout}})
        })

        res, header, query = self._request('http://www.pinterest.com/resource/BoardResource/create/',
                                           data, referrer=url, ajax=True)

        if 'BoardResource' in res:
            json_res = json.loads(res)
            return {'id': json_res['resource_response']['data']['id'],
                    'url': json_res['resource_response']['data']['url']}

        return False

    def follow_board(self, board_id, board_url):
        if not board_id or not board_url:
            raise PinterestPinataException('Illegal arguments board_id={board_id}, board_url={board_url}'.format(
                board_id=board_id, board_url=board_url))

        self.login_if_needed()

        data = urllib.urlencode({
            'source_url': board_url,
            'data': json.dumps({'options': {'board_id': board_id}})
        })

        res, header, query = self._request('http://www.pinterest.com/resource/BoardFollowResource/create/',
                                           data, referrer=board_url, ajax=True)

        if 'BoardFollowResource' in res:
            return True

        return False

    def follow_user(self, user_id):
        if not user_id:
            raise PinterestPinataException('Illegal arguments user_id={user_id}'.format(user_id=user_id))

        self.login_if_needed()

        url = 'http://www.pinterest.com/' + self.username + '/'

        data = urllib.urlencode({
            'source_url': url,
            'data': json.dumps({'options': {'user_id': user_id}})
        })

        res, header, query = self._request('http://www.pinterest.com/resource/UserFollowResource/create/',
                                           data, referrer=url, ajax=True)

        if 'UserFollowResource' in res:
            return True

        return False

    def like(self, pin_id=None):
        """
        :param pin_id:
        :return: bool
        """
        if not pin_id:
            raise PinterestPinataException('Illegal arguments pin_id={pin_id}'.format(pin_id=pin_id))

        self.login_if_needed()

        url = 'http://www.pinterest.com/pin/' + pin_id

        data = urllib.urlencode({
            'source_url': url,
            'data': json.dumps({'options': {'pin_id': pin_id}})
        })

        res, header, query = self._request('http://www.pinterest.com/resource/PinLikeResource2/create/',
                                           data, referrer=url, ajax=True)

        if 'PinLikeResource2' in res:
            return True

        return False

    def comment(self, pin_id=None, comment=None):
        if not pin_id or not comment:
            raise PinterestPinataException('Illegal arguments pin_id={pin_id}, comment={comment}'.format(pin_id=pin_id,
                                                                                                         comment=comment))

        self.login_if_needed()

        url = 'http://www.pinterest.com/pin/' + pin_id

        data = urllib.urlencode({
            'source_url': url,
            'data': json.dumps({'options': {'pin_id': pin_id,
                                            'text': comment}}),
            'module_path': 'App()>Closeup(resource=PinResource(fetch_visual_search_objects=true, id={pin_id}))>'
                           'CloseupContent(resource=PinResource(id={pin_id}))>'
                           'Pin(resource=PinResource(id={pin_id}))>'
                           'PinCommentList(count=0, view_type=detailed, pin_id={pin_id}, '
                           'resource=PinCommentListResource(pin_id={pin_id}))'.format(pin_id=pin_id)
        })

        res, header, query = self._request('http://www.pinterest.com/resource/PinCommentResource/create/',
                                           data, referrer=url, ajax=True)

        if 'PinCommentResource' in res:
            return True

        return False

    def pin(self, board_id=None, description=None, image_url=None, link=None):
        """
        :param query:
        :return: 983242
        """
        if not board_id or not description or not image_url or not link:
            raise PinterestPinataException('Illegal arguments board_id={board_id}, description={description}, image_url={image_url}, '
                                           'link={description}'.format(board_id=board_id, description=description,
                                                                       image_url=image_url, link=link))

        self.login_if_needed()

        url = 'http://pinterest.com/pin/create/bookmarklet/'

        data = urllib.urlencode({
            'source_url': url,
            'data': json.dumps({'options': {'board_id': board_id,
                                            'description': description,
                                            'link': link,
                                            'image_url': image_url}})
        })

        res, header, query = self._request('http://www.pinterest.com/resource/PinResource/create/',
                                           data, referrer=url, ajax=True)

        if 'PinResource' in res:
            json_res = json.loads(res)
            return json_res['resource_response']['data']['id']

        return -1

    def repin(self, board_id=None, pin_id=None, link=None, description=None):
        """
        :param query:
        :return: 983242
        """
        if not board_id or not pin_id:
            raise PinterestPinataException('Illegal arguments board_id={board_id}, pin_id={pin_id}, link={link}, '
                                           'description={description}'.format(board_id=board_id, pin_id=pin_id,
                                                                              link=link, description=description))

        self.login_if_needed()

        url = 'http://pinterest.com/pin/' + pin_id

        data = urllib.urlencode({
            'source_url': url,
            'data': json.dumps({'options': {'board_id': board_id,
                                            'pin_id': pin_id,
                                            'link': link,
                                            'description': description,
                                            }
            })
        })

        res, header, query = self._request('http://www.pinterest.com/resource/RepinResource/create/',
                                           data=data, referrer=url, ajax=True)

        if 'RepinResource' in res:
            json_res = json.loads(res)
            return json_res['resource_response']['data']['id']

        return -1

    def search_boards(self, query):
        """
        :param query:
        :return: [{u'layout': u'xxxx', u'name': u'xxxx', u'privacy': u'xxxx', u'url': u'xxxx', u'owner': {u'id': u'xxxx'}, u'type': u'xxxx', u'id': u'xxxx', u'image_thumbnail_url': u'http://xxxx.jpg'}]
        """
        if not query:
            raise PinterestPinataException('Illegal arguments query={query}'.format(query=query))
        query = urllib.quote(query)

        res, headers, cookies = self._request(url=u'http://www.pinterest.com/search/boards/?q=' + query,
                                              referrer=u'https://www.pinterest.com/search/boards/?q=' + query,
                                              ajax=True)

        data = json.loads(res)
        res = []
        for child in data['module']['tree']['children']:
            for i in child['children']:
                for ji in i['children']:
                    for ki in ji['children']:
                        if 'children' in ki and len(ki['children']) > 0:
                            res.append({'id': ki['resource']['options']['board_id']})

        return res

    def search_pins(self, query):
        """
        :param query:
        :return: [{u'id': u'xxxxxxx', u'img': u'xxxxxxx', u'link': u'xxxxxxx', u'desc': u'xxxxxxx'}]
        """
        if not query:
            raise PinterestPinataException('Illegal arguments query={query}'.format(query=query))
        query = urllib.quote(query)

        res, headers, cookies = self._request(url=u'http://www.pinterest.com/search/pins/?q=' + query + '&rs=rs&%7Crecentsearch%7C0',
                                              referrer=u'https://www.pinterest.com/search/pins/?q=' + query,
                                              ajax=True)

        data = json.loads(res)
        children = data['module']['tree']['children']
        res = []
        #print children
        for child in children:
            try:
                for i in child['children']:
                    for ji in i['children']:
                        for index, ki, in enumerate(ji['children'], start=0):
                            if 'children' in ki and len(ki['children']) > 0:
                                #print ki
                                res.append({
                                    'id': ki['children'][1]['options']['pin_id'],
                                    'img': ji['children'][index]['data']['images']['orig']['url'],
                                    'link': ji['children'][index]['data']['link'],
                                    'grid_description': ji['children'][index]['data']['grid_description'],
                                    'title': ji['children'][index]['data']['title'],
                                    'desc': ji['children'][index]['data']['description'],
                                    'like_count': ji['children'][index]['data']['like_count'],
                                    'comment_count': ji['children'][index]['data']['comment_count'],
                                    'repin_count': ji['children'][index]['data']['repin_count'],
                                    'dominant_color': ji['children'][index]['data']['dominant_color'],
                                    'pinner': ji['children'][index]['data']['pinner']['username'],
                                })
            except Exception,e:
                #print "failed : %s" %e
                pass

        return res

    def search_users(self, query):
        """
        :param query:
        :return: [{u'username': u'xxxxxxx', u'image_small_url': u'xxxxxxx', u'type': u'xxxxxxx', u'id': u'xxxxxxx', u'full_name': u'xxxxxxx'}]
        """
        if not query:
            raise PinterestPinataException('Illegal arguments query={query}'.format(query=query))
        query = urllib.quote(query)

        res, headers, cookies = self._request(url=u'http://www.pinterest.com/search/users/?q=' + query,
                                              referrer=u'https://www.pinterest.com/search/users/?q=' + query,
                                              ajax=True)

        data = json.loads(res)

        children = data['module']['tree']['children']
        res = []
        for child in children:
            for i in child['children']:
                for ji in i['children']:
                    for index, ki, in enumerate(ji['children'], start=0):
                        if 'children' in ki and len(ki['children']) > 0:
                            res.append(ji['children'][index]['data'])

        return res

    def _add_headers(self, opener, referrer='http://google.com/', ajax=False):
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.1 \
                      (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'),
            ('Accept', 'image/png,image/*;q=0.8,*/*;q=0.5'),
            ('Accept-Language', 'en-us,en;q=0.5'),
            ('Accept-Encoding', 'gzip,deflate'),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
            ('Keep-Alive', '3600'),
            ('Host', 'www.pinterest.com'),
            ('Origin', 'http://www.pinterest.com'),
            ('Connection', 'keep-alive'),
            ('X-NEW-APP', 1)
        ]
        opener.addheaders.append(('Referer', referrer))
        if ajax:
            opener.addheaders.append(('X-Requested-With', 'XMLHttpRequest'))
        if self.csrf_token:
            opener.addheaders.append(('X-CSRFToken', self.csrf_token))

    def _request(self, url, data=None, referrer='http://google.com/', ajax=False):
        handlers = [self.cookie_handler]
        if self.proxy:
            handlers.append(self.proxy)
        opener = urllib2.build_opener(*handlers)
        self._add_headers(opener, referrer, ajax)

        html = ''
        try:
            req = urllib2.Request(url, data)
            res = opener.open(req, timeout=30)
            html = res.read()
        except Exception as e:
            sys.exc_clear()
            print "Something went terribly wrong {e}".format(e=e)
            return False, {}, {}

        headers = res.info()
        if ('Content-Encoding' in headers.keys() and headers['Content-Encoding'] == 'gzip') or \
                ('content-encoding' in headers.keys() and headers['content-encoding'] == 'gzip'):
            data = cStringIO.StringIO(html)
            gzipper = gzip.GzipFile(fileobj=data)
            try:
                html_unzipped = gzipper.read()
            except Exception:
                sys.exc_clear()
            else:
                html = html_unzipped

        cookies = {cookie.name: cookie.value for cookie in self.cookie_jar}
        self.csrf_token = cookies['csrftoken']

        return html, headers, cookies


class PinterestPinataException(Exception):
    pass


if __name__ == "__main__":
    import traceback
    try:
        pinata = PinterestPinata(email=sys.argv[1], password=sys.argv[2], username=sys.argv[3])
        print pinata.boards(sys.argv[3])
        # print pinata.create_board(name='my test board', category='food_drink', description='description later')
        # print pinata.search_boards('cats')
        #print pinata.search_pins('soccer7')
        #print pinata.search_pins('hair10')
    except PinterestPinataException:
        print traceback.format_exc()
