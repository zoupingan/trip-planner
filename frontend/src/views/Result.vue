<template>
  <main class="result-page">
    <header class="result-nav">
      <a-button class="back-button" size="large" @click="goBack">
        返回首页
      </a-button>

      <div class="result-actions">
        <a-button v-if="!editMode" @click="toggleEditMode" type="default">
          编辑行程
        </a-button>
        <a-button v-else @click="saveChanges" type="primary">
          保存修改
        </a-button>
        <a-button v-if="editMode" @click="cancelEdit" type="default">
          取消编辑
        </a-button>

        <a-dropdown v-if="!editMode">
          <template #overlay>
            <a-menu>
              <a-menu-item key="image" @click="exportAsImage">导出为图片</a-menu-item>
              <a-menu-item key="pdf" @click="exportAsPDF">导出为 PDF</a-menu-item>
            </a-menu>
          </template>
          <a-button type="default">
            导出行程 <DownOutlined />
          </a-button>
        </a-dropdown>
      </div>
    </header>

    <div v-if="tripPlan" class="result-shell">
      <aside class="side-nav">
        <a-affix :offset-top="96">
          <a-menu mode="inline" :selected-keys="[activeSection]" @click="scrollToSection">
            <a-menu-item key="overview">行程概览</a-menu-item>
            <a-menu-item key="budget" v-if="tripPlan.budget">预算明细</a-menu-item>
            <a-menu-item key="map">景点地图</a-menu-item>
            <a-sub-menu key="days" title="每日行程">
              <a-menu-item v-for="(_, index) in tripPlan.days" :key="`day-${index}`">
                第{{ index + 1 }}天
              </a-menu-item>
            </a-sub-menu>
            <a-menu-item key="weather" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0">
              天气信息
            </a-menu-item>
          </a-menu>
        </a-affix>
      </aside>

      <section class="main-content">
        <section id="overview" class="overview-hero">
          <div>
            <p class="eyebrow">旅行计划</p>
            <h1>{{ tripPlan.city }}</h1>
            <p class="date-range">{{ tripPlan.start_date }} 至 {{ tripPlan.end_date }}</p>
          </div>
          <p class="overview-suggestion">{{ tripPlan.overall_suggestions }}</p>
        </section>

        <section class="content-map-grid">
          <div class="planning-column">
            <section id="budget" v-if="tripPlan.budget" class="budget-panel">
              <div class="section-heading">
                <p>预算明细</p>
                <h2>费用预估</h2>
              </div>
              <div class="budget-grid">
                <div class="budget-item">
                  <span>景点门票</span>
                  <strong>¥{{ tripPlan.budget.total_attractions }}</strong>
                </div>
                <div class="budget-item">
                  <span>酒店住宿</span>
                  <strong>¥{{ tripPlan.budget.total_hotels }}</strong>
                </div>
                <div class="budget-item">
                  <span>餐饮费用</span>
                  <strong>¥{{ tripPlan.budget.total_meals }}</strong>
                </div>
                <div class="budget-item">
                  <span>交通费用</span>
                  <strong>¥{{ tripPlan.budget.total_transportation }}</strong>
                </div>
              </div>
              <div class="budget-total">
                <span>预估总费用</span>
                <strong>¥{{ tripPlan.budget.total }}</strong>
              </div>
            </section>

            <section class="days-section">
              <div class="section-heading">
                <p>每日行程</p>
                <h2>路线安排</h2>
              </div>

              <a-collapse v-model:activeKey="activeDays" accordion>
                <a-collapse-panel
                  v-for="(day, dayIndex) in tripPlan.days"
                  :key="dayIndex"
                  :id="`day-${dayIndex}`"
                >
                  <template #header>
                    <div class="day-header">
                      <span>第{{ dayIndex + 1 }}天</span>
                      <strong>{{ day.date }}</strong>
                    </div>
                  </template>

                  <div class="day-info">
                    <div class="info-row">
                      <span>行程描述</span>
                      <p>{{ day.description }}</p>
                    </div>
                    <div class="info-row">
                      <span>交通方式</span>
                      <p>{{ day.transportation }}</p>
                    </div>
                    <div class="info-row">
                      <span>住宿</span>
                      <p>{{ day.accommodation }}</p>
                    </div>
                  </div>

                  <div class="subsection-title">景点安排</div>
                  <a-list :data-source="day.attractions" :grid="{ gutter: 18, column: 2 }">
                    <template #renderItem="{ item, index }">
                      <a-list-item>
                        <a-card :title="item.name" size="small" class="attraction-card">
                          <template #extra v-if="editMode">
                            <a-space>
                              <a-button
                                size="small"
                                @click="moveAttraction(dayIndex, index, 'up')"
                                :disabled="index === 0"
                              >
                                上移
                              </a-button>
                              <a-button
                                size="small"
                                @click="moveAttraction(dayIndex, index, 'down')"
                                :disabled="index === day.attractions.length - 1"
                              >
                                下移
                              </a-button>
                              <a-button
                                size="small"
                                danger
                                @click="deleteAttraction(dayIndex, index)"
                              >
                                删除
                              </a-button>
                            </a-space>
                          </template>

                          <div class="attraction-image-wrapper">
                            <img
                              :src="getAttractionImage(item.name, index)"
                              :alt="item.name"
                              class="attraction-image"
                              @error="handleImageError"
                            />
                            <div class="attraction-badge">
                              <span class="badge-number">{{ index + 1 }}</span>
                            </div>
                            <div v-if="item.ticket_price" class="price-tag">
                              ¥{{ item.ticket_price }}
                            </div>
                          </div>

                          <div v-if="editMode" class="edit-fields">
                            <p><strong>地址:</strong></p>
                            <a-input v-model:value="item.address" size="small" style="margin-bottom: 8px" />

                            <p><strong>游览时长(分钟):</strong></p>
                            <a-input-number v-model:value="item.visit_duration" :min="10" :max="480" size="small" style="width: 100%; margin-bottom: 8px" />

                            <p><strong>描述:</strong></p>
                            <a-textarea v-model:value="item.description" :rows="2" size="small" style="margin-bottom: 8px" />
                          </div>

                          <div v-else class="attraction-copy">
                            <p><strong>地址:</strong> {{ item.address }}</p>
                            <p><strong>游览时长:</strong> {{ item.visit_duration }}分钟</p>
                            <p><strong>描述:</strong> {{ item.description }}</p>
                            <p v-if="item.rating"><strong>评分:</strong> {{ item.rating }} / 5</p>
                          </div>
                        </a-card>
                      </a-list-item>
                    </template>
                  </a-list>

                  <template v-if="day.hotel">
                    <div class="subsection-title">住宿推荐</div>
                    <a-card size="small" class="hotel-card">
                      <template #title>
                        <span class="hotel-title">{{ day.hotel.name }}</span>
                      </template>
                      <a-descriptions :column="2" size="small">
                        <a-descriptions-item label="地址">{{ day.hotel.address }}</a-descriptions-item>
                        <a-descriptions-item label="类型">{{ day.hotel.type }}</a-descriptions-item>
                        <a-descriptions-item label="价格范围">{{ day.hotel.price_range }}</a-descriptions-item>
                        <a-descriptions-item label="评分">{{ day.hotel.rating }} / 5</a-descriptions-item>
                        <a-descriptions-item label="距离" :span="2">{{ day.hotel.distance }}</a-descriptions-item>
                      </a-descriptions>
                    </a-card>
                  </template>

                  <div class="subsection-title">餐饮安排</div>
                  <a-descriptions :column="1" bordered size="small">
                    <a-descriptions-item
                      v-for="meal in day.meals"
                      :key="meal.type"
                      :label="getMealLabel(meal.type)"
                    >
                      {{ meal.name }}
                      <span v-if="meal.description"> - {{ meal.description }}</span>
                    </a-descriptions-item>
                  </a-descriptions>
                </a-collapse-panel>
              </a-collapse>
            </section>

            <section id="weather" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0" class="weather-panel">
              <div class="section-heading">
                <p>天气信息</p>
                <h2>出行天气</h2>
              </div>
              <a-list :data-source="tripPlan.weather_info" :grid="{ gutter: 16, column: 3 }">
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-card size="small" class="weather-card">
                      <div class="weather-date">{{ item.date }}</div>
                      <div class="weather-info-row">
                        <span>白天</span>
                        <strong>{{ item.day_weather }} {{ item.day_temp }}°C</strong>
                      </div>
                      <div class="weather-info-row">
                        <span>夜间</span>
                        <strong>{{ item.night_weather }} {{ item.night_temp }}°C</strong>
                      </div>
                      <div class="weather-wind">
                        {{ item.wind_direction }} {{ item.wind_power }}
                      </div>
                    </a-card>
                  </a-list-item>
                </template>
              </a-list>
            </section>
          </div>

          <aside id="map" class="map-rail">
            <div class="map-panel">
              <div class="map-heading">
                <p>景点地图</p>
                <h2>路线位置</h2>
              </div>
              <div id="amap-container"></div>
            </div>
          </aside>
        </section>
      </section>
    </div>

    <a-empty v-else description="没有找到旅行计划数据" class="empty-state">
      <template #description>
        <span>暂无旅行计划数据,请先创建行程</span>
      </template>
      <a-button type="primary" @click="goBack">返回首页创建行程</a-button>
    </a-empty>

    <a-back-top :visibility-height="300">
      <div class="back-top-button">
        ↑
      </div>
    </a-back-top>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownOutlined } from '@ant-design/icons-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { TripPlan } from '@/types'

