# -*- coding: utf-8 -*-
Version = "1.3.3"                                               # 版本信息 : str
ApiVersion = 4                                                  # API版本 : int
Author = "Zero123"                                              # 创作者: str
ContactInformation = "QQ:913702423"                             # 联系方式: str
Other = """
    # QuModLibs By Zero123(网易:游趣开发组) 别名:一灵 | h2v-wither123... BilBil-UID:456549011
    # 开源协议: BSD (适用于我们在Gitee/Github等渠道上公布的版本)

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
"""

"""
    v1.3 变动更新
    - 所有实体组件类以及EasyThread类被标记为[即将废弃], 移动到Deprecated模块
    + 新版实体组件类 QBaseEntityComp 更加安全高性能的实现
    + 新的线程模块(包括线程池和主线程通信方案)
    + UIManager现在基于帧事件驱动
    + 重构底层源代码实现 (QuMod, Server, Client, LoaderSystem等部分)
    + QuMod模块新增函数式功能
    - 移除QuDestroy关键词命名函数
    + 新增DestroyFunc装饰器修饰在游戏关闭时执行的函数
    + LensPlayer系统使用帧事件驱动 且不再需要开发者释放资源 当播放器不被使用时自动将会释放
    + @Listen 静态注册监听现在将会按照文件module区分隔离了
    + GLR现在支持非玩家实体的节点管理(需声明白名单/全局支持)
    + EventsPool事件池机制 优化高频率动态监听/反监听性能表现
    ! ATE扩展现在默认使用GLRender作为节点同步支持而不是CTRender(将在未来废弃)
    + ATE扩展对象均采用EventPool管理事件 并且不再需要手动释放
    + 新增Util.QTimeLine模块

    # 如果您想要在旧版项目中使用该版本并确保兼容 请使用
    from QuModLibs.Modules.Deprecated.Server import *
    from QuModLibs.Modules.Deprecated.Client import *
"""