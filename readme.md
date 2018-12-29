# Introduction

This repository contains code for crawling data from varying sources based on [Scrapy](https://scrapy.org).

# Usage

The specific spider (for example `pedaily_pe.py` here) can be run as:
```bash
scrapy runspider main/spiders/pedaily_pe.py --loglevel INFO
```
, which runs `main/spiders/pedaily_pe.py` and output only log equal to or above `INFO` level. The 
result will go to `Downloads` of the home folder.

To create a new spider, it can be done as 
```bash
scrapy genspider pedaily_pe zdb.pedaily.cn
```
, which generates a new spider `pedaily_pe` under `main/spiders` for domain `zdb.pedaily.cn`.

# Dependencies

- Python 3.5+
- scrapy
- scrapy_selenium
- selenium chrome driver under your home directory

# Structure

## `base`

This folder contains `ButtonSpider`, which is subclassed from `scrapy.Spider`, to help you configure the proxy.

## `proxy`

This folder provides the code for handling the proxies.

### `pool.py`

It exposes `POOL` to let user retrieve a proxy and invalidate the proxy:
- `get`: gets a random proxy
- `remove`: invalidates a proxy
- `add`: adds a new proxy to it

It supports expiration time and expiration count for the proxy, where the expired proxy will be removed from the pool 
automatically.

## `main`

This is where the real spider implementation goes.

## `spiders`

This folder contains a list of spiders:
- `china_clinic`: for  [China clinic trial](https://www.chictr.org.cn)
- `gsxt`: **not completed yet** for [国家企业信用信息公示平台](https://www.gsxt.gov.cn)
- `pedaily_invest.py`: for [Pedaily investment](https://zdb.pedaily.cn/inv) 
- `pedaily_ma.py`: for [Pedaily merge and acquire](https://zdb.pedaily.cn/ma) 
- `pedaily_ipo.py`: for [Pedaily IPO](https://zdb.pedaily.cn/ipo) 
- `pedaily_pe.py`: for [Pedaily private equity](https://zdb.pedaily.cn/pe) 
