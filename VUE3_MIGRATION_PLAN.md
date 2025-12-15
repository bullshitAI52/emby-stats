# Emby Stats 前端重构计划 - React to Vue 3 (细化版)

## 项目目标

将整个前端从 React 技术栈迁移到 Vue 3 技术栈

**当前技术栈：** React 19 + Context + React Router + Tailwind CSS + ECharts
**目标技术栈：** Vue 3 + Pinia + Vue Router + Vuetify + ECharts + PWA

---

## 图例说明
- `[ ]` 待完成
- `[>]` 进行中
- `[✓]` 已完成
- `[!]` 遇到问题
- `[~]` 部分完成

---

## 阶段 A：环境搭建 (8 个任务)

### A01. 创建 Vue 3 项目 [ ]
**命令：**
```bash
cd /root/emby-stats
npm create vue@latest frontend-vue
```
**选项：** TypeScript✅ Vue Router✅ Pinia✅ 其他❌
**验证：** `frontend-vue` 目录存在，包含 `package.json`
**耗时：** 10 分钟

---

### A02. 安装 Vuetify [ ]
**命令：**
```bash
cd frontend-vue
npm install vuetify@^3.5.0
npm install @mdi/font
```
**验证：** `package.json` 中有 `vuetify` 和 `@mdi/font`
**耗时：** 5 分钟

---

### A03. 安装 ECharts [ ]
**命令：**
```bash
npm install echarts@^5.5.0 vue-echarts@^7.0.0
```
**验证：** `package.json` 中有 `echarts` 和 `vue-echarts`
**耗时：** 5 分钟

---

### A04. 安装工具库 [ ]
**命令：**
```bash
npm install @vueuse/core@^11.0.0
npm install axios@^1.6.0
```
**验证：** `package.json` 中有对应依赖
**耗时：** 5 分钟

---

### A05. 安装 PWA 插件 [ ]
**命令：**
```bash
npm install vite-plugin-pwa@^0.19.0 -D
npm install pinia-plugin-persistedstate
```
**验证：** `package.json` devDependencies 中有 `vite-plugin-pwa`
**耗时：** 5 分钟

---

### A06. 配置 Vuetify 插件 [ ]
**创建文件：** `src/plugins/vuetify.ts`
**内容：**
```typescript
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        colors: {
          primary: '#1976d2',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
        },
      },
    },
  },
})
```
**验证：** 文件存在且无语法错误
**耗时：** 15 分钟

---

### A07. 配置 Vite [ ]
**修改文件：** `vite.config.ts`
**添加内容：**
```typescript
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico'],
      manifest: {
        name: 'Emby Stats',
        short_name: 'Emby Stats',
        description: 'Emby 媒体服务器播放统计分析面板',
        theme_color: '#1976d2',
        background_color: '#121212',
        display: 'standalone',
        icons: [],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```
**验证：** 配置无语法错误，能正常启动开发服务器
**耗时：** 20 分钟

---

### A08. 初始化 main.ts [ ]
**修改文件：** `src/main.ts`
**内容：**
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import vuetify from './plugins/vuetify'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')
```
**验证：** 运行 `npm run dev` 无错误
**耗时：** 10 分钟

---

## 阶段 B：类型定义 (2 个任务)

### B01. 迁移基础类型 [ ]
**创建文件：** `src/types/index.ts`
**从原文件复制：** `frontend/src/types/index.ts`
**包含类型：**
- Server, ServerConfig
- Session, User
- FilterOptions
- OverviewData, TrendData, HourlyData
**验证：** TypeScript 编译无错误
**耗时：** 20 分钟

---

### B02. 迁移扩展类型 [ ]
**继续添加到：** `src/types/index.ts`
**包含类型：**
- UsersData, ClientsData, DevicesData
- RecentData, NowPlayingData, ContentDetailData
- FavoritesData, FavoriteItem, UserFavorites, UserFavoriteItem
**验证：** TypeScript 编译无错误
**耗时：** 20 分钟

---

## 阶段 C：API 服务层 (4 个任务)

### C01. 创建 Axios 实例 [ ]
**创建文件：** `src/services/axios.ts`
**内容：**
```typescript
import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true,
})

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 触发登出逻辑
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
```
**验证：** 导入无错误
**耗时：** 15 分钟

---

### C02. 创建认证 API [ ]
**创建文件：** `src/services/api/auth.ts`
**包含方法：**
```typescript
import axios from '../axios'
import type { User } from '@/types'

