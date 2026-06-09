<template>
  <main class="home-page">
    <nav class="topbar">
      <div class="brand-lockup">
        <span class="brand-mark">AI</span>
        <div>
          <strong>智能旅行助手</strong>
          <span>Trip Planning Studio</span>
        </div>
      </div>
      <div class="nav-copy">多 Agent 协同生成行程</div>
    </nav>

    <section class="hero-stage">
      <div class="hero-copy">
        <p class="eyebrow">旅行计划生成器</p>
        <h1>
          把目的地、偏好和时间，整理成一份可执行的旅行计划。
        </h1>
        <p class="hero-description">
          输入你的出行信息，后端会协调景点、天气、酒店和规划 Agent，生成可查看地图与图片的结果页。
        </p>
      </div>

      <div class="hero-ticket" aria-hidden="true">
        <div class="ticket-line"></div>
        <div class="ticket-content">
          <span>{{ formData.city || '目的地待定' }}</span>
          <strong>{{ formData.travel_days }} 天</strong>
          <small>{{ formData.transportation }} / {{ formData.accommodation }}</small>
        </div>
      </div>
    </section>

    <section class="planner-grid">
      <section class="form-panel">
        <div class="panel-heading">
          <p>开始规划</p>
          <h2>出行信息</h2>
        </div>

        <a-form :model="formData" layout="vertical" @finish="handleSubmit">
          <div class="form-block">
            <div class="block-title">
              <span class="step-dot"></span>
              <span>目的地与时间</span>
            </div>

            <div class="field-grid destination-grid">
              <a-form-item name="city" :rules="[{ required: true, message: '请输入目的地城市' }]">
                <template #label>
                  <span class="form-label">目的地城市</span>
                </template>
                <a-input
                  v-model:value="formData.city"
                  placeholder="例如: 北京"
                  size="large"
                  class="studio-input"
                />
              </a-form-item>

              <a-form-item name="start_date" :rules="[{ required: true, message: '请选择开始日期' }]">
                <template #label>
                  <span class="form-label">开始日期</span>
                </template>
                <a-date-picker
                  v-model:value="formData.start_date"
                  style="width: 100%"
                  size="large"
                  class="studio-input"
                  placeholder="选择日期"
                />
              </a-form-item>

              <a-form-item name="end_date" :rules="[{ required: true, message: '请选择结束日期' }]">
                <template #label>
                  <span class="form-label">结束日期</span>
                </template>
                <a-date-picker
                  v-model:value="formData.end_date"
                  style="width: 100%"
                  size="large"
                  class="studio-input"
                  placeholder="选择日期"
                />
              </a-form-item>

              <a-form-item>
                <template #label>
                  <span class="form-label">旅行天数</span>
                </template>
                <div class="days-meter">
                  <strong>{{ formData.travel_days }}</strong>
                  <span>天</span>
                </div>
              </a-form-item>
            </div>
          </div>

          <div class="form-block">
            <div class="block-title">
              <span class="step-dot"></span>
              <span>偏好配置</span>
            </div>

            <div class="field-grid preference-grid">
              <a-form-item name="transportation">
                <template #label>
                  <span class="form-label">交通方式</span>
                </template>
                <a-select v-model:value="formData.transportation" size="large" class="studio-select">
                  <a-select-option value="公共交通">公共交通</a-select-option>
                  <a-select-option value="自驾">自驾</a-select-option>
                  <a-select-option value="步行">步行</a-select-option>
                  <a-select-option value="混合">混合</a-select-option>
                </a-select>
              </a-form-item>

              <a-form-item name="accommodation">
                <template #label>
                  <span class="form-label">住宿偏好</span>
                </template>
                <a-select v-model:value="formData.accommodation" size="large" class="studio-select">
                  <a-select-option value="经济型酒店">经济型酒店</a-select-option>
                  <a-select-option value="舒适型酒店">舒适型酒店</a-select-option>
                  <a-select-option value="豪华酒店">豪华酒店</a-select-option>
                  <a-select-option value="民宿">民宿</a-select-option>
                </a-select>
              </a-form-item>
            </div>

            <a-form-item name="preferences">
              <template #label>
                <span class="form-label">旅行偏好</span>
              </template>
              <a-checkbox-group v-model:value="formData.preferences" class="preference-list">
                <a-checkbox value="历史文化">历史文化</a-checkbox>
                <a-checkbox value="自然风光">自然风光</a-checkbox>
                <a-checkbox value="美食">美食</a-checkbox>
                <a-checkbox value="购物">购物</a-checkbox>
                <a-checkbox value="艺术">艺术</a-checkbox>
                <a-checkbox value="休闲">休闲</a-checkbox>
              </a-checkbox-group>
            </a-form-item>
          </div>

          <div class="form-block">
            <div class="block-title">
              <span class="step-dot"></span>
              <span>补充要求</span>
            </div>

            <a-form-item name="free_text_input">
              <a-textarea
                v-model:value="formData.free_text_input"
                placeholder="例如: 希望少走路、想看升旗、需要无障碍设施"
                :rows="4"
                size="large"
                class="studio-textarea"
              />
            </a-form-item>
          </div>

          <a-button
            type="primary"
            html-type="submit"
            :loading="loading"
            size="large"
            block
            class="submit-button"
          >
            <span v-if="!loading">生成旅行计划</span>
            <span v-else>正在生成中</span>
          </a-button>

          <div v-if="loading" class="loading-panel">
            <a-progress
              :percent="loadingProgress"
              status="active"
              :stroke-color="{ '0%': '#0f766e', '100%': '#2563eb' }"
              :stroke-width="8"
            />
            <p>{{ loadingStatus }}</p>
          </div>
        </a-form>
      </section>

      <aside class="preview-panel">
        <div class="preview-card primary-preview">
          <p>当前草稿</p>
          <h2>{{ formData.city || '等待输入城市' }}</h2>
          <div class="preview-route">
            <span></span>
            <i></i>
            <span></span>
            <i></i>
            <span></span>
          </div>
          <div class="preview-meta">
            <div>
              <small>日期</small>
              <strong>{{ dateRangeText }}</strong>
            </div>
            <div>
              <small>天数</small>
              <strong>{{ formData.travel_days }} 天</strong>
            </div>
          </div>
        </div>

        <div class="preview-card detail-preview">
          <div class="summary-row" v-for="item in summaryItems" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>

        <div class="planner-steps">
          <div
            v-for="(step, index) in planningSteps"
            :key="step"
            class="planner-step"
            :class="{ active: loading && loadingProgress >= (index + 1) * 20 }"
          >
            <span>{{ index + 1 }}</span>
            <p>{{ step }}</p>
          </div>
        </div>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { generateTripPlan } from '@/services/api'
