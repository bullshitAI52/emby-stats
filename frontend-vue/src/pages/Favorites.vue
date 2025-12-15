<template>
  <div class="page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">收藏统计</h2>
        <p class="page-subtitle">查看用户收藏的内容和热门排行</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <template v-if="loading">
      <v-row class="mb-6">
        <v-col v-for="i in 3" :key="i" cols="12" sm="4">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 数据展示 -->
    <template v-else-if="favoritesData">
      <!-- 统计卡片 -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="4">
          <v-card class="pulse-card" hover>
            <v-card-text>
              <div class="stat-content">
                <div class="stat-icon" style="background: rgba(236, 72, 153, 0.1);">
                  <v-icon size="24" color="pink">mdi-heart</v-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">收藏内容</div>
                  <AnimatedNumber
                    :value="totalFavoriteItems"
                    class="stat-value"
                    style="color: rgb(236, 72, 153);"
                  />
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="4">
          <v-card class="pulse-card" hover>
            <v-card-text>
              <div class="stat-content">
                <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1);">
                  <v-icon size="24" color="primary">mdi-account-group</v-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">有收藏的用户</div>
                  <div class="stat-value text-primary">
                    {{ usersWithFavorites }} / {{ totalUsers }}
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="4">
          <v-card class="pulse-card" hover>
            <v-card-text>
              <div class="stat-content">
                <div class="stat-icon" style="background: rgba(168, 85, 247, 0.1);">
                  <v-icon size="24" color="purple">mdi-filmstrip</v-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">电影 / 剧集</div>
                  <div class="stat-value text-purple">
                    {{ movieCount }} / {{ seriesCount }}
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 主内容区 -->
      <v-card hover>
        <v-card-text>
          <!-- 顶部控制栏 -->
          <div class="d-flex flex-column flex-sm-row justify-space-between align-start mb-4" style="gap: 12px;">
            <!-- 视图切换 -->
            <v-btn-toggle
              v-model="viewMode"
              mandatory
              variant="outlined"
              divided
              density="comfortable"
            >
              <v-btn value="users" prepend-icon="mdi-account">
                按用户
              </v-btn>
              <v-btn value="ranking" prepend-icon="mdi-heart">
                热门榜单
              </v-btn>
            </v-btn-toggle>

            <!-- 类型筛选 -->
            <v-btn-toggle
              v-model="filterType"
              mandatory
              variant="outlined"
              divided
              density="comfortable"
            >
              <v-btn value="all">全部</v-btn>
              <v-btn value="Movie">电影</v-btn>
              <v-btn value="Series">剧集</v-btn>
            </v-btn-toggle>
          </div>

          <!-- 搜索框 -->
          <v-text-field
            v-model="searchQuery"
            :placeholder="viewMode === 'users' ? '搜索用户或内容...' : '搜索内容或用户...'"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
            class="mb-4"
          />

          <!-- 按用户视图 -->
          <template v-if="viewMode === 'users'">
            <div v-if="filteredUsersFavorites.length === 0" class="text-center py-8 text-grey">
              {{ searchQuery ? '没有找到匹配的结果' : '暂无收藏数据' }}
            </div>
            <div v-else class="user-list">
              <v-expansion-panels v-model="expandedUsers" multiple>
                <v-expansion-panel
                  v-for="user in filteredUsersFavorites"
                  :key="user.user_id"
                  :value="user.user_id"
                >
                  <v-expansion-panel-title>
                    <div class="d-flex align-center w-100" style="gap: 12px;">
                      <!-- 用户头像 -->
                      <Avatar :name="user.username" size="40" />

                      <!-- 用户信息 -->
                      <div class="flex-grow-1">
                        <div class="d-flex align-center" style="gap: 8px;">
                          <span class="font-weight-medium">{{ user.username }}</span>
                          <v-chip size="x-small" color="grey">
                            收藏 {{ user.favorite_count }} 部
                          </v-chip>
                        </div>
                        <div class="text-caption text-grey mt-1">
                          <span v-if="user.movie_count > 0">
                            <v-icon size="small">mdi-movie</v-icon> {{ user.movie_count }} 电影
                          </span>
                          <span v-if="user.series_count > 0" class="ml-3">
                            <v-icon size="small">mdi-television</v-icon> {{ user.series_count }} 剧集
                          </span>
                        </div>
                      </div>

                      <!-- 海报预览（桌面端） -->
                      <div class="d-none d-sm-flex align-center" style="gap: 4px;">
                        <div
                          v-for="item in user.preview_items"
                          :key="item.item_id"
                          class="preview-poster"
                        >
                          <v-img
                            v-if="item.poster_url"
                            :src="item.poster_url"
                            aspect-ratio="0.67"
                            cover
                            class="rounded"
                          />
                          <div v-else class="preview-poster-placeholder">
                            <v-icon size="small">mdi-filmstrip</v-icon>
                          </div>
                        </div>
                        <div v-if="user.favorite_count > 5" class="preview-poster-more">
                          +{{ user.favorite_count - 5 }}
                        </div>
                      </div>

                      <!-- 收藏数徽章 -->
                      <div class="d-flex align-center" style="gap: 4px;">
                        <v-icon color="pink">mdi-heart</v-icon>
                        <span class="font-weight-bold text-pink">{{ user.favorite_count }}</span>
                      </div>
                    </div>
                  </v-expansion-panel-title>

                  <v-expansion-panel-text>
                    <v-row class="mt-2">
                      <v-col
                        v-for="item in user.favorites"
                        :key="item.item_id"
                        cols="6"
                        sm="4"
                        md="3"
                        lg="2"
                      >
                        <div class="favorite-item-card" @click="goToDetail(item)">
                          <div class="favorite-item-poster">
                            <v-img
                              v-if="item.poster_url"
                              :src="item.poster_url"
                              aspect-ratio="0.67"
                              cover
                            />
                            <div v-else class="favorite-item-placeholder">
                              <v-icon>mdi-filmstrip</v-icon>
                            </div>
                            <!-- 类型标签 -->
                            <div class="favorite-item-type-badge">
                              {{ item.type === 'Movie' ? '电影' : '剧集' }}
                            </div>
                          </div>
                          <div class="favorite-item-info">
                            <div class="favorite-item-title" :title="item.name">
                              {{ item.name }}
                            </div>
                            <div v-if="item.year" class="favorite-item-year">
                              {{ item.year }}
                            </div>
                          </div>
                        </div>
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </template>

          <!-- 热门榜单视图 -->
          <template v-else>
            <div v-if="filteredItems.length === 0" class="text-center py-8 text-grey">
              {{ searchQuery ? '没有找到匹配的结果' : '暂无收藏数据' }}
            </div>
            <div v-else class="ranking-list">
              <v-expansion-panels v-model="expandedItems" multiple>
                <v-expansion-panel
                  v-for="(item, index) in filteredItems"
                  :key="item.item_id"
                  :value="item.item_id"
                >
                  <v-expansion-panel-title>
                    <div class="d-flex align-center w-100" style="gap: 12px;">
                      <!-- 排名 -->
                      <div class="rank-badge" :class="getRankClass(index + 1)">
                        #{{ index + 1 }}
                      </div>

                      <!-- 海报 -->
                      <div class="ranking-poster">
                        <v-img
                          v-if="item.poster_url"
                          :src="item.poster_url"
                          aspect-ratio="0.67"
                          cover
                          class="rounded"
                        />
                        <div v-else class="ranking-poster-placeholder">
                          <v-icon>mdi-filmstrip</v-icon>
                        </div>
                      </div>

                      <!-- 内容信息 -->
                      <div class="flex-grow-1">
                        <div class="font-weight-medium">{{ item.name }}</div>
                        <div class="text-caption text-grey mt-1">
                          <v-chip size="x-small" :color="item.type === 'Movie' ? 'blue' : 'purple'">
                            {{ item.type === 'Movie' ? '电影' : '剧集' }}
                          </v-chip>
                          <span class="ml-2">{{ item.favorite_count }} 人收藏</span>
                        </div>
                      </div>

                      <!-- 收藏数徽章 -->
                      <div class="d-flex align-center" style="gap: 4px;">
                        <v-icon color="pink">mdi-heart</v-icon>
                        <span class="font-weight-bold text-pink">{{ item.favorite_count }}</span>
                      </div>
                    </div>
                  </v-expansion-panel-title>

                  <v-expansion-panel-text>
                    <div class="mt-2">
                      <div class="text-subtitle-2 mb-2">收藏用户</div>
                      <v-chip-group column>
                        <v-chip
                          v-for="user in item.users"
                          :key="user.user_id"
                          size="small"
                        >
                          <Avatar :name="user.username" size="24" class="mr-2" />
                          {{ user.username }}
                        </v-chip>
                      </v-chip-group>
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </template>
        </v-card-text>
      </v-card>
    </template>

    <!-- 空状态 -->
    <v-row v-else>
      <v-col cols="12">
        <v-alert type="info" variant="tonal">
          暂无收藏数据
        </v-alert>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Avatar, AnimatedNumber } from '@/components/ui'
