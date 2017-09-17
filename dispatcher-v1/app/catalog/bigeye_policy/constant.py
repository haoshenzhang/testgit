# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
bigeye 策略
"""

class BigeyePolicy(object):
    """
    bigeye 策略名称
    """
    TRNT_MemUtil = u"TRNT_MemUtil"   # WINDOWS系统内存
    TRNT_disk = u"TRNT_disk"  # WINDOWS逻辑磁盘空间
    TRNT_CpuUtil = u"TRNT_CpuUtil"  # WINDOWS系统CPU使用率

    TRUNIX_MemUtil = u"TRUNIX_MemUtil"    # Linux系统内存
    TRUNIX_CpuUtil = u"TRUNIX_CpuUtil"   # Linux系统CPU
    TRUNIX_FileSystemSpace = u"TRUNIX_FileSystemSpace"  # Linux系统文件系统使用率