const router = useRouter()
const tripPlan = ref<TripPlan | null>(null)
const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const attractionPhotos = ref<Record<string, string>>({})
const activeSection = ref('overview')
const activeDays = ref<number[]>([0]) // 默认展开第一天
let map: any = null

onMounted(async () => {
  const data = sessionStorage.getItem('tripPlan')
  if (data) {
    tripPlan.value = JSON.parse(data)
    // 加载景点图片
    await loadAttractionPhotos()
    // 等待DOM渲染完成后初始化地图
    await nextTick()
    initMap()
  }
})

const goBack = () => {
  router.push('/')
}

// 滚动到指定区域
const scrollToSection = ({ key }: { key: string }) => {
  activeSection.value = key
  const element = document.getElementById(key)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 切换编辑模式
const toggleEditMode = () => {
  editMode.value = true
  // 保存原始数据用于取消编辑
  originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  message.info('进入编辑模式')
}

// 保存修改
const saveChanges = () => {
  editMode.value = false
  // 更新sessionStorage
  if (tripPlan.value) {
    sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.value))
  }
  message.success('修改已保存')

  // 重新初始化地图以反映更改
  if (map) {
    map.destroy()
  }
  nextTick(() => {
    initMap()
  })
}

// 取消编辑
const cancelEdit = () => {
  if (originalPlan.value) {
    tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
  }
  editMode.value = false
  message.info('已取消编辑')
}

