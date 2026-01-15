# 时区显示修复说明

## 修复的问题

修复了 [Issue #3](https://github.com/qingcheng00624/emby-stats/issues/3) - 活跃时段分布和播放历史的时间显示不正确

尽管设置了 `TZ=Asia/Shanghai`,所有时间仍然显示为 UTC 时间,导致时间偏差 8 小时。

## 修复内容

### 1. 后端修复 - 活跃时段统计查询

**文件:** `backend/routers/stats/trend.py`

**修改:**
- 添加 `CAST` 确保小时和星期值正确转换为整数
- 添加 `ORDER BY` 确保结果排序一致

```python
# 修改前
SELECT
    strftime('%w', {datetime_col}) as day_of_week,
    strftime('%H', {datetime_col}) as hour,
    ...

# 修改后
SELECT
    CAST(strftime('%w', {datetime_col}) AS INTEGER) as day_of_week,
    CAST(strftime('%H', {datetime_col}) AS INTEGER) as hour,
    ...
ORDER BY day_of_week, hour
```

### 2. 前端修复 - 时间解析逻辑

**文件:** `frontend/src/lib/utils.ts`

**问题原因:**
- 后端返回的是本地时间字符串(如 `"2026-01-15 15:00:00"`)
- 前端的 `new Date()` 错误地将其解析为 UTC 时间
- 导致再次转换为本地时间时,时间偏移 8 小时

**修改:**
添加 `parseLocalDateTime()` 辅助函数,正确解析本地时间字符串:

```typescript
function parseLocalDateTime(dateStr: string): Date {
  // 将空格替换为 'T',使其符合 ISO 格式(无时区后缀)
  // 这样浏览器会将其解析为本地时间而非 UTC
  const isoLike = dateStr.replace(' ', 'T')
  return new Date(isoLike)
}
```

更新所有时间格式化函数使用新的解析方法:
- `formatDate()`
- `formatTime()`
- `formatDateTime()`

## 影响范围

✅ **修复后,以下功能的时间显示都已正确:**
- 活跃时段分布热力图
- 播放历史记录
- 所有其他时间显示

## 如何使用

### Docker 部署

1. 拉取更新后的代码
2. 重新构建并启动容器:

```bash
docker-compose down
docker-compose up -d --build
```

### 手动部署

1. 更新代码文件
2. 重启后端服务
3. 清除浏览器缓存(重要!)

## 验证方法

1. **检查播放历史:**
   - 打开播放历史页面
   - 确认显示的时间与实际播放时间一致(上海时间 UTC+8)

2. **检查活跃时段热力图:**
   - 打开概览页面
   - 确认热力图显示的高峰时段与实际观看习惯一致

3. **对比 Emby 服务器:**
   - 在 Emby 服务器中查看相同的播放记录
   - 确认两边显示的时间一致

## 技术细节

### 时区处理流程

**修复前:**
1. Emby 存储 UTC 时间: `2026-01-15 07:00:00`
2. 后端转换为本地时间: `2026-01-15 15:00:00` ✅
3. 前端解析为 UTC: `new Date("2026-01-15 15:00:00")` → 认为是 15:00 UTC ❌
4. 前端转换为本地时间: 15:00 UTC → 23:00 北京时间 ❌

**修复后:**
1. Emby 存储 UTC 时间: `2026-01-15 07:00:00`
2. 后端转换为本地时间: `2026-01-15 15:00:00` ✅
3. 前端正确解析为本地时间: `new Date("2026-01-15T15:00:00")` → 15:00 本地时间 ✅
4. 前端显示: 15:00 ✅

### 配置说明

确保 `docker-compose.yml` 或 `.env` 中的时区配置正确:

```yaml
environment:
  - TZ=Asia/Shanghai      # 系统时区
  - TZ_OFFSET=8           # SQLite 查询偏移(小时)
```

## 相关链接

- 原始 Issue: https://github.com/qingcheng00624/emby-stats/issues/3
- 修复后的仓库: https://github.com/bullshitAI52/emby-stats
- Commit: https://github.com/bullshitAI52/emby-stats/commit/d872cbc

## 贡献者

感谢 [@lostlv](https://github.com/lostlv) 报告此问题!

---

**更新日期:** 2026-01-15
