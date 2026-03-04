<template>
  <main class="mx-auto min-h-screen w-full max-w-6xl p-4 md:p-8">
    <header class="mb-6 animate-floatIn">
      <h1 class="text-3xl font-bold text-sky-900">多大模型统一调用平台</h1>
      <p class="mt-2 text-sm text-sky-800/80">统一入口支持 chat / vision / image_gen / video_gen / overseas_image_gen</p>
    </header>

    <section class="card-glass mb-4 rounded-2xl p-4 shadow-jelly animate-floatIn">
      <label class="mb-2 block text-sm font-medium text-sky-900">访问口令（X-Access-Token）</label>
      <input
        v-model="accessToken"
        type="password"
        placeholder="请输入 ACCESS_TOKEN"
        class="w-full rounded-xl border border-sky-200 bg-white/80 px-3 py-2 text-sm outline-none ring-sky-300 focus:ring"
        @change="persistToken"
      />
    </section>

    <ModelSelector v-model="selectedModelId" :models="models" />

    <section class="card-glass mt-4 rounded-2xl p-4 shadow-jelly animate-floatIn">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label class="mb-2 block text-sm font-medium text-sky-900">system_prompt</label>
          <textarea
            v-model="systemPrompt"
            rows="5"
            class="w-full rounded-xl border border-sky-200 bg-white/80 px-3 py-2 text-sm outline-none ring-sky-300 focus:ring"
            placeholder="你是一个有帮助的助手..."
          />
        </div>
        <div>
          <label class="mb-2 block text-sm font-medium text-sky-900">user_message</label>
          <textarea
            v-model="userMessage"
            rows="5"
            class="w-full rounded-xl border border-sky-200 bg-white/80 px-3 py-2 text-sm outline-none ring-sky-300 focus:ring"
            placeholder="请输入用户问题或图像生成提示词"
          />
        </div>
      </div>

      <div class="mt-4">
        <label class="mb-2 block text-sm font-medium text-sky-900">params(JSON)</label>
        <textarea
          v-model="paramsJson"
          rows="3"
          class="w-full rounded-xl border border-sky-200 bg-white/80 px-3 py-2 font-mono text-sm outline-none ring-sky-300 focus:ring"
          placeholder='{"temperature":0.7}'
        />
      </div>

      <div class="mt-4">
        <div class="mb-2 text-sm font-medium text-sky-900">图片上传（多图）</div>
        <div class="flex flex-wrap items-center gap-3">
          <input type="file" accept="image/*" multiple @change="onUploadFiles" />
          <span v-if="isUploading" class="text-sm text-sky-700">上传中...</span>
        </div>

        <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          <div
            v-for="(url, idx) in imageUrls"
            :key="`${url}-${idx}`"
            class="group relative overflow-hidden rounded-xl border border-sky-200 bg-white"
          >
            <img :src="url" class="h-24 w-full object-cover" />
            <button
              type="button"
              class="absolute right-1 top-1 rounded-full bg-white/90 px-2 py-0.5 text-xs text-red-600 opacity-0 transition group-hover:opacity-100"
              @click="removeImage(idx)"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      <div class="mt-5 flex items-center gap-3">
        <button
          type="button"
          class="rounded-xl bg-sky-600 px-5 py-2 text-sm font-semibold text-white shadow-jelly transition hover:bg-sky-700 disabled:opacity-50"
          :disabled="isInvoking"
          @click="onInvoke"
        >
          {{ isInvoking ? '调用中...' : '调用模型' }}
        </button>

        <span v-if="selectedModel" class="text-sm text-sky-800">
          当前模型：{{ selectedModel.name }} ({{ selectedModel.type }})
        </span>
      </div>
    </section>

    <div class="mt-4">
      <OutputPanel :output="output" :error="errorMessage" />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import ModelSelector from './components/ModelSelector.vue'
import OutputPanel from './components/OutputPanel.vue'
import type { InvokeRequest, InvokeResponse, JobResponse, ModelItem, ModelsResponse, UploadResponse } from './types/api'

const models = ref<ModelItem[]>([])
const selectedModelId = ref<number | null>(null)
const systemPrompt = ref('')
const userMessage = ref('')
const paramsJson = ref('{}')
const imageUrls = ref<string[]>([])
const output = ref<InvokeResponse['output'] | null>(null)
const errorMessage = ref('')
const isUploading = ref(false)
const isInvoking = ref(false)
const accessToken = ref(localStorage.getItem('access_token') || '')