// 删除景点
const deleteAttraction = (dayIndex: number, attrIndex: number) => {
  if (!tripPlan.value) return

  const day = tripPlan.value.days[dayIndex]
  if (day.attractions.length <= 1) {
    message.warning('每天至少需要保留一个景点')
    return
  }

  day.attractions.splice(attrIndex, 1)
  message.success('景点已删除')
}

// 移动景点顺序
const moveAttraction = (dayIndex: number, attrIndex: number, direction: 'up' | 'down') => {
  if (!tripPlan.value) return

  const day = tripPlan.value.days[dayIndex]
  const attractions = day.attractions

  if (direction === 'up' && attrIndex > 0) {
    [attractions[attrIndex], attractions[attrIndex - 1]] = [attractions[attrIndex - 1], attractions[attrIndex]]
  } else if (direction === 'down' && attrIndex < attractions.length - 1) {
    [attractions[attrIndex], attractions[attrIndex + 1]] = [attractions[attrIndex + 1], attractions[attrIndex]]
  }
}

const getMealLabel = (type: string): string => {
  const labels: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '小吃'
  }
  return labels[type] || type
}

// 加载所有景点图片
const loadAttractionPhotos = async () => {
  if (!tripPlan.value) return

  const promises: Promise<void>[] = []
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  tripPlan.value.days.forEach(day => {
    day.attractions.forEach(attraction => {
      const promise = fetch(`${API_BASE_URL}/api/poi/photo?name=${encodeURIComponent(attraction.name)}`)
        .then(res => res.json())
        .then(data => {
          if (data.success && data.data.photo_url) {
            attractionPhotos.value[attraction.name] = data.data.photo_url
          }
        })
        .catch(err => {
          console.error(`获取${attraction.name}图片失败:`, err)
        })

      promises.push(promise)
    })
  })

  await Promise.all(promises)
}