export const authApi = {
  login: (serverId: string, username: string, password: string) =>
    axios.post<User>('/auth/login', { server_id: serverId, username, password }),

  logout: () => axios.post('/auth/logout'),

  checkAuth: () => axios.get<{ authenticated: boolean; user?: User }>('/auth/check'),
}
```
**验证：** TypeScript 编译无错误
**耗时：** 20 分钟

---

### C03. 创建服务器 API [ ]
**创建文件：** `src/services/api/servers.ts`
**包含方法：**
```typescript
import axios from '../axios'
import type { Server, ServerConfig } from '@/types'

export const serversApi = {
  getServers: () => axios.get<Server[]>('/servers'),

  addServer: (config: ServerConfig) => axios.post<Server>('/servers', config),

  updateServer: (id: string, config: ServerConfig) =>
    axios.put<Server>(`/servers/${id}`, config),

  deleteServer: (id: string) => axios.delete(`/servers/${id}`),
}
```
**验证：** TypeScript 编译无错误
**耗时：** 20 分钟

---

### C04. 创建统计 API [ ]
**创建文件：** `src/services/api/stats.ts`
**包含方法：**
```typescript
import axios from '../axios'
import type {
  OverviewData,
  TrendData,
  HourlyData,
  UsersData,
  ClientsData,
  DevicesData,
  RecentData,
  NowPlayingData,
  ContentDetailData,
  FilterOptionsData,
  FavoritesData,
} from '@/types'

export const statsApi = {
  getOverview: (params: Record<string, any>) =>
    axios.get<OverviewData>('/overview', { params }),

  getTrend: (params: Record<string, any>) =>
    axios.get<TrendData>('/trend', { params }),

  getHourly: (params: Record<string, any>) =>
    axios.get<HourlyData>('/hourly', { params }),

  getUsers: (params: Record<string, any>) =>
    axios.get<UsersData>('/users', { params }),

  getClients: (params: Record<string, any>) =>
    axios.get<ClientsData>('/clients', { params }),

  getDevices: (params: Record<string, any>) =>
    axios.get<DevicesData>('/devices', { params }),

  getRecent: (params: Record<string, any>) =>
    axios.get<RecentData>('/recent', { params }),

  getNowPlaying: (params: Record<string, any>) =>
    axios.get<NowPlayingData>('/now-playing', { params }),

  getContentDetail: (itemId: string, params: Record<string, any>) =>
    axios.get<ContentDetailData>(`/content-detail`, { params: { ...params, item_id: itemId } }),

  getFilterOptions: (serverId: string) =>
    axios.get<FilterOptionsData>('/filter-options', { params: { server_id: serverId } }),

  getFavorites: (params: Record<string, any>) =>
    axios.get<FavoritesData>('/favorites', { params }),
}
```
**验证：** TypeScript 编译无错误
**耗时：** 30 分钟

---

## 阶段 D：Pinia Stores (5 个任务)

### D01. 创建 Auth Store [ ]
**创建文件：** `src/stores/auth.ts`
**内容：**
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api/auth'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const username = computed(() => user.value?.username || null)
  const isAdmin = computed(() => user.value?.is_admin || false)

  async function login(serverId: string, username: string, password: string) {
    isLoading.value = true
    try {
      const response = await authApi.login(serverId, username, password)
      user.value = response.data
      return true
    } catch (error) {
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      user.value = null
    }
  }

  async function checkAuth() {
    isLoading.value = true
    try {
      const response = await authApi.checkAuth()
      if (response.data.authenticated && response.data.user) {
        user.value = response.data.user
      } else {
        user.value = null
      }
    } catch {
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    isLoading,
    isAuthenticated,
    username,
    isAdmin,
    login,
    logout,
    checkAuth,
  }
}, {
  persist: {
    storage: sessionStorage,
  },
})
```
**验证：** 可以导入使用
**耗时：** 30 分钟

---

### D02. 创建 Server Store [ ]
**创建文件：** `src/stores/server.ts`
**内容：**
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { serversApi } from '@/services/api/servers'
import type { Server, ServerConfig } from '@/types'

