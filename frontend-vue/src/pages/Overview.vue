<template>
  <div class="page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">播放统计总览</h2>
        <p class="page-subtitle">
          实时监控媒体服务器播放数据
        </p>
      </div>
    </div>

    <!-- 正在播放 -->
    <NowPlaying />

    <!-- 骨架屏加载 -->
    <template v-if="loading">
      <v-row class="mb-6">
        <v-col v-for="i in 4" :key="i" cols="12" sm="6" md="3">
          <v-card class="stat-card">
            <v-skeleton-loader type="article" />
          </v-card>
        </v-col>
      </v-row>
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 数据展示 -->
    <template v-else-if="overviewData && trendData && hourlyData">
      <!-- 统计卡片 -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card pulse-card" hover>
            <v-card-text>
              <div class="stat-content">
                <div class="stat-icon" style="background: rgba(29, 78, 216, 0.1);">
                  <v-icon size="24" color="primary">mdi-play-circle</v-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">总播放次数</div>
                  <AnimatedNumber
                    :value="overviewData.total_plays"
                    class="stat-value text-primary"
                  />
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card pulse-card" hover>
            <v-card-text>
              <div class="stat-content">
                <div class="stat-icon" style="background: rgba(34, 197, 94, 0.1);">
                  <v-icon size="24" color="success">mdi-clock-outline</v-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">总播放时长</div>
                  <div class="stat-value text-success">
                    {{ overviewData.total_duration_hours.toFixed(1) }}h
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card pulse-card" hover>
            <v-card-text>
              <div class="stat-content">
                <div class="stat-icon" style="background: rgba(249, 115, 22, 0.1);">
                  <v-icon size="24" color="warning">mdi-account-group</v-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">活跃用户</div>
                  <AnimatedNumber
                    :value="overviewData.unique_users"
                    class="stat-value text-warning"
                  />
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card class="stat-card pulse-card" hover>
            <v-card-text>
              <div class="stat-content">
                <div class="stat-icon" style="background: rgba(239, 68, 68, 0.1);">
                  <v-icon size="24" color="error">mdi-filmstrip</v-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">观看内容数</div>
                  <AnimatedNumber
                    :value="overviewData.unique_items"
                    class="stat-value text-error"
                  />
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 趋势图表 -->
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card hover>
            <v-card-title class="card-header">
              <span>播放趋势</span>
              <v-icon>mdi-chart-line</v-icon>
            </v-card-title>
            <v-card-text>
              <TrendChart
                :data="trendData.trend"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 时段热力图 -->
      <v-row>
        <v-col cols="12">
          <v-card hover>
            <v-card-title class="card-header">
              <span>活跃时段分布</span>
              <v-icon>mdi-clock-time-four-outline</v-icon>
            </v-card-title>
            <v-card-text>
              <HeatmapChart
                :data="hourlyData.hourly"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- 空状态 -->
    <v-row v-else>
      <v-col cols="12">
        <v-alert type="info" variant="tonal">
          暂无统计数据
        </v-alert>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { AnimatedNumber } from '@/components/ui'
import { TrendChart, HeatmapChart } from '@/components/charts'
import NowPlaying from '@/components/NowPlaying.vue'
import { useServerStore, useFilterStore } from '@/stores'
import { statsApi } from '@/services'
import type { OverviewData, TrendData, HourlyData } from '@/types'

const serverStore = useServerStore()
const filterStore = useFilterStore()

const loading = ref(false)
const overviewData = ref<OverviewData | null>(null)
const trendData = ref<TrendData | null>(null)
const hourlyData = ref<HourlyData | null>(null)

// 获取所有概览数据
async function fetchOverviewData() {
  if (!serverStore.currentServer) return

  loading.value = true
  try {
    const params = {
      server_id: serverStore.currentServer.id,
      ...filterStore.buildQueryParams,
    }

    const [overviewRes, trendRes, hourlyRes] = await Promise.all([
      statsApi.getOverview(params),
      statsApi.getTrend(params),
      statsApi.getHourly(params),
    ])

    overviewData.value = overviewRes.data
    trendData.value = trendRes.data
    hourlyData.value = hourlyRes.data
  } catch (error) {
    console.error('Failed to fetch overview data:', error)
  } finally {
    loading.value = false
  }
}

// 监听服务器和筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    fetchOverviewData()
  },
  { deep: true }
)

onMounted(() => {
  fetchOverviewData()
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
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 统计卡片动画 */
.stat-card {
  cursor: pointer;
  animation: fadeInUp 0.5s ease backwards;
}

.pulse-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.pulse-card:hover {
  transform: translateY(-6px) scale(1.02);
}

/* 深色模式增强 - 适度蓝色边框 */
.v-theme--dark .pulse-card {
  border: 1px solid rgba(59, 130, 246, 0.15);
}

.v-theme--dark .pulse-card:hover {
  border-color: rgba(59, 130, 246, 0.35);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6) !important;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  transition: transform 0.3s ease;
}

.pulse-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  opacity: 0.7;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

/* 卡片标题 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
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

  .stat-value {
    font-size: 20px;
  }
}
</style>