// 获取景点图片
const getAttractionImage = (name: string, index: number): string => {
  // 如果已加载真实图片,返回真实图片
  if (attractionPhotos.value[name]) {
    return attractionPhotos.value[name]
  }

  // 返回一个纯色占位图(避免跨域问题)
  const colors = [
    { start: '#667eea', end: '#764ba2' },
    { start: '#f093fb', end: '#f5576c' },
    { start: '#4facfe', end: '#00f2fe' },
    { start: '#43e97b', end: '#38f9d7' },
    { start: '#fa709a', end: '#fee140' }
  ]
  const colorIndex = index % colors.length
  const { start, end } = colors[colorIndex]

  // 使用base64编码避免中文问题
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
    <defs>
      <linearGradient id="grad${index}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${start};stop-opacity:1" />
        <stop offset="100%" style="stop-color:${end};stop-opacity:1" />
      </linearGradient>
    </defs>
    <rect width="400" height="300" fill="url(#grad${index})"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="bold" fill="white">${name}</text>
  </svg>`

  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
}

// 图片加载失败时的处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  // 使用灰色占位图
  img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="18" fill="%23999"%3E图片加载失败%3C/text%3E%3C/svg%3E'
}



// 导出为图片
const exportAsImage = async () => {
  try {
    message.loading({ content: '正在生成图片...', key: 'export', duration: 0 })

    const element = document.querySelector('.main-content') as HTMLElement
    if (!element) {
      throw new Error('未找到内容元素')
    }

    // 创建一个独立的容器
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#f5f7fa'
    exportContainer.style.padding = '20px'

    // 复制所有内容
    exportContainer.innerHTML = element.innerHTML

    // 处理地图截图
    const mapContainer = document.getElementById('amap-container')
    if (mapContainer && map) {
      const mapCanvas = mapContainer.querySelector('canvas')
      if (mapCanvas) {
        const mapSnapshot = mapCanvas.toDataURL('image/png')
        const exportMapContainer = exportContainer.querySelector('#amap-container')
        if (exportMapContainer) {
          exportMapContainer.innerHTML = `<img src="${mapSnapshot}" style="width:100%;height:100%;object-fit:cover;" />`
        }
      }
    }

    // 移除所有ant-card类,替换为纯div
    const cards = exportContainer.querySelectorAll('.ant-card')
    cards.forEach((card) => {
      const cardEl = card as HTMLElement
      try {
        cardEl.className = '' // 移除所有类
        cardEl.style.setProperty('background-color', '#ffffff')
        cardEl.style.setProperty('border-radius', '12px')
        cardEl.style.setProperty('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.1)')
        cardEl.style.setProperty('margin-bottom', '20px')
        cardEl.style.setProperty('overflow', 'hidden')
      } catch (err) {
        console.error('设置卡片样式失败:', err)
      }
    })

    // 处理卡片头部
    const cardHeads = exportContainer.querySelectorAll('.ant-card-head')
    cardHeads.forEach((head) => {
      const headEl = head as HTMLElement
      try {
        headEl.style.setProperty('background-color', '#667eea')
        headEl.style.setProperty('color', '#ffffff')
        headEl.style.setProperty('padding', '16px 24px')
        headEl.style.setProperty('font-size', '18px')
        headEl.style.setProperty('font-weight', '600')
      } catch (err) {
        console.error('设置卡片头部样式失败:', err)
      }
    })

    // 处理卡片内容
    const cardBodies = exportContainer.querySelectorAll('.ant-card-body')
    cardBodies.forEach((body) => {
      const bodyEl = body as HTMLElement
      bodyEl.style.setProperty('background-color', '#ffffff')
      bodyEl.style.setProperty('padding', '24px')
    })

    // 处理酒店卡片头部
    const hotelCards = exportContainer.querySelectorAll('.hotel-card')
    hotelCards.forEach((card) => {
      const head = card.querySelector('.ant-card-head') as HTMLElement
      if (head) {
        head.style.setProperty('background-color', '#1976d2')
      }
      (card as HTMLElement).style.setProperty('background-color', '#e3f2fd')
    })

    // 处理天气卡片
    const weatherCards = exportContainer.querySelectorAll('.weather-card')
    weatherCards.forEach((card) => {
      (card as HTMLElement).style.setProperty('background-color', '#e0f7fa')
    })

    // 处理预算总计
    const budgetTotal = exportContainer.querySelector('.budget-total')
    if (budgetTotal) {
      const el = budgetTotal as HTMLElement
      el.style.setProperty('background-color', '#667eea')
      el.style.setProperty('color', '#ffffff')
      el.style.setProperty('padding', '20px')
      el.style.setProperty('border-radius', '12px')
      el.style.setProperty('margin-bottom', '20px')
    }

    // 处理预算项
    const budgetItems = exportContainer.querySelectorAll('.budget-item')
    budgetItems.forEach((item) => {
      const el = item as HTMLElement
      el.style.setProperty('background-color', '#f5f7fa')
      el.style.setProperty('padding', '16px')
      el.style.setProperty('border-radius', '8px')
      el.style.setProperty('margin-bottom', '12px')
    })

    // 添加到body(隐藏)
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)

    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f5f7fa',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    // 移除容器
    document.body.removeChild(exportContainer)

    // 转换为图片并下载
    const link = document.createElement('a')
    link.download = `旅行计划_${tripPlan.value?.city}_${new Date().getTime()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()

    message.success({ content: '图片导出成功!', key: 'export' })
  } catch (error: any) {
    console.error('导出图片失败:', error)
    message.error({ content: `导出图片失败: ${error.message}`, key: 'export' })
  }
}