import type { TripFormData } from '@/types'
import type { Dayjs } from 'dayjs'

type HomeFormData = Omit<TripFormData, 'start_date' | 'end_date'> & {
  start_date: Dayjs | null
  end_date: Dayjs | null
}

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')

const formData = reactive<HomeFormData>({
  city: '',
  start_date: null,
  end_date: null,
  travel_days: 1,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: ''
})

const dateRangeText = computed(() => {
  if (!formData.start_date || !formData.end_date) {
    return '待选择'
  }
  return `${formData.start_date.format('MM月DD日')} - ${formData.end_date.format('MM月DD日')}`
})

const preferenceText = computed(() => {
  return formData.preferences.length ? formData.preferences.join(' / ') : '尚未选择'
})

const summaryItems = computed(() => [
  { label: '交通', value: formData.transportation },
  { label: '住宿', value: formData.accommodation },
  { label: '偏好', value: preferenceText.value },
  { label: '补充', value: formData.free_text_input || '暂无' }
])

const planningSteps = ['景点搜索', '天气查询', '酒店推荐', '行程整合']

watch([() => formData.start_date, () => formData.end_date], ([start, end]) => {
  if (start && end) {
    const days = end.diff(start, 'day') + 1
    if (days > 0 && days <= 30) {
      formData.travel_days = days
    } else if (days > 30) {
      message.warning('旅行天数不能超过30天')
      formData.end_date = null
    } else {
      message.warning('结束日期不能早于开始日期')
      formData.end_date = null
    }
  }
})

