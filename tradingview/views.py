from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging
import decimal
import datetime
import calendar

from btc.models import MarketPrice
from django.utils import timezone
from btc.logic.api import common_func
import pytz
from btc import consts


# Create your views here.
class DecimalJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return DjangoJSONEncoder


def index(request):
    return render(request, "tradingview/index.html")


def config(request):
    results = {}
    results["supports_search"] = True
    results["supports_group_request"] = False
    results["supported_resolutions"] = [
        "1", "5", "15", "30", "60", "240", "1D"
    ]
    results["supports_marks"] = False
    results["supports_time"] = True
    data = json.dumps(results, cls=DecimalJSONEncoder)
    return HttpResponse(data, content_type="application/json")


def symbols(request):
    symbol = request.GET.get("symbol")
    base, quote = symbol.split('_')

    # ws.send('{"id":1, "method":"call", "params":[0,"lookup_asset_symbols",[["' + base + '"], 0]]}')
    # result = ws.recv()
    # j = json.loads(result)
    # base_precision = 10**j["result"][0]["precision"]
    precision = 5
    base_precision = 10**precision

    results = {}

    results["name"] = symbol
    results["ticker"] = symbol
    results["description"] = base + "/" + quote
    results["type"] = ""
    results["session"] = "24x7"
    results["exchange"] = ""
    results["listed_exchange"] = ""
    results["timezone"] = "Asia/Shanghai"
    results["minmov"] = 1
    results["pricescale"] = base_precision
    results["minmove2"] = 0
    results["fractional"] = False
    results["has_intraday"] = True
    results["supported_resolutions"] = [
        "1", "5", "15", "30", "60", "240", "1D"
    ]
    results["intraday_multipliers"] = ""
    results["has_seconds"] = False
    results["seconds_multipliers"] = ""
    results["has_daily"] = True
    results["has_weekly_and_monthly"] = False
    results["has_empty_bars"] = True
    results["force_session_rebuild"] = ""
    results["has_no_volume"] = False
    results["volume_precision"] = ""
    results["data_status"] = ""
    results["expired"] = ""
    results["expiration_date"] = ""
    results["sector"] = ""
    results["industry"] = ""
    results["currency_code"] = ""

    data = json.dumps(results, cls=DecimalJSONEncoder)
    return HttpResponse(data, content_type="application/json")


'''
s: 状态码。 预期值:ok|error|no_data
errmsg: 错误消息。只在s = 'error'时出现
t: K线时间. unix时间戳 (UTC)
c: 收盘价
o: 开盘价 (可选)
h: 最高价 (可选)
l: 最低价(可选)
v: 成交量 (可选)
nextTime: 下一个K线柱的时间 如果在请求期间无数据 (状态码为no_data) (可选)
'''


def search(request):
    query = request.args.get('query')
    type = request.args.get('type')
    exchange = request.args.get('exchange')
    limit = request.args.get('limit')

    final = []
    '''
    #con = psycopg2.connect(database=postgres_database, user=postgres_username, host=postgres_host,password=postgres_password)
    #cur = con.cursor()
    #query = "SELECT * FROM markets WHERE pair LIKE '%" + query + "%'"
    #print(query)

    #cur.execute(query)
    #result = cur.fetchall()
    #con.close()

    result=[["BTS_BLOCKPAY","BTS/BLOCKPAY"],["OPEN.BTC_BLOCKPAY","OPEN.BTC/BLOCKPAY"],["BTS_USD","BTS/USD"]]
    for w in range(0, len(result)):

        results = {}
        #print w
        base, quote = result[w][1].split('/')

        results["symbol"] = base + "_" + quote

        results["full_name"] = result[w][1]
        results["description"] = result[w][1]
        results["exchange"] = ""
        results["ticker"] = base + "_" + quote
        results["type"] = ""
        if query in result[w][0]:
            final.append(results)
    '''
    data = json.dumps(final, cls=DecimalJSONEncoder)
    return HttpResponse(data, content_type="application/json")


'''
https://b.aistock.ga/books/tradingview/book/How-To-Connect-My-Data.html

s: 状态码。 预期值:ok|error|no_data
errmsg: 错误消息。只在s = 'error'时出现
t: K线时间. unix时间戳 (UTC)
c: 收盘价
o: 开盘价 (可选)
h: 最高价 (可选)
l: 最低价(可选)
v: 成交量 (可选)
nextTime: 下一个K线柱的时间 如果在请求期间无数据 (状态码为no_data) (可选)
打不开
可能vpn的问题
我就想看看效果
不行就自己写
小林 前端  13:06:13
Datafeeds.UDFCompatibleDatafeed = function(datafeedURL, updateFrequency, protocolVersion)
updateFrequency（更新频率）

这是一个有间隔的实时数据请求，datafeed将以毫秒为单位发送到服务器。 默认值为10000（10秒）
index.html

'''


def history(request):
    symbol = request.GET.get('symbol')
    from_ = request.GET.get('from')
    to = request.GET.get('to')
    resolution = request.GET.get('resolution')
    # todo 暂时加8小时搜索
    inv_time = 8*3600
    from_ = int(from_) + inv_time
    to = int(to) + inv_time
    #print(" from - to %r, from_ %r, to %r" % (from_ - to, from_, to))
    time_type = 'min'
    left = datetime.datetime.fromtimestamp(from_).strftime('%Y-%m-%dT%H:%M:%S')
    right = datetime.datetime.fromtimestamp(to).strftime('%Y-%m-%dT%H:%M:%S')
    # 时间区间

    results = {}
    coin_type, use_coin_type = symbol.split('_')
    rows = MarketPrice.objects.filter(
        coin_type=coin_type,
        use_coin_type=use_coin_type,
        time_type=time_type,
        date_time__gt=left,
        date_time__lte=right)

    t = []
    c = []
    o = []
    h = []
    l = []
    v = []
    count = rows.count()
    if count > 2000:
        count = 2000
    rows = rows[0:count]

    for row in rows:
        date_time = row.date_time
        ts = date_time.timestamp() + inv_time   # 日后
        c.append(row.close)
        o.append(row.open)
        h.append(row.high)
        l.append(row.low)
        v.append(row.volume)
        t.append(ts)
    if len(t) == 0:
        results["s"] = "no_data"
        results["t"] = []
        results["c"] = []
        results["o"] = []
        results["h"] = []
        results["l"] = []
        results["v"] = []
    else:
        results["s"] = "ok"
        results["t"] = t
        results["c"] = c
        results["o"] = o
        results["h"] = h
        results["l"] = l
        results["v"] = v
    # todo errror处理
    # if s = error ; results["errmsg"] = "Some eror msg here"
    data = json.dumps(results, cls=DecimalJSONEncoder)
    return HttpResponse(data, content_type="application/json")


def time(request):
    # ws.send('{"id":1, "method":"call", "params":[0,"get_dynamic_global_properties",[]]}')
    # result = ws.recv()
    # j = json.loads(result)
    # date = datetime.datetime.strptime(j["result"]["time"], "%Y-%m-%dT%H:%M:%S")
    # return jsonify(str(calendar.timegm(date.utctimetuple())))
    # str="1517201928"
    # date = datetime.datetime.strptime(j["result"]["time"], "%Y-%m-%dT%H:%M:%S")
    # str1 = str(calendar.timegm(date.utctimetuple()))
    import time
    str1 = str(round(time.time()))
    #print("str1 %r %r " % (1517459128, str1))
    return HttpResponse(str1, content_type="application/json")
