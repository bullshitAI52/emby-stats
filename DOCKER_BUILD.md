# 构建和发布 Docker 镜像指南

## 方案一: 使用 GitHub Actions 自动构建 (推荐)

这是最简单的方法,不需要在本地安装 Docker。

### 1. 创建 GitHub Actions 工作流

在你的仓库中创建 `.github/workflows/docker-publish.yml`:

```yaml
name: Build and Publish Docker Image

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'
  workflow_dispatch:

env:
  REGISTRY: docker.io
  IMAGE_NAME: bullshitai52/emby-stats

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=latest
            type=raw,value=timezone-fix
            type=sha,prefix={{branch}}-

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 2. 配置 Docker Hub 密钥

1. 登录 Docker Hub: https://hub.docker.com/
2. 创建 Access Token:
   - 点击右上角头像 → Account Settings
   - Security → New Access Token
   - 描述: "GitHub Actions"
   - 权限: Read, Write, Delete
   - 复制生成的 token

3. 在 GitHub 仓库中添加 Secrets:
   - 打开你的仓库: https://github.com/bullshitAI52/emby-stats
   - Settings → Secrets and variables → Actions
   - 点击 "New repository secret"
   - 添加两个 secrets:
     - `DOCKERHUB_USERNAME`: 你的 Docker Hub 用户名 (bullshitai52)
     - `DOCKERHUB_TOKEN`: 刚才复制的 token

### 3. 触发构建

提交并推送 workflow 文件后,GitHub Actions 会自动构建并发布镜像。

你也可以手动触发:
- 打开仓库的 Actions 页面
- 选择 "Build and Publish Docker Image"
- 点击 "Run workflow"

### 4. 使用镜像

构建完成后,你的朋友可以直接使用:

```bash
docker pull bullshitai52/emby-stats:latest
```

或者:

```bash
docker pull bullshitai52/emby-stats:timezone-fix
```

---

## 方案二: 本地构建 (需要安装 Docker)

如果你想在本地构建,需要先安装 Docker。

### 1. 安装 Docker Desktop

下载并安装: https://www.docker.com/products/docker-desktop/

### 2. 登录 Docker Hub

```bash
docker login
# 输入用户名: bullshitai52
# 输入密码或 token
```

### 3. 构建镜像

```bash
cd /Users/apple/Downloads/emby-stats

# 构建镜像(带两个标签)
docker build -t bullshitai52/emby-stats:latest \
             -t bullshitai52/emby-stats:timezone-fix .
```

### 4. 推送到 Docker Hub

```bash
# 推送 latest 标签
docker push bullshitai52/emby-stats:latest

# 推送 timezone-fix 标签
docker push bullshitai52/emby-stats:timezone-fix
```

### 5. 验证

访问 Docker Hub 查看镜像:
https://hub.docker.com/r/bullshitai52/emby-stats

---

## 你的朋友如何使用

### 方法 1: 使用 docker run

```bash
docker run -d \
  --name emby-stats \
  --restart unless-stopped \
  -p 8899:8000 \
  -v /path/to/emby/data:/data \
  -v emby-stats-config:/config \
  -e TZ=Asia/Shanghai \
  -e TZ_OFFSET=8 \
  -e PLAYBACK_DB=/data/playback_reporting.db \
  -e USERS_DB=/data/users.db \
  -e AUTH_DB=/data/authentication.db \
  -e EMBY_URL=http://your-emby-server:8096 \
  bullshitai52/emby-stats:latest
```

### 方法 2: 使用 docker-compose

创建 `docker-compose.yml`:

```yaml
services:
  emby-stats:
    image: bullshitai52/emby-stats:latest
    container_name: emby-stats
    restart: unless-stopped
    ports:
      - "8899:8000"
    volumes:
      - /path/to/emby/data:/data
      - emby-stats-config:/config
    environment:
      - TZ=Asia/Shanghai
      - TZ_OFFSET=8
      - PLAYBACK_DB=/data/playback_reporting.db
      - USERS_DB=/data/users.db
      - AUTH_DB=/data/authentication.db
      - EMBY_URL=http://your-emby-server:8096

volumes:
  emby-stats-config:
```

然后运行:

```bash
docker-compose up -d
```

---

## 镜像信息

- **镜像名称:** `bullshitai52/emby-stats`
- **标签:**
  - `latest` - 最新版本(包含时区修复)
  - `timezone-fix` - 时区修复版本(与 latest 相同)
- **架构:** linux/amd64
- **基础镜像:** Python 3.11 + Node 20

## 包含的修复

✅ 活跃时段分布时间显示修复  
✅ 播放历史时间显示修复  
✅ 所有时间显示正确转换为本地时区  

详细说明: https://github.com/bullshitAI52/emby-stats/blob/main/TIMEZONE_FIX.md

---

**推荐使用方案一(GitHub Actions)**,这样每次你推送代码更新,都会自动构建新的镜像!
