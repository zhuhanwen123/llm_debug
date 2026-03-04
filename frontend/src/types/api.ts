export type ModelType = 'chat' | 'vision' | 'image_gen' | 'video_gen' | 'overseas_image_gen'

export interface ModelItem {
  id: number
  name: string
  type: ModelType
  capabilities?: Record<string, unknown>
  default_params?: Record<string, unknown>
  sort_order: number
}

export interface ModelsResponse {
  items: ModelItem[]
}

export interface InvokeRequest {
  model_id: number
  system_prompt: string
  user_message: string
  images: string[]
  params: Record<string, unknown>
}

export interface InvokeResponse {
  request_id: string
  model_id: number
  model_type: ModelType
  status: string
  output: {
    kind: string
    text?: string
    images?: string[]
    job_id?: string
    progress?: number
    status?: string
    video_url?: string
    cover_url?: string
  }
}

export interface JobResponse {
  job_id: string
  model_id: number
  status: string
  progress: number
  result?: {
    kind: string
    video_url?: string
    cover_url?: string
  }
  error_message?: string
}

export interface UploadResponse {
  urls: string[]
}
