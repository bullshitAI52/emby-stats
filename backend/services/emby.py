"""
Emby API 服务模块
处理与 Emby 服务器的所有交互
"""
import httpx
import aiosqlite
from typing import Optional, Dict
from config import settings


class EmbyService:
    """Emby 服务类，管理与 Emby 服务器的交互"""

    def __init__(self):
        self._api_key_cache: Dict[str, str] = {}  # server_id -> api_key
        self._user_id_cache: Dict[str, str] = {}  # server_id -> user_id
        self._item_info_cache: dict = {}

    async def get_api_key(self, server_config: Optional[dict] = None) -> str:
        """获取 Emby API Key"""
        # 如果提供了 server_config，使用它
        if server_config:
            # 优先使用配置中的 API Key
            if server_config.get('emby_api_key'):
                return server_config['emby_api_key']

            # 从缓存获取
            server_id = server_config.get('id', 'default')
            if server_id in self._api_key_cache:
                return self._api_key_cache[server_id]

            # 从数据库获取
            try:
                auth_db = server_config.get('auth_db', settings.AUTH_DB)
                async with aiosqlite.connect(auth_db) as db:
                    async with db.execute(
                        "SELECT AccessToken FROM Tokens_2 WHERE IsActive=1 ORDER BY DateLastActivityInt DESC LIMIT 1"
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            self._api_key_cache[server_id] = row[0]
                            return self._api_key_cache[server_id]
            except Exception as e:
                print(f"Error getting API key from {auth_db}: {e}")
        else:
            # 使用默认配置（向后兼容）
            if settings.EMBY_API_KEY:
                return settings.EMBY_API_KEY

            if 'default' in self._api_key_cache:
                return self._api_key_cache['default']

            try:
                async with aiosqlite.connect(settings.AUTH_DB) as db:
                    async with db.execute(
                        "SELECT AccessToken FROM Tokens_2 WHERE IsActive=1 ORDER BY DateLastActivityInt DESC LIMIT 1"
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            self._api_key_cache['default'] = row[0]
                            return self._api_key_cache['default']
            except Exception as e:
                print(f"Error getting API key: {e}")
        return ""

    async def get_user_id(self, server_config: Optional[dict] = None) -> str:
        """获取一个 Emby 用户 ID 用于 API 调用"""
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL
        server_id = server_config.get('id', 'default') if server_config else 'default'

        if server_id in self._user_id_cache:
            return self._user_id_cache[server_id]

        try:
            api_key = await self.get_api_key(server_config)
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Users",
                    params={"api_key": api_key},
                    timeout=10
                )
                if resp.status_code == 200:
                    users = resp.json()
                    if users:
                        self._user_id_cache[server_id] = users[0]["Id"]
                        return self._user_id_cache[server_id]
        except Exception as e:
            print(f"Error getting user ID: {e}")
        return ""

    async def get_item_info(self, item_id: str, server_config: Optional[dict] = None) -> dict:
        """获取媒体项目信息（包含海报等）"""
        cache_key = f"{server_config.get('id', 'default') if server_config else 'default'}:{item_id}"
        if cache_key in self._item_info_cache:
            return self._item_info_cache[cache_key]

        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            user_id = await self.get_user_id(server_config)
            if not api_key or not user_id:
                return {}

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Users/{user_id}/Items/{item_id}",
                    params={
                        "api_key": api_key,
                        "Fields": "SeriesInfo,ImageTags,SeriesPrimaryImageTag,PrimaryImageAspectRatio,Overview,BackdropImageTags"
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    info = resp.json()
                    self._item_info_cache[cache_key] = info
                    # 限制缓存大小
                    if len(self._item_info_cache) > settings.ITEM_CACHE_MAX_SIZE:
                        keys = list(self._item_info_cache.keys())[:settings.ITEM_CACHE_EVICT_COUNT]
                        for k in keys:
                            del self._item_info_cache[k]
                    return info
        except Exception as e:
            print(f"Error getting item info for {item_id}: {e}")
        return {}

    async def get_poster(self, item_id: str, max_height: int = 300, max_width: int = 200, server_config: Optional[dict] = None) -> tuple[bytes, str]:
        """获取海报图片，返回 (图片数据, content_type)"""
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            if not api_key:
                return b"", "image/jpeg"

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Items/{item_id}/Images/Primary",
                    params={
                        "api_key": api_key,
                        "maxHeight": max_height,
                        "maxWidth": max_width,
                        "quality": 90
                    },
                    timeout=15
                )
                if resp.status_code == 200:
                    return resp.content, resp.headers.get("content-type", "image/jpeg")
        except Exception as e:
            print(f"Error fetching poster for {item_id}: {e}")

        return b"", "image/jpeg"

    async def get_backdrop(self, item_id: str, max_height: int = 720, max_width: int = 1280, server_config: Optional[dict] = None) -> tuple[bytes, str]:
        """获取背景图(横版)，返回 (图片数据, content_type)"""
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            if not api_key:
                return b"", "image/jpeg"

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Items/{item_id}/Images/Backdrop",
                    params={
                        "api_key": api_key,
                        "maxHeight": max_height,
                        "maxWidth": max_width,
                        "quality": 90
                    },
                    timeout=15
                )
                if resp.status_code == 200:
                    return resp.content, resp.headers.get("content-type", "image/jpeg")
        except Exception as e:
            print(f"Error fetching backdrop for {item_id}: {e}")

        return b"", "image/jpeg"

    def get_poster_url(self, item_id: str, item_type: str, item_info: dict, server_id: str = None) -> str | None:
        """根据媒体信息获取海报 URL"""
        if not item_info:
            return None

        server_param = f"?server_id={server_id}" if server_id else ""
        # 对于剧集，使用剧集海报；对于电影，使用自身海报
        if item_type == "Episode" and item_info.get("SeriesId"):
            return f"/api/poster/{item_info['SeriesId']}{server_param}"
        elif item_info.get("ImageTags", {}).get("Primary"):
            return f"/api/poster/{item_id}{server_param}"

        return None

    def get_backdrop_url(self, item_id: str, item_type: str, item_info: dict, server_id: str = None) -> str | None:
        """根据媒体信息获取背景图(横版) URL"""
        if not item_info:
            return None

        server_param = f"?server_id={server_id}" if server_id else ""
        # 对于剧集，使用剧集背景图
        if item_type == "Episode" and item_info.get("SeriesId"):
            return f"/api/backdrop/{item_info['SeriesId']}{server_param}"
        # 检查是否有 Backdrop 图片
        elif item_info.get("BackdropImageTags") and len(item_info.get("BackdropImageTags", [])) > 0:
            return f"/api/backdrop/{item_id}{server_param}"

        return None

    async def get_now_playing(self, server_config: Optional[dict] = None) -> list[dict]:
        """获取当前正在播放的会话"""
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            if not api_key:
                return []

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Sessions",
                    params={"api_key": api_key},
                    timeout=10
                )
                if resp.status_code == 200:
                    sessions = resp.json()
                    playing = []
                    for session in sessions:
                        # 只返回正在播放的会话
                        if session.get("NowPlayingItem"):
                            playing.append(session)
                    return playing
        except Exception as e:
            print(f"Error getting now playing: {e}")
        return []

    async def authenticate_user(self, username: str, password: str) -> dict | None:
        """
        使用 Emby API 验证用户登录
        返回用户信息 dict 或 None（验证失败）
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.EMBY_URL}/emby/Users/AuthenticateByName",
                    headers={
                        "X-Emby-Authorization": 'MediaBrowser Client="Emby Stats", Device="Web", DeviceId="emby-stats", Version="1.0.0"',
                        "Content-Type": "application/json"
                    },
                    json={
                        "Username": username,
                        "Pw": password
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "user_id": data.get("User", {}).get("Id"),
                        "username": data.get("User", {}).get("Name"),
                        "access_token": data.get("AccessToken"),
                        "is_admin": data.get("User", {}).get("Policy", {}).get("IsAdministrator", False)
                    }
        except Exception as e:
            print(f"Error authenticating user: {e}")
        return None


# 单例实例
emby_service = EmbyService()