export const useServerStore = defineStore('server', () => {
  const servers = ref<Server[]>([])
  const currentServerId = ref<string | null>(null)
  const loading = ref(false)

  const currentServer = computed(() =>
    servers.value.find((s) => s.id === currentServerId.value) || null
  )

  const defaultServer = computed(() =>
    servers.value.find((s) => s.is_default) || servers.value[0] || null
  )

  async function fetchServers() {
    loading.value = true
    try {
      const response = await serversApi.getServers()
      servers.value = response.data
      if (!currentServerId.value && defaultServer.value) {
        currentServerId.value = defaultServer.value.id
      }
    } finally {
      loading.value = false
    }
  }

  function setCurrentServer(serverId: string) {
    currentServerId.value = serverId
  }

  async function addServer(config: ServerConfig) {
    const response = await serversApi.addServer(config)
    servers.value.push(response.data)
    return response.data
  }

  async function updateServer(id: string, config: ServerConfig) {
    const response = await serversApi.updateServer(id, config)
    const index = servers.value.findIndex((s) => s.id === id)
    if (index !== -1) {
      servers.value[index] = response.data
    }
    return response.data
  }

  async function deleteServer(id: string) {
    await serversApi.deleteServer(id)
    servers.value = servers.value.filter((s) => s.id !== id)
    if (currentServerId.value === id) {
      currentServerId.value = defaultServer.value?.id || null
    }
  }

  return {
    servers,
    currentServerId,
    currentServer,
    defaultServer,
    loading,
    fetchServers,
    setCurrentServer,
    addServer,
    updateServer,
    deleteServer,
  }
}, {
  persist: {
    paths: ['currentServerId'],
  },
})
```
**验证：** 可以导入使用
**耗时：** 40 分钟

---

### D03. 创建 Filter Store [ ]
**创建文件：** `src/stores/filter.ts`
**内容：**
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statsApi } from '@/services/api/stats'
import type { FilterOptionsData } from '@/types'

export const useFilterStore = defineStore('filter', () => {
  const days = ref(30)
  const startDate = ref<string | null>(null)
  const endDate = ref<string | null>(null)
  const users = ref<string[]>([])
  const clients = ref<string[]>([])
  const devices = ref<string[]>([])
  const itemTypes = ref<string[]>([])
  const playbackMethods = ref<string[]>([])
  const options = ref<FilterOptionsData | null>(null)

  const hasActiveFilters = computed(() => {
    return (
      days.value !== 30 ||
      startDate.value !== null ||
      endDate.value !== null ||
      users.value.length > 0 ||
      clients.value.length > 0 ||
      devices.value.length > 0 ||
      itemTypes.value.length > 0 ||
      playbackMethods.value.length > 0
    )
  })

  const buildQueryParams = computed(() => {
    const params: Record<string, any> = {}
    if (days.value) params.days = days.value
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    if (users.value.length) params.users = users.value.join(',')
    if (clients.value.length) params.clients = clients.value.join(',')
    if (devices.value.length) params.devices = devices.value.join(',')
    if (itemTypes.value.length) params.item_types = itemTypes.value.join(',')
    if (playbackMethods.value.length) params.playback_methods = playbackMethods.value.join(',')
    return params
  })

  async function fetchFilterOptions(serverId: string) {
    try {
      const response = await statsApi.getFilterOptions(serverId)
      options.value = response.data
    } catch (error) {
      console.error('Failed to fetch filter options:', error)
    }
  }

  function clearFilters() {
    days.value = 30
    startDate.value = null
    endDate.value = null
    users.value = []
    clients.value = []
    devices.value = []
    itemTypes.value = []
    playbackMethods.value = []
  }

  return {
    days,
    startDate,
    endDate,
    users,
    clients,
    devices,
    itemTypes,
    playbackMethods,
    options,
    hasActiveFilters,
    buildQueryParams,
    fetchFilterOptions,
    clearFilters,
  }
}, {
  persist: true,
})
```
**验证：** 可以导入使用
**耗时：** 40 分钟

---

