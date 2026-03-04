<template>
  <section class="card-glass rounded-2xl p-4 shadow-jelly animate-floatIn">
    <h2 class="mb-3 text-lg font-semibold text-sky-900">输出区</h2>

    <div v-if="error" class="rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-700">
      {{ error }}
    </div>

    <template v-else-if="output">
      <div v-if="output.kind === 'text'" class="rounded-xl bg-white/70 p-4 text-sm leading-7 text-sky-900">
        {{ output.text || '(空文本)' }}
      </div>

      <div v-else-if="output.kind === 'image'" class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <a
          v-for="(img, idx) in output.images"
          :key="`${img}-${idx}`"
          :href="img"
          target="_blank"
          rel="noreferrer"
          class="overflow-hidden rounded-xl border border-sky-200 bg-white"
        >
          <img :src="img" class="h-52 w-full object-cover" />
        </a>
      </div>

      <div v-else-if="output.kind === 'video_job'" class="space-y-3">
        <div class="text-sm text-sky-900">任务ID: {{ output.job_id }}</div>
        <div class="h-3 w-full overflow-hidden rounded-full bg-sky-100">
          <div class="h-full rounded-full bg-sky-500 transition-all" :style="{ width: `${output.progress || 0}%` }"></div>
        </div>
        <div class="text-sm text-sky-700">状态: {{ output.status }} · {{ output.progress || 0 }}%</div>
      </div>

      <div v-else-if="output.kind === 'video'" class="space-y-3">
        <img v-if="output.cover_url" :src="output.cover_url" class="h-52 w-full rounded-xl object-cover" />
        <a
          v-if="output.video_url"
          :href="output.video_url"
          target="_blank"
          rel="noreferrer"
          class="inline-block rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white"
        >
          打开视频链接
        </a>
      </div>
    </template>

    <div v-else class="text-sm text-sky-700">暂无输出</div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  output: {
    kind: string
    text?: string
    images?: string[]
    job_id?: string
    progress?: number
    status?: string
    video_url?: string
    cover_url?: string
  } | null
  error: string
}>()
</script>
