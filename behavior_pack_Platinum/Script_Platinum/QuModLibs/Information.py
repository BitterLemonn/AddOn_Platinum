# -*- coding: utf-8 -*-
Version = "1.1.0-NX (NEW)"                                      # 版本信息 : str
ApiVersion = 2                                                  # API版本 : int
Author = "Zero123"                                              # 创作者: str
ContactInformation = "QQ:913702423"                             # 联系方式: str
Other = """
    # QuModLibs By Zero123(网易:游趣开发组) 别名:一灵 | h2v-wither123... BilBil-UID:456549011
    # 开源协议: BSD
    # 附加条例: 使用QuModLibs开发的项目如需商用, 应在发布页标明使用的相关框架及涉及到的[三方扩展](如有需要)

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
"""


"""
新版NX11核心改动 (旧版项目更新参考)
    - @Listen 监听现在是基于函数名称唯一存储记录的了 当建立多个相同事件监听时请加上前缀区分
    - ListenForEvent 现在会包装成一个lambda对象再进行执行调度 因此新的报错提示有所区别
    - Call / Request 通信逻辑现在基于新的加载器系统建立 System仍然保留为原版系统实例
    - 所有的事件监听逻辑均需提交到加载器队列进行统一注册 这可能影响动态监听实时性触发问题 对于初始注册的监听将会立即更新
    - 可以通过 _loaderSystem.unsafeUpdate(ListenForEvent(...)) 立即刷新队列数据 详细请阅读[安全问题]
    - Events 现在是一个虚假封装对象 用于避免加载Events文件产生的IO开销同时保留VSC补全信息段和功能作用

安全问题
    网易MC移动端不知道出于什么原因存在一种安全机制(反作弊?) 外界调用self.ListenForEvent将会主动断开游戏连接导致游戏卡死读条现象
    为避免这一系问题对QuMod项目产生的影响在NX11中引入了一个加载器系统包括执行队列的维护 由系统本身发起调用解决安全系统导致的卡死
    通常来说安全系统只在读条期间校验? 在游戏加载完毕后您可以使用unsafeUpdate强制立即刷新或者等待队列1tick后刷新
    对于初始化注册的监听则会立即刷新

功能裁剪
    - ATE战斗扩展因商务原因暂时没有引入浏览版中 (ATE最初为其他开发者外包定做的战斗扩展模块)
"""