### D04. 创建 Theme Store [ ]
**创建文件：** `src/stores/theme.ts`
**内容：**
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useTheme } from 'vuetify'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(true)

  function toggleTheme() {
    isDark.value = !isDark.value
    const theme = useTheme()
    theme.global.name.value = isDark.value ? 'dark' : 'light'
  }

  function setTheme(dark: boolean) {
    isDark.value = dark
    const theme = useTheme()
    theme.global.name.value = isDark.value ? 'dark' : 'light'
  }

  return {
    isDark,
    toggleTheme,
    setTheme,
  }
}, {
  persist: true,
})
```
**验证：** 可以导入使用
**耗时：** 20 分钟

---

### D05. 配置 Stores 入口 [ ]
**创建文件：** `src/stores/index.ts`
**内容：**
```typescript
export { useAuthStore } from './auth'
export { useServerStore } from './server'
export { useFilterStore } from './filter'
export { useThemeStore } from './theme'
```
**验证：** 可以统一导入
**耗时：** 5 分钟

---

## 阶段 E：工具函数和 Composables (6 个任务)

### E01. 创建工具函数 [ ]
**创建文件：** `src/utils/index.ts`
**内容：**
```typescript
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('zh-CN')
}

export function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}
```
**验证：** TypeScript 编译无错误
**耗时：** 20 分钟

---

### E02. 创建 useApi Composable [ ]
**创建文件：** `src/composables/useApi.ts`
**内容：**
```typescript
import { ref } from 'vue'
import type { AxiosResponse } from 'axios'

export function useApi<T>(apiFunc: (...args: any[]) => Promise<AxiosResponse<T>>) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function execute(...args: any[]): Promise<T | null> {
    loading.value = true
    error.value = null
    try {
      const response = await apiFunc(...args)
      data.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    execute,
  }
}
```
**验证：** TypeScript 编译无错误
**耗时：** 20 分钟

---

### E03. 创建 useToast Composable [ ]
**创建文件：** `src/composables/useToast.ts`
**内容：**
```typescript
import { ref } from 'vue'

interface ToastState {
  show: boolean
  message: string
  color: string
}

const state = ref<ToastState>({
  show: false,
  message: '',
  color: 'info',
})

export function useToast() {
  function showToast(message: string, color: 'success' | 'error' | 'info' | 'warning' = 'info') {
    state.value = {
      show: true,
      message,
      color,
    }
  }

  function success(message: string) {
    showToast(message, 'success')
  }

  function error(message: string) {
    showToast(message, 'error')
  }

  function info(message: string) {
    showToast(message, 'info')
  }

  function warning(message: string) {
    showToast(message, 'warning')
  }

  function close() {
    state.value.show = false
  }

  return {
    state,
    showToast,
    success,
    error,
    info,
    warning,
    close,
  }
}
```
**验证：** TypeScript 编译无错误
**耗时：** 25 分钟

---

### E04. 创建 useConfirm Composable [ ]
**创建文件：** `src/composables/useConfirm.ts`
**内容：**
```typescript
import { ref } from 'vue'

interface ConfirmState {
  show: boolean
  title: string
  message: string
  resolve: ((value: boolean) => void) | null
}

const state = ref<ConfirmState>({
  show: false,
  title: '',
  message: '',
  resolve: null,
})

export function useConfirm() {
  function confirm(title: string, message: string): Promise<boolean> {
    return new Promise((resolve) => {
      state.value = {
        show: true,
        title,
        message,
        resolve,
      }
    })
  }

  function handleConfirm() {
    if (state.value.resolve) {
      state.value.resolve(true)
    }
    state.value.show = false
  }

  function handleCancel() {
    if (state.value.resolve) {
      state.value.resolve(false)
    }
    state.value.show = false
  }

  return {
    state,
    confirm,
    handleConfirm,
    handleCancel,
  }
}
```
**验证：** TypeScript 编译无错误
**耗时：** 25 分钟

---

### E05. 创建 useLoading Composable [ ]
**创建文件：** `src/composables/useLoading.ts`
**内容：**
```typescript
import { ref } from 'vue'

