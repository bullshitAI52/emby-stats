<template>
  <div class="page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">设备统计</h2>
        <p class="page-subtitle">
          了解客户端和设备的使用情况
        </p>
      </div>
    </div>

    <!-- 骨架屏加载 -->
    <template v-if="loading">
      <v-row class="mb-6">
        <v-col cols="12" md="6">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="table" /></v-card>
        </v-col>
      </v-row>
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 数据展示 -->
    <template v-else-if="devicesData">
      <!-- 客户端和设备分布图表 -->
      <v-row class="mb-6">
        <v-col cols="12" md="6">
          <v-card hover>
            <v-card-title class="card-header">
              <span>客户端分布</span>
              <v-icon>mdi-application</v-icon>
            </v-card-title>
            <v-card-text>
              <PieChart :data="clientsChartData" />
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card hover>
            <v-card-title class="card-header">
              <span>设备分布</span>
              <v-icon>mdi-monitor</v-icon>
            </v-card-title>
            <v-card-text>
              <PieChart :data="devicesChartData" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 客户端详细表格 -->
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card hover>
            <v-card-title class="card-header">
              <span>客户端详情</span>
              <v-icon>mdi-view-list</v-icon>
            </v-card-title>
            <v-card-text>
              <!-- 桌面端表格 -->
              <v-table v-if="!mobile" density="comfortable">
                <thead>
                  <tr>
                    <th>客户端</th>
                    <th class="text-right">观看次数</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="client in devicesData.clients" :key="client.client">
                    <td>
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-application" class="mr-2" />
                        {{ client.client }}
                      </div>
                    </td>
                    <td class="text-right">{{ formatNumber(client.play_count) }}</td>
                  </tr>
                </tbody>
              </v-table>

              <!-- 移动端卡片列表 -->
              <v-list v-else>
                <v-list-item
                  v-for="client in devicesData.clients"
                  :key="client.client"
                  class="mb-2"
                >
                  <template #prepend>
                    <v-icon icon="mdi-application" size="32" class="mr-3" />
                  </template>
                  <v-list-item-title class="font-weight-medium">
                    {{ client.client }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    观看次数: {{ formatNumber(client.play_count) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 设备详细表格 -->
      <v-row>
        <v-col cols="12">
          <v-card hover>
            <v-card-title class="card-header">
              <span>设备详情</span>
              <v-icon>mdi-view-list</v-icon>
            </v-card-title>
            <v-card-text>
              <!-- 桌面端表格 -->
              <v-table v-if="!mobile" density="comfortable">
                <thead>
                  <tr>
                    <th>设备</th>
                    <th class="text-right">观看次数</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="device in devicesData.devices" :key="device.device">
                    <td>
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-monitor" class="mr-2" />
                        {{ device.device }}
                      </div>
                    </td>
                    <td class="text-right">{{ formatNumber(device.play_count) }}</td>
                  </tr>
                </tbody>
              </v-table>

              <!-- 移动端卡片列表 -->
              <v-list v-else>
                <v-list-item
                  v-for="device in devicesData.devices"
                  :key="device.device"
                  class="mb-2"
                >
                  <template #prepend>
                    <v-icon icon="mdi-monitor" size="32" class="mr-3" />
                  </template>
                  <v-list-item-title class="font-weight-medium">
                    {{ device.device }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    观看次数: {{ formatNumber(device.play_count) }}
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
          暂无设备统计数据
        </v-alert>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useDisplay } from 'vuetify'
import { Card } from '@/components/ui'
import { PieChart } from '@/components/charts'
import { useServerStore, useFilterStore } from '@/stores'
import { statsApi } from '@/services'
import { formatDuration, formatNumber, formatPercentage } from '@/utils'

const { mobile } = useDisplay()

// 自定义类型
interface ClientData {
  client: string
  play_count: number
  total_duration?: number
  percentage?: number
}

interface DeviceData {
  device: string
  play_count: number
  total_duration?: number
  percentage?: number
}

interface DevicesData {
  clients: ClientData[]
  devices: DeviceData[]
}

const serverStore = useServerStore()
const filterStore = useFilterStore()

const loading = ref(false)
const devicesData = ref<DevicesData | null>(null)

// 客户端图表数据
const clientsChartData = computed(() => {
  if (!devicesData.value?.clients) return []

  return devicesData.value.clients.map((client: ClientData) => ({
    name: client.client,
    value: client.play_count,
  }))
})

// 设备图表数据
const devicesChartData = computed(() => {
  if (!devicesData.value?.devices) return []

  return devicesData.value.devices.map((device: DeviceData) => ({
    name: device.device,
    value: device.play_count,
  }))
})

// 获取设备统计数据
async function fetchDevicesData() {
  if (!serverStore.currentServer) return

  loading.value = true
  try {
    const [clientsResponse, devicesResponse] = await Promise.all([
      statsApi.getClients({
        server_id: serverStore.currentServer.id,
        ...filterStore.buildQueryParams,
      }),
      statsApi.getDevices({
        server_id: serverStore.currentServer.id,
        ...filterStore.buildQueryParams,
      }),
    ])

    devicesData.value = {
      clients: (clientsResponse.data.clients || []).map((c: any) => ({
        client: c.client,
        play_count: c.play_count,
        total_duration: c.total_duration,
        percentage: c.percentage,
      })),
      devices: (devicesResponse.data.devices || []).map((d: any) => ({
        device: d.device,
        play_count: d.play_count,
        total_duration: d.total_duration,
        percentage: d.percentage,
      })),
    }
  } catch (error) {
    console.error('Failed to fetch devices data:', error)
  } finally {
    loading.value = false
  }
}

// 监听服务器和筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    fetchDevicesData()
  },
  { deep: true }
)

onMounted(() => {
  fetchDevicesData()
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
  padding: 16px !important;
}

/* 确保卡片内容不与标题重叠 */
:deep(.v-card-text) {
  padding-top: 16px !important;
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