const handleSubmit = async () => {
  if (!formData.start_date || !formData.end_date) {
    message.error('请选择日期')
    return
  }

  loading.value = true
  loadingProgress.value = 0
  loadingStatus.value = '正在初始化'

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += 10

      if (loadingProgress.value <= 30) {
        loadingStatus.value = '正在搜索景点'
      } else if (loadingProgress.value <= 50) {
        loadingStatus.value = '正在查询天气'
      } else if (loadingProgress.value <= 70) {
        loadingStatus.value = '正在推荐酒店'
      } else {
        loadingStatus.value = '正在生成行程计划'
      }
    }
  }, 500)

  try {
    const requestData: TripFormData = {
      city: formData.city,
      start_date: formData.start_date.format('YYYY-MM-DD'),
      end_date: formData.end_date.format('YYYY-MM-DD'),
      travel_days: formData.travel_days,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      free_text_input: formData.free_text_input
    }

    const response = await generateTripPlan(requestData)

    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingStatus.value = '生成完成'

    if (response.success && response.data) {
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))
      message.success('旅行计划生成成功')

      setTimeout(() => {
        router.push('/result')
      }, 500)
    } else {
      message.error(response.message || '生成失败')
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    message.error(error.message || '生成旅行计划失败,请稍后重试')
  } finally {
    setTimeout(() => {
      loading.value = false
      loadingProgress.value = 0
      loadingStatus.value = ''
    }, 1000)
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  background:
    radial-gradient(circle at 78% 8%, rgba(20, 184, 166, 0.18), transparent 28%),
    linear-gradient(135deg, #f8fafc 0%, #e5edf5 46%, #f7f4ef 100%);
  color: #111827;
  font-family: Outfit, "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
  padding: 28px;
}

.topbar {
  width: min(1480px, 100%);
  margin: 0 auto;
  padding: 14px 18px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(18px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
}

.brand-lockup {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-lockup strong,
.brand-lockup span {
  display: block;
}

.brand-lockup strong {
  font-size: 16px;
  color: #0f172a;
}

.brand-lockup span:not(.brand-mark) {
  color: #64748b;
  font-size: 12px;
  margin-top: 2px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #ffffff;
  font-weight: 800;
  background: #0f172a;
}

.nav-copy {
  color: #475569;
  font-size: 14px;
}

.hero-stage {
  width: min(1480px, 100%);
  margin: 86px auto 62px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 60px;
  align-items: end;
}

.eyebrow,
.panel-heading p,
.preview-card p {
  color: #0f766e;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin: 0 0 14px;
}

.hero-copy h1 {
  max-width: 920px;
  font-size: clamp(44px, 6vw, 84px);
  line-height: 1.02;
  letter-spacing: 0;
  margin: 0;
  color: #0f172a;
}

.hero-description {
  max-width: 680px;
  margin: 26px 0 0;
  color: #475569;
  font-size: 18px;
  line-height: 1.8;
}

.hero-ticket {
  min-height: 260px;
  border-radius: 8px;
  padding: 22px;
  background:
    linear-gradient(145deg, rgba(15, 23, 42, 0.94), rgba(19, 78, 74, 0.88)),
    url("https://picsum.photos/seed/travel-map/900/700") center / cover;
  box-shadow: 0 28px 70px rgba(15, 23, 42, 0.24);
  color: #ffffff;
  position: relative;
  overflow: hidden;
}

.ticket-line {
  position: absolute;
  inset: 18px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 6px;
}

.ticket-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 8px;
}

.ticket-content span {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.72);
}

.ticket-content strong {
  font-size: 60px;
  line-height: 1;
}

.ticket-content small {
  color: rgba(255, 255, 255, 0.76);
}

.planner-grid {
  width: min(1480px, 100%);
  margin: 0 auto 80px;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 24px;
  align-items: start;
}

.form-panel {
  grid-column: span 7;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 8px;
  padding: clamp(24px, 4vw, 44px);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.12);
}

.preview-panel {
  grid-column: span 5;
  position: sticky;
  top: 28px;
  display: grid;
  gap: 18px;
}

.panel-heading h2 {
  margin: 0 0 30px;
  font-size: clamp(30px, 4vw, 48px);
  color: #0f172a;
  line-height: 1.1;
}

.form-block {
  padding: 26px 0;
  border-top: 1px solid rgba(15, 23, 42, 0.1);
}

.form-block:first-of-type {
  padding-top: 0;
  border-top: 0;
}

.block-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  color: #0f172a;
  font-size: 18px;
  font-weight: 800;
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #14b8a6;
  box-shadow: 0 0 0 8px rgba(20, 184, 166, 0.12);
}

.field-grid {
  display: grid;
  gap: 18px;
}

.destination-grid {
  grid-template-columns: 1.3fr 1fr 1fr 120px;
}

.preference-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.form-label {
  color: #334155;
  font-weight: 700;
}

