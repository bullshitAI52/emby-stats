<template>
  <div class="page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">播放历史</h2>
        <p class="page-subtitle">
          查看所有播放记录和搜索内容
        </p>
      </div>
    </div>

    <v-row>
      <v-col cols="12">
        <v-card hover>
          <v-card-title class="card-header">
            <span>最近播放</span>
            <v-icon>mdi-history</v-icon>
          </v-card-title>
          <v-card-text>
            <!-- 搜索栏 -->
            <div class="d-flex flex-column flex-sm-row align-sm-center justify-space-between ga-3 mb-4">
              <!-- 搜索框 -->
              <div class="d-flex ga-2 flex-grow-1">
                <v-text-field
                  v-model="searchInput"
                  placeholder="搜索内容名称..."
                  prepend-inner-icon="mdi-magnify"
                  :append-inner-icon="searchInput ? 'mdi-close' : ''"
                  @click:append-inner="clearSearch"
                  @keydown.enter="handleSearch"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  style="max-width: 400px"
                />
                <v-btn
                  color="primary"
                  @click="handleSearch"
                >
                  搜索
                </v-btn>
              </div>
            </div>

            <!-- 搜索结果提示 -->
            <div v-if="searchQuery" class="mb-4 text-caption text-medium-emphasis">
              搜索结果："{{ searchQuery }}"
              <span v-if="!loading">({{ historyItems.length }} 条记录)</span>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" class="d-flex justify-center align-center py-8">
              <v-progress-circular indeterminate color="primary" />
            </div>

            <!-- 空状态 -->
            <div v-else-if="historyItems.length === 0" class="text-center py-8">
              <p class="text-medium-emphasis">
                {{ searchQuery ? '未找到匹配的播放记录' : '暂无播放记录' }}
              </p>
            </div>

            <!-- 搜索结果：列表展示 -->
            <template v-else-if="isSearching">
              <v-list>
                <v-list-item
                  v-for="(item, index) in itemsWithServerUrls"
                  :key="`search-${item.item_id}-${item.time}-${index}`"
                  class="mb-2 rounded"
                >
                  <template #prepend>
                    <!-- 小封面 -->
                    <div class="poster-thumbnail mr-4">
                      <v-img
                        v-if="item.poster_url"
                        :src="item.poster_url"
                        cover
                        width="48"
                        height="64"
                        class="rounded"
                      >
                        <template #placeholder>
                          <div class="d-flex align-center justify-center fill-height">
                            <v-icon icon="mdi-filmstrip" />
                          </div>
                        </template>
                      </v-img>
                      <div v-else class="poster-placeholder d-flex align-center justify-center">
                        <v-icon icon="mdi-filmstrip" />
                      </div>
                    </div>
                  </template>

                  <!-- 内容信息 -->
                  <div class="d-flex flex-column" style="width: 100%;">
                    <!-- 标题 -->
                    <div class="text-subtitle-2 font-weight-medium mb-2">
                      {{ formatEpisodeName(item.item_name) }}
                    </div>

                    <!-- 详细信息 -->
                    <div class="text-caption text-medium-emphasis">
                      <div class="mb-1">
                        <v-icon size="x-small" class="mr-1">mdi-account</v-icon>
                        {{ item.username }}
                      </div>
                      <div class="mb-1">
                        <v-icon size="x-small" class="mr-1">mdi-clock-outline</v-icon>
                        {{ formatDateTime(item.time) }}
                      </div>
                      <div v-if="item.duration_minutes" class="mb-1">
                        <v-icon size="x-small" class="mr-1">mdi-timer-outline</v-icon>
                        {{ formatDuration(item.duration_minutes * 60) }}
                      </div>
                    </div>
                  </div>

                  <!-- 右侧信息 -->
                  <template #append>
                    <div class="text-right text-caption text-medium-emphasis">
                      <div>{{ item.client }}</div>
                      <div class="mt-1">{{ item.device }}</div>
                    </div>
                  </template>
                </v-list-item>
              </v-list>
            </template>

            <!-- 默认：海报网格展示 -->
            <template v-else>
              <v-row dense>
                <v-col
                  v-for="(item, index) in itemsWithServerUrls"
                  :key="`poster-${item.item_id}-${item.time}-${index}`"
                  cols="4"
                  sm="3"
                  md="2"
                  lg="2"
                  xl="2"
                >
                  <PosterCard
                    :title="formatEpisodeName(item.item_name)"
                    :poster-url="item.poster_url"
                    :subtitle="`${item.username} · ${formatDateTime(item.time)}`"
                    @click="goToContentDetail(String(item.item_id))"
                  />
                </v-col>
              </v-row>
            </template>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Card, PosterCard } from '@/components/ui'
import { useServerStore, useFilterStore } from '@/stores'
import { statsApi } from '@/services'
import { formatDateTime, formatDuration, getPosterUrl } from '@/utils'
import type { RecentItem } from '@/types'

const router = useRouter()
const serverStore = useServerStore()
const filterStore = useFilterStore()

const loading = ref(false)
const historyItems = ref<RecentItem[]>([])
const searchInput = ref('')
const searchQuery = ref('')

// 是否在搜索状态
const isSearching = computed(() => !!searchQuery.value.trim())

// 给历史记录项的海报URL添加server_id和尺寸参数
const itemsWithServerUrls = computed(() => {
  return historyItems.value.map(item => ({
    ...item,
    poster_url: getPosterUrl(item.poster_url, serverStore.currentServer?.id, 720, 480)
  }))
})

// 格式化剧集名称（提取S01E02等信息）
function formatEpisodeName(name: string): string {
  if (!name) return ''

  // 如果包含 " - " 分隔符，提取剧集信息
  if (name.includes(' - ')) {
    const parts = name.split(' - ')
    const episodePart = parts[1]
    if (episodePart) {
      const match = episodePart.match(/s(\d+)e(\d+)/i)
      if (match && match[1] && match[2]) {
        const season = match[1]
        const episode = match[2]
        return `${parts[0]} S${season}E${episode}`
      }
    }
  }

  return name
}

// 获取播放历史
async function fetchHistory() {
  if (!serverStore.currentServer) return

  loading.value = true
  try {
    // 构建查询参数
    let params: any = {
      server_id: serverStore.currentServer.id,
      limit: isSearching.value ? 100 : 48,
    }

    if (isSearching.value) {
      // 搜索时：移除时间限制，使用全库范围
      params.search = searchQuery.value.trim()
    } else {
      // 默认：使用筛选器的时间范围
      params = {
        ...params,
        ...filterStore.buildQueryParams,
      }
    }

    const response = await statsApi.getRecent(params)
    historyItems.value = response.data.recent || []
  } catch (error) {
    console.error('Failed to fetch history:', error)
  } finally {
    loading.value = false
  }
}

// 执行搜索
function handleSearch() {
  searchQuery.value = searchInput.value
  fetchHistory()
}

// 清除搜索
function clearSearch() {
  searchInput.value = ''
  searchQuery.value = ''
  fetchHistory()
}

// 跳转到内容详情
function goToContentDetail(itemId: string) {
  router.push(`/content/${itemId}`)
}

// 监听服务器和筛选器变化（只在非搜索状态下）
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    if (!isSearching.value) {
      fetchHistory()
    }
  },
  { deep: true }
)

onMounted(() => {
  fetchHistory()
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
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.poster-thumbnail {
  width: 48px;
  height: 64px;
  flex-shrink: 0;
}

.poster-placeholder {
  width: 48px;
  height: 64px;
  background-color: rgb(var(--v-theme-surface-variant));
  border-radius: 4px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
