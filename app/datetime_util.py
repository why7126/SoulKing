"""应用层时间：统一使用中国（北京）时区的本地墙上时钟，写入数据库为 naive datetime。"""

from datetime import datetime
from zoneinfo import ZoneInfo

CN_TZ = ZoneInfo("Asia/Shanghai")


def now_cn_naive() -> datetime:
    """当前北京时间，去掉 tzinfo，便于与现有 DateTime 列兼容。"""
    return datetime.now(CN_TZ).replace(tzinfo=None)
