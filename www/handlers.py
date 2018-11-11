#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date    : 2018-11-11 09:19:32
import json
import logging
import asyncio
from coroweb import get, post
from models import User, Blog, Comment, next_id

@get('/')
async def index(request):
    users=await User.findAll()
    return {
        '__template__':'test.html',
        'users':users
    }#返回值会经过app的middlewares函数处理