.studio-input :deep(.ant-input),
.studio-input :deep(.ant-picker),
.studio-select :deep(.ant-select-selector),
.studio-textarea :deep(.ant-input) {
  border-radius: 8px !important;
  border-color: rgba(15, 23, 42, 0.16) !important;
  box-shadow: none !important;
}

.studio-input :deep(.ant-input:hover),
.studio-input :deep(.ant-picker:hover),
.studio-select:hover :deep(.ant-select-selector),
.studio-textarea :deep(.ant-input:hover) {
  border-color: #0f766e !important;
}

.days-meter {
  height: 40px;
  border-radius: 8px;
  background: #0f172a;
  color: #ffffff;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.days-meter strong {
  font-size: 24px;
}

.days-meter span {
  font-size: 13px;
}

.preference-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
}

.preference-list :deep(.ant-checkbox-wrapper) {
  margin: 0;
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid rgba(15, 23, 42, 0.14);
  border-radius: 8px;
  background: #f8fafc;
  transition: transform 0.25s ease, border-color 0.25s ease, background 0.25s ease;
}

.preference-list :deep(.ant-checkbox-wrapper:hover) {
  transform: translateY(-2px);
  border-color: #0f766e;
  background: #ecfdf5;
}

.submit-button {
  height: 58px;
  border-radius: 8px;
  border: 0;
  background: #0f172a;
  color: #ffffff;
  font-size: 17px;
  font-weight: 800;
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.22);
}

.submit-button:hover {
  background: #134e4a !important;
  color: #ffffff !important;
}

.loading-panel {
  margin-top: 18px;
  padding: 18px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid rgba(15, 23, 42, 0.1);
}

.loading-panel p {
  margin: 12px 0 0;
  color: #0f766e;
  font-weight: 700;
}

.preview-card {
  border-radius: 8px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.primary-preview {
  padding: 30px;
  color: #ffffff;
  min-height: 320px;
  background:
    linear-gradient(155deg, rgba(15, 23, 42, 0.88), rgba(15, 118, 110, 0.78)),
    url("https://picsum.photos/seed/rail-window/1200/900") center / cover;
}

.primary-preview p {
  color: rgba(255, 255, 255, 0.68);
}

.primary-preview h2 {
  margin: 0;
  font-size: clamp(34px, 5vw, 60px);
  color: #ffffff;
  line-height: 1.05;
}

.preview-route {
  display: grid;
  grid-template-columns: 12px 1fr 12px 1fr 12px;
  align-items: center;
  gap: 10px;
  margin: 54px 0;
}

.preview-route span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #f97316;
}

.preview-route i {
  height: 1px;
  background: rgba(255, 255, 255, 0.52);
}

.preview-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.preview-meta div {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.24);
}

.preview-meta small,
.summary-row span {
  display: block;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 6px;
}

.preview-meta small {
  color: rgba(255, 255, 255, 0.62);
}

.preview-meta strong {
  color: #ffffff;
}

.detail-preview {
  padding: 8px 24px;
}

.summary-row {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.summary-row:last-child {
  border-bottom: 0;
}

.summary-row strong {
  color: #0f172a;
  line-height: 1.6;
  word-break: break-word;
}

.planner-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.planner-step {
  min-height: 112px;
  padding: 14px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.1);
  transition: transform 0.25s ease, background 0.25s ease, color 0.25s ease;
}

.planner-step.active {
  transform: translateY(-4px);
  background: #0f766e;
  color: #ffffff;
}

.planner-step span {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.08);
  font-weight: 800;
}

.planner-step.active span {
  background: rgba(255, 255, 255, 0.2);
}

.planner-step p {
  margin: 24px 0 0;
  font-weight: 800;
}

@media (max-width: 1100px) {
  .home-page {
    padding: 18px;
  }

  .hero-stage,
  .planner-grid {
    grid-template-columns: 1fr;
  }

  .form-panel,
  .preview-panel {
    grid-column: auto;
  }

  .preview-panel {
    position: static;
  }

  .destination-grid,
  .preference-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 720px) {
  .topbar {
    border-radius: 8px;
    align-items: flex-start;
    gap: 14px;
    flex-direction: column;
  }

  .hero-stage {
    margin-top: 52px;
  }

  .destination-grid,
  .preference-grid,
  .preference-list,
  .planner-steps {
    grid-template-columns: 1fr;
  }

  .hero-ticket {
    min-height: 220px;
  }
}
</style>