import { useServerStore, useFilterStore } from '@/stores'
import { statsApi } from '@/services'

const router = useRouter()
const serverStore = useServerStore()
const filterStore = useFilterStore()

const loading = ref(false)
const viewMode = ref<'users' | 'ranking'>('users')
const filterType = ref<'all' | 'Movie' | 'Series'>('all')
const searchQuery = ref('')
const expandedUsers = ref<string[]>([])
const expandedItems = ref<string[]>([])

interface FavoriteItem {
  item_id: string
  name: string
  type: string
  year?: string
  has_poster: boolean
  poster_url?: string
  series_id?: string
  series_name?: string
}

interface UserFavorite {
  user_id: string
  username: string
  favorite_count: number
  favorites: FavoriteItem[]
  movie_count: number
  series_count: number
  preview_items: FavoriteItem[]
}

interface RankingItem {
  item_id: string
  name: string
  type: string
  favorite_count: number
  has_poster: boolean
  poster_url?: string
  series_id?: string
  users: Array<{ user_id: string; username: string }>
}

interface FavoritesData {
  users_favorites: UserFavorite[]
  items: RankingItem[]
  total_users: number
  users_with_favorites: number
}

const favoritesData = ref<FavoritesData | null>(null)

// 统计数据
const totalFavoriteItems = computed(() => favoritesData.value?.items.length || 0)
const totalUsers = computed(() => favoritesData.value?.total_users || 0)
const usersWithFavorites = computed(() => favoritesData.value?.users_with_favorites || 0)
const movieCount = computed(() => favoritesData.value?.items.filter(i => i.type === 'Movie').length || 0)
const seriesCount = computed(() => favoritesData.value?.items.filter(i => i.type === 'Series').length || 0)

