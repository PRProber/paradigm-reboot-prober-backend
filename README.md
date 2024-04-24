# 范式：起源 查分器

**中文** | [English](https://github.com/PRProber/paradigm-reboot-prober-backend/blob/master/docs/README_en.md)

[前端](https://github.com/PRProber/paradigm-reboot-prober-frontend)

## 声明

本查分器仅为《范式：起源》 Rating 计算提供参考，不保证数据与计算 100% 正确，请以游戏内显示为准。 本软件与击弦网络及相关游戏发行、开发及分发公司无任何关系，均使用互联网公开资源，仅供学习研究用途，相关版权归相关方所有。

**本查分器不包含任何直接访问官方服务器用户数据的功能，请勿使用本代码用于网络攻击或其他滥用行为。**

## 用户指南

前端目前已经部署，可以[直接访问](https://prp.icel.site)注册使用。

### 手动导入 / 导出

#### 下载 Best 50 图

### 其他导入方式

请等待第三方开发者进行开发。

## 开发者指南

### API Docs

请访问 [FastAPI SwaggerUI](https://api.prp.icel.site/docs) 进行 API 的文档的查阅。

### 本地部署

请参考 [部署指南](https://github.com/PRProber/paradigm-reboot-prober-backend/blob/master/docs/deployment.md)。

### 项目结构

源代码均在 `backend` 软件包下。

```
│  config.py        <-- API 相关配置
│  main.py          <-- Uvicorn 入口
│
├─crud              <-- DAO 层实现
│  │  record.py     
│  │  song.py
│  │  user.py
│
├─model             <-- 实体/schema 定义
│  │  database.py
│  │  entities.py
│  │  schemas.py
│
├─router            <-- Controller 层实现
│  │  record.py
│  │  song.py
│  │  upload.py
│  │  user.py
│ 
├─service           <-- Service 层实现
│  │  record.py
│  │  song.py
│  │  user.py
│
├─util
   │  cache.py      <-- 序列化 Response 的 encoder / decoder
   │  database.py   
   │  ocr.py       
   │  rating.py     <-- 提供 rating 的计算
   │  security.py   <-- 提供 authorization / authentication 的工具类
   │
   ├─b50
      │  csv.py     <-- 提供 csv -> schemas.PlayRecordCreate 的转换
      │  img.py     <-- 提供 best 50 图像的生成
```

## 数据来源及计算方式参考

1. [@临履](https://space.bilibili.com/405967183), 范式：起源查分表（持续更新）及Rating计算上的细节讨论 [cv29479925](https://www.bilibili.com/read/cv29479925/)
2. [@Errno](https://space.bilibili.com/272105666), 关于范式：起源Rating计算方法，已知和未知的各种信息与推测 [cv28420633](https://www.bilibili.com/read/cv28420633/)
3. [@クロネコ](https://space.bilibili.com/390198606), 范式：起源 (Paradigm: Reboot) 定数表
4. [Paradigm: Reboot Wiki*](https://wikiwiki.jp/paradigm_/), 歌曲详情及曲绘
5. [Fandom Paradigm: Reboot Wiki](https://paradigmreboot.fandom.com/wiki/Paradigm:_Reboot_Wiki), 歌曲详情及 Logo 等资源
