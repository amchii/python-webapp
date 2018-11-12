#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date    : 2018-11-11 09:19:32
import json
import time
import logging
import asyncio
from coroweb import get, post
from models import User, Blog, Comment, next_id

# @get('/')
# async def index(request):
#     users=await User.findAll()
#     return {
#         '__template__':'test.html',
#         'users':users
#     }#返回值会经过app的middlewares函数处理


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