// 筛选后的用户收藏列表
const filteredUsersFavorites = computed(() => {
  if (!favoritesData.value) return []

  return favoritesData.value.users_favorites
    .map(user => {
      let filtered = user.favorites

      // 类型筛选
      if (filterType.value !== 'all') {
        filtered = filtered.filter(item => item.type === filterType.value)
      }

      // 搜索筛选
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(item =>
          item.name.toLowerCase().includes(query) ||
          (item.series_name && item.series_name.toLowerCase().includes(query))
        )
      }

      const movieCount = filtered.filter(f => f.type === 'Movie').length
      const seriesCount = filtered.filter(f => f.type === 'Series').length
      const previewItems = filtered.slice(0, 5)

      return {
        ...user,
        favorites: filtered,
        favorite_count: filtered.length,
        movie_count: movieCount,
        series_count: seriesCount,
        preview_items: previewItems
      }
    })
    .filter(user => {
      // 搜索用户名
      if (searchQuery.value.trim() && user.username.toLowerCase().includes(searchQuery.value.toLowerCase())) {
        return true
      }
      return user.favorites.length > 0
    })
})

// 筛选后的排行榜列表
const filteredItems = computed(() => {
  if (!favoritesData.value) return []

  let filtered = favoritesData.value.items

  // 类型筛选
  if (filterType.value !== 'all') {
    filtered = filtered.filter(item => item.type === filterType.value)
  }

  // 搜索筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(query) ||
      item.users.some(u => u.username.toLowerCase().includes(query))
    )
  }

  return filtered
})

// 获取排名样式
function getRankClass(rank: number) {
  switch (rank) {
    case 1: return 'rank-gold'
    case 2: return 'rank-silver'
    case 3: return 'rank-bronze'
    default: return ''
  }
}

// 跳转到详情页
function goToDetail(item: FavoriteItem) {
  // 对于剧集，使用 series_id；对于其他类型，使用 item_id
  if (item.type === 'Series') {
    router.push({
      path: `/content/${item.series_id || item.item_id}`
    })
  } else {
    router.push({
      path: `/content/${item.item_id}`
    })
  }
}