// 导出为PDF
const exportAsPDF = async () => {
  try {
    message.loading({ content: '正在生成PDF...', key: 'export', duration: 0 })

    const element = document.querySelector('.main-content') as HTMLElement
    if (!element) {
      throw new Error('未找到内容元素')
    }

    // 创建一个独立的容器
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#f5f7fa'
    exportContainer.style.padding = '20px'

    // 复制所有内容
    exportContainer.innerHTML = element.innerHTML

    // 处理地图截图
    const mapContainer = document.getElementById('amap-container')
    if (mapContainer && map) {
      const mapCanvas = mapContainer.querySelector('canvas')
      if (mapCanvas) {
        const mapSnapshot = mapCanvas.toDataURL('image/png')
        const exportMapContainer = exportContainer.querySelector('#amap-container')
        if (exportMapContainer) {
          exportMapContainer.innerHTML = `<img src="${mapSnapshot}" style="width:100%;height:100%;object-fit:cover;" />`
        }
      }
    }

    // 移除所有ant-card类,替换为纯div
    const cards = exportContainer.querySelectorAll('.ant-card')
    cards.forEach((card) => {
      const cardEl = card as HTMLElement
      try {
        cardEl.className = ''
        cardEl.style.setProperty('background-color', '#ffffff')
        cardEl.style.setProperty('border-radius', '12px')
        cardEl.style.setProperty('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.1)')
        cardEl.style.setProperty('margin-bottom', '20px')
        cardEl.style.setProperty('overflow', 'hidden')
      } catch (err) {
        console.error('设置卡片样式失败:', err)
      }
    })

    // 处理卡片头部
    const cardHeads = exportContainer.querySelectorAll('.ant-card-head')
    cardHeads.forEach((head) => {
      const headEl = head as HTMLElement
      try {
        headEl.style.setProperty('background-color', '#667eea')
        headEl.style.setProperty('color', '#ffffff')
        headEl.style.setProperty('padding', '16px 24px')
        headEl.style.setProperty('font-size', '18px')
        headEl.style.setProperty('font-weight', '600')
      } catch (err) {
        console.error('设置卡片头部样式失败:', err)
      }
    })

    // 处理卡片内容
    const cardBodies = exportContainer.querySelectorAll('.ant-card-body')
    cardBodies.forEach((body) => {
      const bodyEl = body as HTMLElement
      bodyEl.style.setProperty('background-color', '#ffffff')
      bodyEl.style.setProperty('padding', '24px')
    })

    // 处理酒店卡片头部
    const hotelCards = exportContainer.querySelectorAll('.hotel-card')
    hotelCards.forEach((card) => {
      const head = card.querySelector('.ant-card-head') as HTMLElement
      if (head) {
        head.style.setProperty('background-color', '#1976d2')
      }
      (card as HTMLElement).style.setProperty('background-color', '#e3f2fd')
    })

    // 处理天气卡片
    const weatherCards = exportContainer.querySelectorAll('.weather-card')
    weatherCards.forEach((card) => {
      (card as HTMLElement).style.setProperty('background-color', '#e0f7fa')
    })

    // 处理预算总计
    const budgetTotal = exportContainer.querySelector('.budget-total')
    if (budgetTotal) {
      const el = budgetTotal as HTMLElement
      el.style.setProperty('background-color', '#667eea')
      el.style.setProperty('color', '#ffffff')
      el.style.setProperty('padding', '20px')
      el.style.setProperty('border-radius', '12px')
      el.style.setProperty('margin-bottom', '20px')
    }

    // 处理预算项
    const budgetItems = exportContainer.querySelectorAll('.budget-item')
    budgetItems.forEach((item) => {
      const el = item as HTMLElement
      el.style.setProperty('background-color', '#f5f7fa')
      el.style.setProperty('padding', '16px')
      el.style.setProperty('border-radius', '8px')
      el.style.setProperty('margin-bottom', '12px')
    })

    // 添加到body(隐藏)
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)

    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f5f7fa',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    // 移除容器
    document.body.removeChild(exportContainer)

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const imgWidth = 210 // A4宽度(mm)
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    // 如果内容高度超过一页,分页处理
    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= 297 // A4高度

    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= 297
    }

    pdf.save(`旅行计划_${tripPlan.value?.city}_${new Date().getTime()}.pdf`)

    message.success({ content: 'PDF导出成功!', key: 'export' })
  } catch (error: any) {
    console.error('导出PDF失败:', error)
    message.error({ content: `导出PDF失败: ${error.message}`, key: 'export' })
  }
}

// 初始化地图
const initMap = async () => {
  try {
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY,  // 高德地图Web端(JS API) Key
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.InfoWindow']
    })

    // 创建地图实例
    map = new AMap.Map('amap-container', {
      zoom: 12,
      center: [116.397128, 39.916527], // 默认中心点(北京)
      viewMode: '3D'
    })

    // 添加景点标记
    addAttractionMarkers(AMap)

    message.success('地图加载成功')
  } catch (error) {
    console.error('地图加载失败:', error)
    message.error('地图加载失败')
  }
}

