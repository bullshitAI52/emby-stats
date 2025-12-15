<template>
  <div class="page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">内容统计</h2>
        <p class="page-subtitle">
          发现最受欢迎的内容和剧集
        </p>
      </div>
    </div>

    <!-- 热门内容 -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card hover>
          <v-card-title class="card-header">
            <span>热门内容</span>
            <v-icon>mdi-fire</v-icon>
          </v-card-title>
          <v-card-text>
            <!-- 加载状态 -->
            <div v-if="topContentLoading" class="d-flex justify-center align-center" style="min-height: 200px">
              <v-progress-circular indeterminate color="primary" size="48" />
            </div>

            <!-- 瀑布流海报展示 -->
            <v-row v-else-if="topContents.length > 0">
              <v-col
                v-for="(item, index) in topContents"
                :key="`top-content-${item.item_id}-${index}`"
                cols="6"
                sm="4"
                md="3"
                lg="2"
              >
                <PosterCard
                  :title="item.show_name || item.name"
                  :poster-url="item.poster_url"
                  :play-count="item.play_count"
                  :duration="item.duration_hours * 3600"
                  @click="goToContentDetail(item, true)"
                />
              </v-col>
            </v-row>

            <!-- 空状态 -->
            <div v-else class="text-center text-grey pa-8">
              暂无数据
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 播放排行 -->
    <v-row>
      <v-col cols="12">
        <v-card hover>
          <v-card-title class="card-header">
            <span>播放排行</span>
            <v-icon>mdi-trophy</v-icon>
          </v-card-title>
          <v-card-text>
            <!-- 加载状态 -->
            <div v-if="contentLoading" class="d-flex justify-center align-center" style="min-height: 200px">
              <v-progress-circular indeterminate color="primary" size="48" />
            </div>

            <!-- 排行榜列表 -->
            <div v-else-if="contents.length > 0" class="ranking-list">
              <div
                v-for="(item, index) in contents"
                :key="`content-${item.item_id}-${index}`"
                class="ranking-item"
                @click="goToContentDetail(item, false)"
              >
                <!-- 排名 -->
                <div class="ranking-number" :class="`rank-${index + 1}`">
                  {{ index + 1 }}
                </div>

                <!-- 海报 -->
                <div class="ranking-poster">
                  <img
                    v-if="item.poster_url"
                    :src="item.poster_url"
                    :alt="item.show_name || item.name"
                    class="poster-img"
                  />
                  <div v-else class="poster-placeholder">
                    <v-icon icon="mdi-image-off" size="32" />
                  </div>
                </div>

                <!-- 内容信息 -->
                <div class="ranking-info">
                  <div class="ranking-title">
                    {{ item.show_name || item.name }}
                  </div>
                  <div class="ranking-meta">
                    <v-chip size="x-small" color="primary" class="mr-2">
                      <v-icon icon="mdi-play-circle" size="12" class="mr-1" />
                      {{ item.play_count }} 次
                    </v-chip>
                    <v-chip size="x-small" color="secondary">
                      <v-icon icon="mdi-clock-outline" size="12" class="mr-1" />
                      {{ formatDuration(item.duration_hours * 3600) }}
                    </v-chip>
                  </div>
                </div>

                <!-- 箭头 -->
                <div class="ranking-arrow">
                  <v-icon icon="mdi-chevron-right" />
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-else class="text-center text-grey pa-8">
              暂无数据
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, PosterCard } from '@/components/ui'
import { useServerStore, useFilterStore } from '@/stores'
import { statsApi } from '@/services'
import { formatDuration } from '@/utils'

const router = useRouter()
const serverStore = useServerStore()
const filterStore = useFilterStore()

const topContentLoading = ref(false)
const contentLoading = ref(false)
const topContents = ref<any[]>([])
const contents = ref<any[]>([])

// 获取热门内容（包括剧集和电影）
async function fetchTopContent() {
  if (!serverStore.currentServer) return

  topContentLoading.value = true
  try {
    const params = {
      server_id: serverStore.currentServer.id,
      ...filterStore.buildQueryParams,
      limit: 16,
    }

    const response = await statsApi.getTopContent(params)
    topContents.value = response.data.top_content || []
  } catch (error) {
    console.error('Failed to fetch top content:', error)
  } finally {
    topContentLoading.value = false
  }
}

// 获取播放排行
async function fetchPlayRankings() {
  if (!serverStore.currentServer) return

  contentLoading.value = true
  try {
    const params = {
      server_id: serverStore.currentServer.id,
      ...filterStore.buildQueryParams,
      limit: 18,
    }

    const response = await statsApi.getTopContent(params)
    contents.value = response.data.top_content || []
  } catch (error) {
    console.error('Failed to fetch play rankings:', error)
  } finally {
    contentLoading.value = false
  }
}

// 跳转到内容详情
function goToContentDetail(item: any, isShowsCard: boolean) {
  // 热门剧集和播放排行都直接跳转，后端已经返回正确的 ID
  router.push({
    path: `/content/${item.item_id}`,
    query: { name: item.show_name }
  })
}

// 监听服务器和筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    fetchTopContent()
    fetchPlayRankings()
  },
  { deep: true }
)

onMounted(() => {
  fetchTopContent()
  fetchPlayRankings()
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

/* 排行榜样式 */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ranking-item:hover {
  background: rgba(var(--v-theme-surface-variant), 0.5);
  transform: translateX(4px);
}

.ranking-number {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  border-radius: 8px;
  background: rgba(var(--v-theme-primary), 0.15);
  color: rgb(var(--v-theme-primary));
}

.ranking-number.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #000;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

.ranking-number.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #000;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.4);
}

.ranking-number.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
  color: #000;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.4);
}

.ranking-poster {
  flex-shrink: 0;
  width: 60px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
}

.poster-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.3;
}

.ranking-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-title {
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ranking-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.ranking-arrow {
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.ranking-item:hover .ranking-arrow {
  opacity: 1;
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

  .ranking-number {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .ranking-poster {
    width: 50px;
    height: 75px;
  }

  .ranking-title {
    font-size: 14px;
  }
}
</style>