// 获取收藏数据
async function fetchFavoritesData() {
  if (!serverStore.currentServer) return

  loading.value = true
  try {
    const params = {
      server_id: serverStore.currentServer.id,
      ...filterStore.buildQueryParams,
    }

    const response = await statsApi.getFavorites(params)
    const data = response.data

    // 处理用户收藏数据
    const usersFavorites = (data.users_favorites || []).map((uf: any) => ({
      user_id: uf.user_id,
      username: uf.username,
      favorite_count: uf.favorites?.length || 0,
      favorites: (uf.favorites || []).map((f: any) => ({
        item_id: f.item_id,
        name: f.name,
        type: f.type,
        year: f.year,
        has_poster: f.has_poster,
        poster_url: f.has_poster ? `/api/poster/${f.series_id || f.item_id}?maxHeight=720&maxWidth=480&server_id=${serverStore.currentServer?.id}` : undefined,
        series_id: f.series_id,
        series_name: f.series_name,
      })),
      movie_count: 0,
      series_count: 0,
      preview_items: []
    }))

    // 处理排行榜数据
    const items = (data.items || []).map((item: any) => ({
      item_id: item.item_id,
      name: item.name,
      type: item.type,
      favorite_count: item.favorite_count,
      has_poster: item.has_poster,
      poster_url: item.has_poster ? `/api/poster/${item.series_id || item.item_id}?maxHeight=256&maxWidth=192&server_id=${serverStore.currentServer?.id}` : undefined,
      series_id: item.series_id,
      users: item.users || []
    }))

    favoritesData.value = {
      users_favorites: usersFavorites,
      items,
      total_users: data.total_users || 0,
      users_with_favorites: data.users_with_favorites || 0
    }
  } catch (error) {
    console.error('Failed to fetch favorites data:', error)
  } finally {
    loading.value = false
  }
}

// 监听服务器和筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    fetchFavoritesData()
  },
  { deep: true }
)

onMounted(() => {
  fetchFavoritesData()
})
</script>

<style scoped>
.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  opacity: 0.7;
  margin: 0;
}

.pulse-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.pulse-card:hover {
  transform: translateY(-6px) scale(1.02);
}

.v-theme--dark .pulse-card {
  border: 1px solid rgba(59, 130, 246, 0.15);
}

.v-theme--dark .pulse-card:hover {
  border-color: rgba(59, 130, 246, 0.35);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6) !important;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  opacity: 0.7;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
}

/* 海报预览样式 */
.preview-poster {
  width: 32px;
  height: 48px;
  border-radius: 4px;
  overflow: hidden;
  background-color: rgb(39, 39, 42);
}

.preview-poster-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgb(39, 39, 42);
}

.preview-poster-more {
  width: 32px;
  height: 48px;
  border-radius: 4px;
  background-color: rgb(39, 39, 42);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  opacity: 0.7;
}

/* 收藏项目卡片 */
.favorite-item-card {
  cursor: pointer;
  transition: transform 0.2s;
  border-radius: 12px;
  overflow: hidden;
}

.favorite-item-card:hover {
  transform: scale(1.03);
}

.favorite-item-poster {
  position: relative;
  background-color: rgb(39, 39, 42);
  border-radius: 8px;
  overflow: hidden;
}

.favorite-item-placeholder {
  aspect-ratio: 0.67;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgb(39, 39, 42);
}

.favorite-item-type-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  padding: 2px 6px;
  background-color: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  font-size: 10px;
  color: white;
  backdrop-filter: blur(4px);
}

.favorite-item-info {
  padding: 8px 0;
}

.favorite-item-title {
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.favorite-item-year {
  font-size: 10px;
  opacity: 0.6;
  margin-top: 2px;
}

/* 排行榜样式 */
.rank-badge {
  width: 32px;
  text-align: center;
  font-weight: 700;
  font-size: 14px;
}

.rank-gold {
  color: #fbbf24;
}

.rank-silver {
  color: #9ca3af;
}

.rank-bronze {
  color: #f59e0b;
}

.ranking-poster {
  width: 48px;
  height: 64px;
  border-radius: 4px;
  overflow: hidden;
  background-color: rgb(39, 39, 42);
  flex-shrink: 0;
}

.ranking-poster-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .page {
    padding: 16px;
  }

  .stat-value {
    font-size: 20px;
  }
}
</style>
