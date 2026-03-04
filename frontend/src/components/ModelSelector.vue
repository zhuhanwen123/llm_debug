<template>
  <section class="card-glass rounded-2xl p-4 shadow-jelly animate-floatIn">
    <h2 class="mb-3 text-lg font-semibold text-sky-900">ModelSelector</h2>
    <div class="grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-3">
      <button
        v-for="model in models"
        :key="model.id"
        type="button"
        class="jelly-btn"
        :class="{ active: model.id === modelValue }"
        @click="emit('update:modelValue', model.id)"
      >
        <span class="text-sm font-semibold">{{ model.name }}</span>
        <span class="text-xs uppercase opacity-80">{{ model.type }}</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { ModelItem } from '../types/api'

defineProps<{
  models: ModelItem[]
  modelValue: number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
}>()
</script>

<style scoped>
.jelly-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  border-radius: 18px;
  border: 1px solid rgba(111, 199, 255, 0.5);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.88), rgba(209, 236, 255, 0.58));
  padding: 12px 14px;
  color: #1c557d;
  box-shadow: 0 8px 20px rgba(93, 170, 232, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.jelly-btn:hover {
  transform: translateY(-2px) scale(1.01);
  border-color: rgba(57, 176, 250, 0.7);
}

.jelly-btn.active {
  border-color: rgba(36, 156, 235, 0.95);
  background: linear-gradient(150deg, rgba(223, 244, 255, 0.96), rgba(147, 214, 255, 0.72));
  box-shadow: 0 12px 24px rgba(57, 176, 250, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.85);
  animation: jelly 420ms ease-out;
}

@keyframes jelly {
  0% { transform: scale(1); }
  35% { transform: scale(0.92, 1.08); }
  70% { transform: scale(1.04, 0.96); }
  100% { transform: scale(1); }
}
</style>