// 添加景点标记
const addAttractionMarkers = (AMap: any) => {
  if (!tripPlan.value) return

  const markers: any[] = []
  const allAttractions: any[] = []

  // 收集所有景点
  tripPlan.value.days.forEach((day, dayIndex) => {
    day.attractions.forEach((attraction, attrIndex) => {
      if (attraction.location && attraction.location.longitude && attraction.location.latitude) {
        allAttractions.push({
          ...attraction,
          dayIndex,
          attrIndex
        })
      }
    })
  })

  // 创建标记
  allAttractions.forEach((attraction, index) => {
    const marker = new AMap.Marker({
      position: [attraction.location.longitude, attraction.location.latitude],
      title: attraction.name,
      label: {
        content: `<div style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">${index + 1}</div>`,
        offset: new AMap.Pixel(0, -30)
      }
    })

    // 创建信息窗口
    const infoWindow = new AMap.InfoWindow({
      content: `
        <div style="padding: 10px;">
          <h4 style="margin: 0 0 8px 0;">${attraction.name}</h4>
          <p style="margin: 4px 0;"><strong>地址:</strong> ${attraction.address}</p>
          <p style="margin: 4px 0;"><strong>游览时长:</strong> ${attraction.visit_duration}分钟</p>
          <p style="margin: 4px 0;"><strong>描述:</strong> ${attraction.description}</p>
          <p style="margin: 4px 0; color: #1890ff;"><strong>第${attraction.dayIndex + 1}天 景点${attraction.attrIndex + 1}</strong></p>
        </div>
      `,
      offset: new AMap.Pixel(0, -30)
    })

    // 点击标记显示信息窗口
    marker.on('click', () => {
      infoWindow.open(map, marker.getPosition())
    })

    markers.push(marker)
  })

  // 添加标记到地图
  map.add(markers)

  // 自动调整视野以包含所有标记
  if (allAttractions.length > 0) {
    map.setFitView(markers)
  }

  // 绘制路线
  drawRoutes(AMap, allAttractions)
}

// 绘制路线
const drawRoutes = (AMap: any, attractions: any[]) => {
  if (attractions.length < 2) return

  // 按天分组绘制路线
  const dayGroups: any = {}
  attractions.forEach(attr => {
    if (!dayGroups[attr.dayIndex]) {
      dayGroups[attr.dayIndex] = []
    }
    dayGroups[attr.dayIndex].push(attr)
  })

  // 为每天的景点绘制路线
  Object.values(dayGroups).forEach((dayAttractions: any) => {
    if (dayAttractions.length < 2) return

    const path = dayAttractions.map((attr: any) => [
      attr.location.longitude,
      attr.location.latitude
    ])

    const polyline = new AMap.Polyline({
      path: path,
      strokeColor: '#1890ff',
      strokeWeight: 4,
      strokeOpacity: 0.8,
      strokeStyle: 'solid',
      showDir: true // 显示方向箭头
    })

    map.add(polyline)
  })
}
</script>

<style scoped>
.result-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px 20px;
}

.page-header {
  max-width: 1200px;
  margin: 0 auto 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: fadeInDown 0.6s ease-out;
}

.back-button {
  border-radius: 8px;
  font-weight: 500;
}

/* 内容布局 */
.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
}

.side-nav {
  width: 240px;
  flex-shrink: 0;
}

.side-nav :deep(.ant-menu) {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background: white;
}

.side-nav :deep(.ant-menu-item) {
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.side-nav :deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.side-nav :deep(.ant-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
}

.main-content {
  flex: 1;
  min-width: 0;
}

/* 景点图片样式 */
.attraction-image-wrapper {
  position: relative;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.attraction-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.attraction-image-wrapper:hover .attraction-image {
  transform: scale(1.05);
}

.attraction-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.badge-number {
  font-size: 18px;
}

.price-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 77, 79, 0.9);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 天气卡片样式 */
.weather-card {
  background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
  border: none !important;
  transition: all 0.3s ease;
}

.weather-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.weather-date {
  font-size: 16px;
  font-weight: bold;
  color: #00796b;
  margin-bottom: 12px;
  text-align: center;
}

.weather-info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.weather-icon {
  font-size: 24px;
}

.weather-label {
  font-size: 12px;
  color: #666;
}

.weather-value {
  font-size: 16px;
  font-weight: 600;
  color: #00796b;
}

.weather-wind {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 121, 107, 0.2);
  text-align: center;
  color: #00796b;
  font-size: 14px;
}