let pollTimer: number | null = null

const selectedModel = computed(() => models.value.find((m) => m.id === selectedModelId.value) || null)

onMounted(async () => {
  await fetchModels()
})

onBeforeUnmount(() => {
  if (pollTimer) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
})

function persistToken() {
  localStorage.setItem('access_token', accessToken.value)
}

async function fetchModels() {
  try {
    const resp = await fetch('/api/models')
    if (!resp.ok) {
      throw new Error(`加载模型失败: ${resp.status}`)
    }
    const data = (await resp.json()) as ModelsResponse
    models.value = data.items || []
    if (!selectedModelId.value && models.value.length > 0) {
      selectedModelId.value = models.value[0].id
      if (models.value[0].default_params) {
        paramsJson.value = JSON.stringify(models.value[0].default_params, null, 2)
      }
    }
  } catch (err) {
    errorMessage.value = (err as Error).message
  }
}

async function onUploadFiles(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) {
    return
  }
  if (!accessToken.value) {
    errorMessage.value = '请先输入访问口令'
    return
  }

  isUploading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    Array.from(files).forEach((file) => formData.append('files', file))

    const resp = await fetch('/api/upload', {
      method: 'POST',
      headers: {
        'X-Access-Token': accessToken.value
      },
      body: formData
    })

    const data = (await resp.json()) as UploadResponse & { message?: string }
    if (!resp.ok) {
      throw new Error(data.message || `上传失败: ${resp.status}`)
    }

    imageUrls.value.push(...data.urls)
    target.value = ''
  } catch (err) {
    errorMessage.value = (err as Error).message
  } finally {
    isUploading.value = false
  }
}

function removeImage(index: number) {
  imageUrls.value.splice(index, 1)
}

function parseParams(): Record<string, unknown> {
  if (!paramsJson.value.trim()) {
    return {}
  }
  return JSON.parse(paramsJson.value)
}

async function onInvoke() {
  if (!selectedModelId.value) {
    errorMessage.value = '请先选择模型'
    return
  }
  if (!accessToken.value) {
    errorMessage.value = '请先输入访问口令'
    return
  }

  isInvoking.value = true
  errorMessage.value = ''

  try {
    const payload: InvokeRequest = {
      model_id: selectedModelId.value,
      system_prompt: systemPrompt.value,
      user_message: userMessage.value,
      images: imageUrls.value,
      params: parseParams()
    }

    const resp = await fetch('/api/invoke', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': accessToken.value
      },
      body: JSON.stringify(payload)
    })

    const data = (await resp.json()) as InvokeResponse & { message?: string }
    if (!resp.ok) {
      throw new Error(data.message || `调用失败: ${resp.status}`)
    }

    output.value = data.output
    if (data.output.kind === 'video_job' && data.output.job_id) {
      startJobPolling(data.output.job_id)
    } else {
      clearPolling()
    }
  } catch (err) {
    errorMessage.value = (err as Error).message
  } finally {
    isInvoking.value = false
  }
}

function clearPolling() {
  if (pollTimer) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
}

function startJobPolling(jobId: string) {
  clearPolling()

  pollTimer = window.setInterval(async () => {
    try {
      const resp = await fetch(`/api/jobs/${jobId}`)
      const data = (await resp.json()) as JobResponse & { message?: string }
      if (!resp.ok) {
        throw new Error(data.message || '任务查询失败')
      }

      if (data.status === 'completed' && data.result) {
        output.value = {
          kind: 'video',
          video_url: data.result.video_url,
          cover_url: data.result.cover_url,
          status: data.status,
          progress: data.progress
        }
        clearPolling()
        return
      }

      if (data.status === 'failed') {
        output.value = {
          kind: 'video_job',
          job_id: data.job_id,
          status: data.status,
          progress: data.progress
        }
        errorMessage.value = data.error_message || '视频任务失败'
        clearPolling()
        return
      }

      output.value = {
        kind: 'video_job',
        job_id: data.job_id,
        status: data.status,
        progress: data.progress
      }
    } catch (err) {
      errorMessage.value = (err as Error).message
      clearPolling()
    }
  }, 2000)
}
</script>
