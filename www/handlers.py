#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date    : 2018-11-11 09:19:32
import json
import time
import logging
import asyncio
import re
import hashlib
import base64

from coroweb import get, post
from models import User, Blog, Comment, next_id
from config import configs
from apis import APIError, APIValueError, APIResourceNotFoundError, APIPermissionError
from aiohttp import web


COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def user2cookie(user, max_age):
    '''
    Generate cokkie str by user.
    '''
    # bulid cookie str by:id-expires-sha1
    expires = str(int(time.time() + max_age))  # 过期时间
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            return None
        user.passwd = '******'
        return user

    except Exception as e:
        logging.info('invalid sha1')
        return None


@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary,
             created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary,
             created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary,
             created_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')  # HTTP状态码302，重定向至指定路径
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signout.')
    return r

@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__':'manage_blog_edit.html',
        'id':'',
        'action':'/api/blogs'
    }


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        return APIValueError('passwd', 'Invalid password.')
    # authentication is successful,set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(
        user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


_RE_EMAIL = re.compile(
    r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name.strip():
        raise APIValueError('name', 'Invalid name.')
    if not _RE_EMAIL.match(email):
        raise APIValueError('email', 'Invalid email')
    if not _RE_SHA1.match(passwd):
        raise APIValueError('passwd', 'Invalid password')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:faild', 'email', 'Email is already in use')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(
        user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=True).encode('utf-8')
    return r


@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name.strip():
        raise APIValueError('name', 'name can not be empty.')
    if not summary.strip():
        raise APIValueError('summary', 'summary can not be empty.')
    if not content.strip():
        raise APIValueError('content', 'content can not be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request
                .__user__.image, name=name.strip(), summary=summary.strip(), content=content)
    await blog.save()
    return blog


# @get('/test')
# def test(request):
#     return web.HTTPFound('/signin')
