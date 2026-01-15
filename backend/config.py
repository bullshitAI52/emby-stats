"""
配置管理模块
集中管理所有环境变量和配置项
"""
import os


class Settings:
    """应用配置"""

    # 数据库路径
    PLAYBACK_DB: str = os.getenv("PLAYBACK_DB", "/data/playback_reporting.db")
    USERS_DB: str = os.getenv("USERS_DB", "/data/users.db")
    AUTH_DB: str = os.getenv("AUTH_DB", "/data/authentication.db")

    # Emby 服务器配置
    EMBY_URL: str = os.getenv("EMBY_URL", "http://localhost:8096")
    EMBY_API_KEY: str = os.getenv("EMBY_API_KEY", "")

    # 播放过滤配置
    # 最小播放时长过滤（秒），低于此时长的记录将被忽略，0 表示不过滤
    MIN_PLAY_DURATION: int = int(os.getenv("MIN_PLAY_DURATION", "0"))

    # 时区偏移（小时），用于 SQLite 查询时间转换，上海时区为 +8
    # 时区偏移（小时），用于 SQLite 查询时间转换
    # 优先使用环境变量 TZ_OFFSET
    # 如果未设置，则尝试从系统时区自动计算
    # 如果都失败，默认 +8 (北京时间)
    _system_offset = 8
    try:
        import datetime
        # 获取当前系统时区的偏移小时数
        _system_offset = int(datetime.datetime.now().astimezone().utcoffset().total_seconds() / 3600)
    except Exception:
        pass
    
    TZ_OFFSET: int = int(os.getenv("TZ_OFFSET", str(_system_offset)))

    # 缓存配置
    ITEM_CACHE_MAX_SIZE: int = 500
    ITEM_CACHE_EVICT_COUNT: int = 100


settings = Settings()
