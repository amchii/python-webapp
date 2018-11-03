#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date    : 2018-11-03 10:55:50
import sys
import orm
import asyncio
from models import User, Blog, Comment


async def save(loop, **kw):
    await orm.create_pool(loop, user='root', password='12345678', db='web_app')
    u = User(name=kw.get('name'), email=kw.get('email'),
             passwd=kw.get('passwd'), image=kw.get('image'))
    # u = User(name='Test', email='test4', passwd='123456', image='about-blank')
    # 可以在实例的时候用一个变量保存u.id(primary key)供删除时使用
    await u.save()
    await orm.close_pool()


async def find(loop):
    await orm.create_pool(loop, user='root', password='12345678', db='web_app')
    rs = await User.findAll()
    print('查找测试： %s' % rs)
    await orm.close_pool()

if __name__ == '__main__':
    data=dict(name='Test', email='test5', passwd='123456', image='about-blank')
    loop = asyncio.get_event_loop()
    tasks = [save(loop,**data), find(loop)]
    loop.run_until_complete(asyncio.wait(tasks))
    print('Test finished.')
    loop.close()
    # if loop.is_closed():
    #   sys.exit(0)
