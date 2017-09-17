# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-07-9 12:29
    测试公用库中的helpers相关方法
"""
import datetime

from app.utils.helpers import (format_date, get_image_info, check_image)


def test_format_date():
    date = datetime.date(2015, 2, 15)
    time = datetime.datetime.combine(date, datetime.datetime.min.time())
    assert format_date(time) == "2015-02-15"


def test_get_image_info():
    # some random jpg/git/png images from my imgur account
    jpg = "http://i.imgur.com/NgVIeRG.jpg"
    gif = "http://i.imgur.com/l3Vmp4m.gif"
    png = "http://i.imgur.com/JXzKxNs.png"

    jpg_img = get_image_info(jpg)
    assert jpg_img["content-type"] == "image/jpeg"
    assert jpg_img["height"] == 1024
    assert jpg_img["width"] == 1280
    assert jpg_img["size"] == 209.06

    gif_img = get_image_info(gif)
    assert gif_img["content-type"] == "image/gif"
    assert gif_img["height"] == 168
    assert gif_img["width"] == 400
    assert gif_img["size"] == 576.138

    png_img = get_image_info(png)
    assert png_img["content-type"] == "image/png"
    assert png_img["height"] == 1080
    assert png_img["width"] == 1920
    assert png_img["size"] == 269.409


def test_check_image():
    # 测试200x100.png
    img_width = "http://i.imgur.com/4dAWAZI.png"
    # 测试100x200.png
    img_height = "http://i.imgur.com/I7GwF3D.png"
    # 测试100x100.png
    img_ok = "http://i.imgur.com/CYV6NzT.png"
    # 随机最大图片
    img_size = "http://i.imgur.com/l3Vmp4m.gif"
    # 错误图片方式
    img_type = "https://d11xdyzr0div58.cloudfront.net/static/logos/archlinux-logo-black-scalable.f931920e6cdb.svg"

    data = check_image(img_width)
    assert u"宽度" in data[0]
    assert not data[1]

    data = check_image(img_height)
    assert u"高度" in data[0]
    assert not data[1]

    data = check_image(img_type)
    assert u"类型" in data[0]
    assert not data[1]

    data = check_image(img_ok)
    assert data[0] is None
    assert data[1]

    data = check_image(img_size, 1000, 1000)
    assert u"大小" in data[0]
    assert not data[1]
