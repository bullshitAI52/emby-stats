<template>
  <div class="page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">用户统计</h2>
        <p class="page-subtitle">
          分析用户观看行为和偏好
        </p>
      </div>
    </div>

    <!-- 骨架屏加载 -->
    <template v-if="loading">
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 数据展示 -->
    <template v-else-if="usersData">
      <!-- 用户统计图表 -->
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card hover>
            <v-card-title class="card-header">
              <span>用户观看统计</span>
              <v-icon>mdi-chart-bar</v-icon>
            </v-card-title>
            <v-card-text>
              <UsersChart
                :data="usersData.users"
                :sort-by="sortBy"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 用户详细表格 -->
      <v-row>
        <v-col cols="12">
          <v-card hover>
            <v-card-title class="card-header">
              <span>用户详情</span>
              <v-select
                v-model="sortBy"
                :items="sortOptions"
                item-title="label"
                item-value="value"
                label="排序方式"
                density="compact"
                variant="outlined"
                hide-details
                style="max-width: 200px"
              />
            </v-card-title>
            <v-card-text>
              <!-- 桌面端表格 -->
              <v-table v-if="!mobile" density="comfortable">
                <thead>
                  <tr>
                    <th>用户名</th>
                    <th class="text-right">观看次数</th>
                    <th class="text-right">观看时长（小时）</th>
                    <th class="text-right">最后观看</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in sortedUsers" :key="user.username">
                    <td>
                      <div class="d-flex align-center">
                        <Avatar :name="user.username" size="32" class="mr-2" />
                        {{ user.username }}
                      </div>
                    </td>
                    <td class="text-right">{{ formatNumber(user.play_count) }}</td>
                    <td class="text-right">{{ user.duration_hours.toFixed(1) }}</td>
                    <td class="text-right">{{ user.last_play ? formatDate(user.last_play) : '-' }}</td>
                  </tr>
                </tbody>
              </v-table>

              <!-- 移动端卡片列表 -->
              <v-list v-else>
                <v-list-item
                  v-for="user in sortedUsers"
                  :key="user.username"
                  class="mb-2"
                >
                  <template #prepend>
                    <Avatar :name="user.username" size="48" class="mr-3" />
                  </template>
                  <v-list-item-title class="font-weight-medium mb-1">
                    {{ user.username }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <div class="d-flex flex-column">
                      <span>观看次数: {{ formatNumber(user.play_count) }}</span>
                      <span>观看时长: {{ user.duration_hours.toFixed(1) }} 小时</span>
                      <span>最后观看: {{ user.last_play ? formatDate(user.last_play) : '-' }}</span>
                    </div>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- 空状态 -->
    <v-row v-else>
      <v-col cols="12">
        <v-alert type="info" variant="tonal">
          暂无用户统计数据
        </v-alert>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useDisplay } from 'vuetify'
import { Card, Avatar } from '@/components/ui'
import { UsersChart } from '@/components/charts'
import { useServerStore, useFilterStore } from '@/stores'
import { statsApi } from '@/services'
import { formatDuration, formatDate, formatNumber } from '@/utils'
import type { UsersData } from '@/types'

const serverStore = useServerStore()
const filterStore = useFilterStore()
const { mobile } = useDisplay()

const loading = ref(false)
const usersData = ref<UsersData | null>(null)
const sortBy = ref<'play_count' | 'duration_hours'>('play_count')

const sortOptions = [
  { label: '观看次数', value: 'play_count' },
  { label: '观看时长', value: 'duration_hours' },
]

// 排序后的用户列表
const sortedUsers = computed(() => {
  if (!usersData.value?.users) return []

  return [...usersData.value.users].sort((a, b) => {
    return b[sortBy.value] - a[sortBy.value]
  })
})

// 获取用户统计数据
async function fetchUsersData() {
  if (!serverStore.currentServer) return

  loading.value = true
  try {
    const response = await statsApi.getUsers({
      server_id: serverStore.currentServer.id,
      ...filterStore.buildQueryParams,
    })
    usersData.value = response.data
  } catch (error) {
    console.error('Failed to fetch users data:', error)
  } finally {
    loading.value = false
  }
}

// 监听服务器和筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    fetchUsersData()
  },
  { deep: true }
)

onMounted(() => {
  fetchUsersData()
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