export function useLoading(initialState = false) {
  const loading = ref(initialState)

  function start() {
    loading.value = true
  }

  function stop() {
    loading.value = false
  }

  async function withLoading<T>(fn: () => Promise<T>): Promise<T> {
    start()
    try {
      return await fn()
    } finally {
      stop()
    }
  }

  return {
    loading,
    start,
    stop,
    withLoading,
  }
}
```
**验证：** TypeScript 编译无错误
**耗时：** 15 分钟

---

### E06. 创建 Composables 入口 [ ]
**创建文件：** `src/composables/index.ts`
**内容：**
```typescript
export { useApi } from './useApi'
export { useToast } from './useToast'
export { useConfirm } from './useConfirm'
export { useLoading } from './useLoading'
```
**验证：** 可以统一导入
**耗时：** 5 分钟

---

## 阶段 F：UI 基础组件 (10 个任务)

### F01. 创建 Card 组件 [ ]
**创建文件：** `src/components/ui/Card.vue`
**内容：** 使用 Vuetify v-card，支持 title、subtitle、loading
**验证：** 组件可以正常渲染
**耗时：** 30 分钟

---

### F02. 创建 Modal 组件 [ ]
**创建文件：** `src/components/ui/Modal.vue`
**内容：** 使用 Vuetify v-dialog，支持 title、width、persistent、footer
**验证：** 组件可以正常渲染和关闭
**耗时：** 30 分钟

---

### F03. 创建 Avatar 组件 [ ]
**创建文件：** `src/components/ui/Avatar.vue`
**内容：** 使用 Vuetify v-avatar，支持用户名首字母、图片、大小
**验证：** 组件显示正确
**耗时：** 20 分钟

---

### F04. 创建 Skeleton 组件 [ ]
**创建文件：** `src/components/ui/Skeleton.vue`
**内容：** 使用 Vuetify v-skeleton-loader，支持不同类型
**验证：** 加载动画正常
**耗时：** 15 分钟

---

### F05. 创建 Chip 组件 [ ]
**创建文件：** `src/components/ui/Chip.vue`
**内容：** 使用 Vuetify v-chip，支持颜色、closable、点击
**验证：** 组件交互正常
**耗时：** 15 分钟

---

### F06. 创建 Progress 组件 [ ]
**创建文件：** `src/components/ui/Progress.vue`
**内容：** 使用 Vuetify v-progress-linear，支持百分比、颜色
**验证：** 进度条显示正确
**耗时：** 15 分钟

---

### F07. 创建 AnimatedNumber 组件 [ ]
**创建文件：** `src/components/ui/AnimatedNumber.vue`
**内容：** 数字动画效果，使用 Vue transition 或 requestAnimationFrame
**验证：** 数字变化有动画
**耗时：** 40 分钟

---

### F08. 创建 PosterCard 组件 [ ]
**创建文件：** `src/components/ui/PosterCard.vue`
**内容：** 使用 Vuetify v-card + v-img，海报展示、懒加载
**验证：** 海报显示正确、点击放大
**耗时：** 40 分钟

---

### F09. 创建 PosterModal 组件 [ ]
**创建文件：** `src/components/ui/PosterModal.vue`
**内容：** 海报放大查看，使用 v-dialog
**验证：** 模态框显示和关闭正常
**耗时：** 30 分钟

---

### F10. 创建 UI 组件入口 [ ]
**创建文件：** `src/components/ui/index.ts`
**内容：** 导出所有 UI 组件
**验证：** 可以统一导入
**耗时：** 5 分钟

---

## 阶段 G：图表组件 (4 个任务)

### G01. 创建 TrendChart 组件 [ ]
**创建文件：** `src/components/charts/TrendChart.vue`
**内容：** 使用 vue-echarts，双 Y 轴折线图，播放次数+时长趋势
**验证：** 图表渲染正确、响应式
**耗时：** 60 分钟

---

### G02. 创建 HeatmapChart 组件 [ ]
**创建文件：** `src/components/charts/HeatmapChart.vue`
**内容：** 7x24 热力图，使用 ECharts heatmap 或自定义 CSS Grid
**验证：** 热力图显示正确、Tooltip 正常
**耗时：** 60 分钟

---

### G03. 创建 PieChart 组件 [ ]
**创建文件：** `src/components/charts/PieChart.vue`
**内容：** 使用 vue-echarts，饼图，支持 Legend 筛选
**验证：** 饼图显示正确、交互正常
**耗时：** 40 分钟

---

### G04. 创建 UsersChart 组件 [ ]
**创建文件：** `src/components/charts/UsersChart.vue`
**内容：** 使用 vue-echarts，横向柱状图，用户播放时长排行
**验证：** 柱状图显示正确
**耗时：** 40 分钟

---

## 阶段 H：功能组件 (6 个任务)

### H01. 创建 NowPlaying 组件 [ ]
**创建文件：** `src/components/NowPlaying.vue`
**内容：** 正在播放会话，使用 VueUse useIntervalFn 自动刷新
**验证：** 实时更新正常
**耗时：** 60 分钟

---

### H02. 创建 FilterPanel 组件 (上) [ ]
**创建文件：** `src/components/FilterPanel.vue`
**内容：** 时间范围选择（days、date range）部分
**验证：** 时间筛选正常
**耗时：** 40 分钟

---

### H03. 创建 FilterPanel 组件 (下) [ ]
**继续完善：** `src/components/FilterPanel.vue`
**内容：** 多选筛选（users、clients、devices、itemTypes、playbackMethods）
**验证：** 所有筛选功能正常
**耗时：** 50 分钟

---

### H04. 创建 FilePickerModal 组件 [ ]
**创建文件：** `src/components/FilePickerModal.vue`
**内容：** 文件浏览器，目录导航、文件选择
**验证：** 文件选择功能正常
**耗时：** 60 分钟

---

### H05. 创建 ServerManagementPanel 组件 (上) [ ]
**创建文件：** `src/components/ServerManagementPanel.vue`
**内容：** 服务器列表展示、添加服务器表单
**验证：** 列表和添加功能正常
**耗时：** 50 分钟

---

### H06. 创建 ServerManagementPanel 组件 (下) [ ]
**继续完善：** `src/components/ServerManagementPanel.vue`
**内容：** 编辑、删除服务器、设置默认服务器
**验证：** 所有管理功能正常
**耗时：** 40 分钟

---

## 阶段 I：路由和布局 (3 个任务)

### I01. 配置 Vue Router [ ]
**修改文件：** `src/router/index.ts`
**内容：** 路由配置、路由守卫、页面标题
**验证：** 路由跳转正常、守卫生效
**耗时：** 40 分钟

---

### I02. 创建主布局组件 (上) [ ]
**创建文件：** `src/layouts/DefaultLayout.vue`
**内容：** v-app、v-navigation-drawer、导航菜单
**验证：** 布局结构正确、导航工作
**耗时：** 50 分钟

---

### I03. 创建主布局组件 (下) [ ]
**继续完善：** `src/layouts/DefaultLayout.vue`
**内容：** v-app-bar、服务器选择、用户信息、筛选面板
**验证：** 完整布局功能正常
**耗时：** 50 分钟

---

## 阶段 J：页面组件 - 简单页面 (4 个任务)

### J01. 创建 Login 页面 [ ]
**创建文件：** `src/pages/Login.vue`
**内容：** 服务器选择、用户名密码输入、登录逻辑
**验证：** 登录功能正常
**耗时：** 60 分钟

---

### J02. 创建 Users 页面 [ ]
**创建文件：** `src/pages/Users.vue`
**内容：** 用户统计表格、UsersChart
**验证：** 用户数据展示正确
**耗时：** 50 分钟

---

### J03. 创建 Devices 页面 [ ]
**创建文件：** `src/pages/Devices.vue`
**内容：** 客户端、设备、播放方式三个 PieChart
**验证：** 设备统计展示正确
**耗时：** 50 分钟

---

### J04. 创建 ContentDetail 页面 [ ]
**创建文件：** `src/pages/ContentDetail.vue`
**内容：** 内容详情、播放记录列表、返回按钮
**验证：** 详情页显示正确
**耗时：** 50 分钟

---

## 阶段 K：页面组件 - 复杂页面 (5 个任务)

### K01. 创建 Overview 页面 (上) [ ]
**创建文件：** `src/pages/Overview.vue`
**内容：** 统计卡片（总播放、总时长、用户数、内容数）
**验证：** 统计卡片显示正确
**耗时：** 40 分钟

---

### K02. 创建 Overview 页面 (下) [ ]
**继续完善：** `src/pages/Overview.vue`
**内容：** TrendChart、HeatmapChart、热门内容排行
**验证：** 完整总览页面功能正常
**耗时：** 50 分钟

---

### K03. 创建 Content 页面 [ ]
**创建文件：** `src/pages/Content.vue`
**内容：** 热门剧集、热门电影排行、切换视图、点击详情
**验证：** 内容页功能正常
**耗时：** 60 分钟

---

### K04. 创建 History 页面 [ ]
**创建文件：** `src/pages/History.vue`
**内容：** 最近播放记录、虚拟滚动、点击详情
**验证：** 历史记录展示正确
**耗时：** 60 分钟

---

### K05. 创建 Favorites 页面 [ ]
**创建文件：** `src/pages/Favorites.vue`
**内容：** 双视图切换、搜索、类型筛选、收藏展示
**验证：** 收藏页功能完整
**耗时：** 70 分钟

---

## 阶段 L：报告和 TG Bot (2 个任务)

### L01. 创建 Report 页面 (上) [ ]
**创建文件：** `src/pages/Report.vue`
**内容：** TG Bot 配置表单、报告周期配置
**验证：** 配置表单正常
**耗时：** 60 分钟

---

### L02. 创建 Report 页面 (下) [ ]
**继续完善：** `src/pages/Report.vue`
**内容：** 报告预览、手动发送、TG 绑定用户列表
**验证：** 报告页功能完整
**耗时：** 60 分钟

---

## 阶段 M：App 根组件和全局组件 (3 个任务)

### M01. 创建 App.vue [ ]
**修改文件：** `src/App.vue`
**内容：** v-app、router-view、全局 loading、主题支持
**验证：** 根组件正常工作
**耗时：** 30 分钟

---

### M02. 创建全局 Toast 组件 [ ]
**创建文件：** `src/components/GlobalToast.vue`
**内容：** 使用 Vuetify v-snackbar，全局消息提示
**验证：** Toast 提示正常
**耗时：** 20 分钟

---

### M03. 创建全局 Confirm 组件 [ ]
**创建文件：** `src/components/GlobalConfirm.vue`
**内容：** 使用 Vuetify v-dialog，全局确认对话框
**验证：** 确认对话框正常
**耗时：** 20 分钟

---

## 阶段 N：测试和调试 (8 个任务)

### N01. 测试登录登出流程 [ ]
**测试内容：** 登录、登出、会话保持、权限检查
**验证标准：** 所有登录相关功能正常
**耗时：** 30 分钟

---

### N02. 测试服务器切换 [ ]
**测试内容：** 切换服务器、数据自动刷新、默认服务器
**验证标准：** 服务器切换流畅、数据正确
**耗时：** 20 分钟

---

### N03. 测试筛选功能 [ ]
**测试内容：** 所有筛选条件、清空筛选、筛选持久化
**验证标准：** 筛选功能完整、数据正确
**耗时：** 30 分钟

---

### N04. 测试所有页面数据展示 [ ]
**测试内容：** 9 个页面的数据加载和展示
**验证标准：** 所有页面数据正确、无报错
**耗时：** 60 分钟

---

### N05. 测试图表交互 [ ]
**测试内容：** 4 个图表的交互、响应式、Tooltip
**验证标准：** 图表交互流畅、显示正确
**耗时：** 30 分钟

---

### N06. 测试正在播放和报告 [ ]
**测试内容：** 实时更新、报告配置、预览、发送
**验证标准：** 功能完整、无错误
**耗时：** 30 分钟

---

### N07. 修复发现的 Bug [ ]
**测试内容：** 修复测试中发现的所有问题
**验证标准：** 所有 Bug 已修复
**耗时：** 120 分钟

---

### N08. 浏览器兼容性测试 [ ]
**测试内容：** Chrome、Firefox、Safari、Edge
**验证标准：** 主流浏览器均正常工作
**耗时：** 30 分钟

---

## 阶段 O：性能优化 (6 个任务)

### O01. 组件懒加载 [ ]
**优化内容：** 使用 defineAsyncComponent 懒加载大组件
**验证标准：** 首屏加载速度提升
**耗时：** 30 分钟

---

### O02. 路由懒加载 [ ]
**优化内容：** 路由组件动态导入
**验证标准：** 路由切换速度快
**耗时：** 20 分钟

---

### O03. 图片懒加载优化 [ ]
**优化内容：** 使用 v-img 的 lazy 属性、占位图
**验证标准：** 图片加载流畅
**耗时：** 30 分钟

---

### O04. ECharts 按需引入 [ ]
**优化内容：** 只引入需要的 ECharts 组件
**验证标准：** Bundle 大小减小
**耗时：** 40 分钟

---

### O05. Vuetify 组件优化 [ ]
**优化内容：** 按需导入 Vuetify 组件（如果可能）
**验证标准：** Bundle 大小优化
**耗时：** 30 分钟

---

### O06. 虚拟滚动优化 [ ]
**优化内容：** 在 History 等长列表页面使用虚拟滚动
**验证标准：** 大数据量列表流畅
**耗时：** 40 分钟

---

## 阶段 P：响应式和 PWA (5 个任务)

### P01. 移动端适配 (xs/sm) [ ]
**适配内容：** 320-767px 移动端布局调整
**验证标准：** 移动端体验良好
**耗时：** 90 分钟

---

### P02. 平板端适配 (md) [ ]
**适配内容：** 768-1024px 平板端布局调整
**验证标准：** 平板端体验良好
**耗时：** 60 分钟

---

### P03. 桌面端优化 (lg/xl) [ ]
**适配内容：** 1264px+ 桌面端布局优化
**验证标准：** 桌面端体验最佳
**耗时：** 40 分钟

---

### P04. PWA Manifest 完善 [ ]
**完善内容：** 应用图标、启动画面、主题色
**验证标准：** PWA 可安装、图标正确
**耗时：** 40 分钟

---

### P05. Service Worker 配置 [ ]
**配置内容：** 缓存策略、离线支持、更新提示
**验证标准：** 离线可访问、更新流畅
**耗时：** 60 分钟

---

## 阶段 Q：Docker 集成和发布 (6 个任务)

### Q01. 更新 Dockerfile [ ]
**修改文件：** `/root/emby-stats/Dockerfile`
**修改内容：** 将 frontend 构建改为 frontend-vue
**验证：** Dockerfile 语法正确
**耗时：** 20 分钟

---

### Q02. 本地构建测试 [ ]
**测试命令：** `docker build -t qc0624/emby-stats:vue3-test .`
**验证：** 构建成功、镜像可用
**耗时：** 30 分钟

---

### Q03. 本地容器测试 [ ]
**测试命令：** 使用 docker-compose 启动容器
**验证：** 容器正常运行、所有功能可用
**耗时：** 40 分钟

---

### Q04. 更新版本号和文档 [ ]
**修改文件：** Layout.vue 版本号、CHANGELOG.md、DEVELOPMENT.md
**验证：** 文档完整、版本号正确
**耗时：** 40 分钟

---

### Q05. 代码整理 [ ]
**整理内容：** 删除 console.log、调试代码、未使用导入、格式化代码
**验证：** 代码整洁、无警告
**耗时：** 40 分钟

---

### Q06. 构建和推送镜像 [ ]
**命令：**
```bash
docker build -t qc0624/emby-stats:latest .
docker build -t qc0624/emby-stats:v2.0.0 .
docker push qc0624/emby-stats:latest
docker push qc0624/emby-stats:v2.0.0
```
**验证：** 镜像推送成功
**耗时：** 30 分钟

---

## 总览统计

| 阶段 | 任务数 | 预计总时间 |
|------|-------|----------|
| A. 环境搭建 | 8 | 1.2 小时 |
| B. 类型定义 | 2 | 0.7 小时 |
| C. API 服务层 | 4 | 1.4 小时 |
| D. Pinia Stores | 5 | 2.2 小时 |
| E. 工具和 Composables | 6 | 1.8 小时 |
| F. UI 基础组件 | 10 | 4.2 小时 |
| G. 图表组件 | 4 | 3.3 小时 |
| H. 功能组件 | 6 | 5.0 小时 |
| I. 路由和布局 | 3 | 2.3 小时 |
| J. 简单页面 | 4 | 3.5 小时 |
| K. 复杂页面 | 5 | 4.7 小时 |
| L. 报告和 TG Bot | 2 | 2.0 小时 |
| M. App 和全局组件 | 3 | 1.2 小时 |
| N. 测试和调试 | 8 | 5.5 小时 |
| O. 性能优化 | 6 | 3.2 小时 |
| P. 响应式和 PWA | 5 | 4.8 小时 |
| Q. Docker 和发布 | 6 | 3.3 小时 |
| **总计** | **87 任务** | **约 50 小时** |

---

## 使用说明

1. **顺序执行**：按 A → B → C ... → Q 的顺序执行
2. **标记进度**：完成一个任务标记 `[✓]`，进行中标记 `[>]`
3. **中断恢复**：可随时中断，下次从最后一个未完成任务继续
4. **灵活调整**：如果某个任务遇到问题，标记 `[!]` 并记录问题
5. **验证优先**：每个任务完成后立即验证，确保正确再继续

---

## 下一步

准备好后，请告知从哪个任务开始（建议 **A01**），我将：
1. 详细执行该任务
2. 标记进度状态
3. 验证结果
4. 继续下一个任务