/* 回到顶部按钮 */
.back-top-button {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-top-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

/* 酒店卡片样式 */
.hotel-card {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: none !important;
}

.hotel-card :deep(.ant-card-head) {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
}

.hotel-title {
  color: white !important;
  font-weight: 600;
}

/* 顶部信息区布局 */
.top-info-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.left-info {
  flex: 0 0 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-map {
  flex: 1;
}

/* 行程概览卡片 */
.overview-card {
  height: fit-content;
}

.overview-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.info-value {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
}

/* 预算卡片 */
.budget-card {
  height: fit-content;
}

.budget-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.budget-item {
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.budget-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.budget-value {
  font-size: 20px;
  font-weight: 700;
  color: #1890ff;
}

.budget-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.total-label {
  font-size: 16px;
  font-weight: 600;
}

.total-value {
  font-size: 28px;
  font-weight: 700;
}

/* 地图卡片 */
.map-card {
  height: 100%;
  min-height: 500px;
}

.map-card :deep(.ant-card-body) {
  height: calc(100% - 57px);
  padding: 0;
}

/* 每日行程卡片 */
.days-card {
  margin-top: 20px;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.day-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.day-date {
  font-size: 14px;
  color: #999;
}

.day-info {
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
}

.info-row .value {
  color: #333;
  flex: 1;
}

/* 卡片样式优化 */
:deep(.ant-card) {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out;
}

:deep(.ant-card:hover) {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

:deep(.ant-card-head) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  border-radius: 12px 12px 0 0;
  font-weight: 600;
}

:deep(.ant-card-head-title) {
  color: white !important;
  font-size: 18px;
}

:deep(.ant-card-head-title span) {
  color: white !important;
}

/* Collapse样式 */
:deep(.ant-collapse) {
  border: none;
  background: transparent;
}

:deep(.ant-collapse-item) {
  margin-bottom: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

:deep(.ant-collapse-header) {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  padding: 16px 20px !important;
  font-weight: 600;
}

:deep(.ant-collapse-content) {
  border-top: 1px solid #e8e8e8;
}

:deep(.ant-collapse-content-box) {
  padding: 20px;
}

/* 统计卡片样式 */
:deep(.ant-statistic-title) {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

:deep(.ant-statistic-content) {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
}

/* 景点卡片样式 */
:deep(.ant-list-item) {
  transition: all 0.3s ease;
}

:deep(.ant-list-item:hover) {
  transform: scale(1.02);
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

/* 响应式设计 */
@media (max-width: 768px) {
  .result-container {
    padding: 20px 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }
}

/* New studio result theme */
.result-page {
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  padding: 28px;
  background:
    radial-gradient(circle at 18% 8%, rgba(14, 165, 233, 0.16), transparent 30%),
    radial-gradient(circle at 88% 16%, rgba(249, 115, 22, 0.12), transparent 26%),
    linear-gradient(135deg, #f8fafc 0%, #eef4f8 50%, #f7f4ef 100%);
  color: #0f172a;
  font-family: Outfit, "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
}

.result-nav {
  width: min(1500px, 100%);
  margin: 0 auto 34px;
  padding: 14px 18px;
  border-radius: 999px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(18px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
}

.result-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.back-button,
.result-actions :deep(.ant-btn) {
  border-radius: 999px;
  font-weight: 700;
}

.result-shell {
  width: min(1500px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

.side-nav {
  width: auto;
}

.side-nav :deep(.ant-menu) {
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 8px;
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
  background: rgba(255, 255, 255, 0.88);
  padding: 8px;
}

.side-nav :deep(.ant-menu-item),
.side-nav :deep(.ant-menu-submenu-title) {
  margin: 4px 0;
  border-radius: 8px;
  font-weight: 700;
  color: #334155;
}

.side-nav :deep(.ant-menu-item-selected) {
  background: #0f172a !important;
  color: #ffffff !important;
}

.side-nav :deep(.ant-menu-item:hover),
.side-nav :deep(.ant-menu-submenu-title:hover) {
  background: #e0f2fe !important;
  color: #0f172a !important;
}

.main-content {
  flex: initial;
  min-width: 0;
}

.overview-hero {
  min-height: 360px;
  border-radius: 8px;
  padding: clamp(28px, 5vw, 56px);
  color: #ffffff;
  background:
    linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(12, 74, 110, 0.78)),
    url("https://picsum.photos/seed/china-travel-plan/1800/1000") center / cover;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  gap: 36px;
  align-items: end;
  box-shadow: 0 28px 70px rgba(15, 23, 42, 0.18);
}

.eyebrow,
.section-heading p,
.map-heading p {
  margin: 0 0 12px;
  color: #5eead4;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.overview-hero h1 {
  max-width: 980px;
  margin: 0;
  color: #ffffff;
  font-size: clamp(54px, 7vw, 104px);
  line-height: 0.95;
  letter-spacing: 0;
}

.date-range {
  margin: 18px 0 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 18px;
}

.overview-suggestion {
  margin: 0;
  padding: 24px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.8;
  backdrop-filter: blur(16px);
}

.content-map-grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 24px;
  align-items: start;
}

.planning-column {
  grid-column: span 8;
  display: grid;
  gap: 24px;
}

.map-rail {
  grid-column: span 4;
  position: sticky;
  top: 28px;
}

.budget-panel,
.days-section,
.weather-panel,
.map-panel {
  border-radius: 8px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
}

.budget-panel,
.days-section,
.weather-panel {
  padding: clamp(22px, 3vw, 34px);
}

.section-heading h2,
.map-heading h2 {
  margin: 0 0 24px;
  color: #0f172a;
  font-size: clamp(28px, 4vw, 44px);
  line-height: 1.05;
}

.budget-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.budget-item {
  min-height: 118px;
  padding: 18px;
  border-radius: 8px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #f8fafc;
  text-align: left;
  transition: transform 0.25s ease, background 0.25s ease;
}

.budget-item:hover {
  transform: translateY(-4px);
  background: #ecfeff;
}

.budget-item span,
.weather-info-row span {
  display: block;
  color: #64748b;
  font-size: 13px;
  margin-bottom: 10px;
}

.budget-item strong {
  color: #0f172a;
  font-size: 26px;
}

.budget-total {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px;
  border-radius: 8px;
  background: #0f172a;
  color: #ffffff;
}

.budget-total strong {
  font-size: 32px;
  color: #ffffff;
}

.map-panel {
  overflow: hidden;
}

.map-heading {
  padding: 24px 24px 0;
}

#amap-container {
  width: 100%;
  height: min(68vh, 720px);
  min-height: 520px;
}

.day-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.day-header span {
  color: #0f172a;
  font-size: 18px;
  font-weight: 900;
}

.day-header strong {
  color: #64748b;
  font-weight: 700;
}

.day-info {
  margin: 0 0 24px;
  padding: 20px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 8px;
  background: #f8fafc;
}

.info-row {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr);
  gap: 18px;
  margin-bottom: 14px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row span {
  color: #64748b;
  font-weight: 800;
}

.info-row p {
  margin: 0;
  color: #1f2937;
  line-height: 1.75;
}

.subsection-title {
  margin: 28px 0 14px;
  color: #0f172a;
  font-size: 18px;
  font-weight: 900;
}

.attraction-card,
.hotel-card,
.weather-card {
  border-radius: 8px !important;
  border: 1px solid rgba(15, 23, 42, 0.1) !important;
  box-shadow: none !important;
  overflow: hidden;
}

.attraction-card :deep(.ant-card-head),
.hotel-card :deep(.ant-card-head),
.weather-card :deep(.ant-card-head) {
  background: #ffffff !important;
  color: #0f172a !important;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.attraction-card :deep(.ant-card-head-title),
.hotel-card :deep(.ant-card-head-title) {
  color: #0f172a !important;
  font-size: 17px;
  font-weight: 900;
}

.attraction-image-wrapper {
  border-radius: 8px;
  margin-bottom: 16px;
}

.attraction-image {
  height: 220px;
  filter: saturate(0.95) contrast(1.06);
  transition: transform 0.7s ease;
}

.attraction-image-wrapper:hover .attraction-image {
  transform: scale(1.06);
}

.attraction-badge {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #0f172a;
  color: #ffffff;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.22);
}

.price-tag {
  border-radius: 999px;
  background: #f97316;
  color: #ffffff;
}

.attraction-copy p,
.edit-fields p {
  color: #334155;
  line-height: 1.7;
}

.hotel-card {
  background: #f8fafc !important;
}

.hotel-title {
  color: #0f172a !important;
}

.weather-panel {
  margin-top: 0;
}

.weather-card {
  min-height: 190px;
  background: linear-gradient(145deg, #f8fafc, #ecfeff) !important;
}

.weather-date {
  color: #0f766e;
  font-size: 16px;
  font-weight: 900;
  text-align: left;
}

.weather-info-row {
  display: block;
  margin: 16px 0 0;
}

.weather-info-row strong {
  color: #0f172a;
  font-size: 18px;
}

.weather-wind {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(15, 23, 42, 0.1);
  color: #0f766e;
  text-align: left;
}

:deep(.ant-card) {
  margin-bottom: 0;
  animation: none;
}

:deep(.ant-card:hover) {
  box-shadow: none;
}

:deep(.ant-collapse) {
  background: transparent;
  border: 0;
}

:deep(.ant-collapse-item) {
  margin-bottom: 16px;
  border: 1px solid rgba(15, 23, 42, 0.1) !important;
  border-radius: 8px !important;
  overflow: hidden;
  background: #ffffff;
}

:deep(.ant-collapse-header) {
  background: #ffffff !important;
  padding: 18px 22px !important;
}

:deep(.ant-collapse-content) {
  border-top: 1px solid rgba(15, 23, 42, 0.08);
}

:deep(.ant-collapse-content-box) {
  padding: 22px;
}

:deep(.ant-list-item) {
  transform: none !important;
}

.back-top-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #0f172a;
  color: #ffffff;
  display: grid;
  place-items: center;
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.24);
}

.empty-state {
  width: min(720px, 100%);
  margin: 120px auto;
  padding: 54px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(15, 23, 42, 0.1);
}

@media (max-width: 1200px) {
  .result-shell,
  .content-map-grid,
  .overview-hero {
    grid-template-columns: 1fr;
  }

  .planning-column,
  .map-rail {
    grid-column: auto;
  }

  .map-rail {
    position: static;
  }

  .budget-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .result-page {
    padding: 18px;
  }

  .result-nav {
    border-radius: 8px;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .result-actions {
    justify-content: flex-start;
  }

  .side-nav {
    display: none;
  }

  .overview-hero {
    min-height: auto;
  }

  .budget-grid,
  .info-row {
    grid-template-columns: 1fr;
  }

  #amap-container {
    min-height: 360px;
    height: 420px;
  }
}
</style>

