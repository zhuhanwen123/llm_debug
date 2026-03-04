# Multi LLM Unified Gateway (FastAPI + Vue3)

可部署到服务器并通过域名访问的“多大模型统一调用平台”。

- 前端：Vue3 + Vite + TypeScript + TailwindCSS，浅蓝现代风，包含果冻/凝胶效果模型切换。
- 后端：FastAPI + httpx + SQLAlchemy + MySQL。
- 部署：`docker-compose` 一键启动（`nginx + frontend + backend + mysql`）。

## 1. 功能覆盖

- 统一模型入口：`chat / vision / image_gen / video_gen / overseas_image_gen`
- 模型配置从 MySQL `models` 表读取
- 统一调用接口：`POST /api/invoke`
- 图片上传：`POST /api/upload`，保存到 `/uploads`，支持多图
- 视频任务：异步 job（提交 -> 轮询 -> 完成返回视频）
- 安全控制：`X-Access-Token`（用于 `/api/invoke` 与 `/api/upload`）
- 日志：写入 `invoke_logs`
- 调试日志：标准输出自动包含 `request_id`、阶段进度、耗时与错误堆栈

## 2. 工程结构

```text
.
├── .env.example
├── docker-compose.yml
├── README.md
├── nginx
│   └── nginx.conf
├── mysql
│   └── init.sql
├── backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app
│       ├── main.py
│       ├── adapters
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── chat_adapter.py
│       │   ├── vision_adapter.py
│       │   ├── image_gen_adapter.py
│       │   ├── video_gen_adapter.py
│       │   └── overseas_image_gen_adapter.py
│       ├── core
│       │   ├── config.py
│       │   └── logging.py
│       ├── db
│       │   ├── base.py
│       │   ├── models.py
│       │   └── session.py
│       ├── routers
│       │   ├── models_router.py
│       │   ├── upload_router.py
│       │   ├── invoke_router.py
│       │   └── jobs_router.py
│       ├── schemas
│       │   ├── model_schema.py
│       │   ├── upload_schema.py
│       │   ├── invoke_schema.py
│       │   ├── job_schema.py
│       │   └── error_schema.py
│       ├── services
│       │   ├── model_service.py
│       │   ├── upload_service.py
│       │   ├── invoke_service.py
│       │   └── job_service.py
│       └── utils
│           ├── errors.py
│           ├── crypto.py
│           ├── merge.py
│           ├── file_store.py
│           ├── security.py
│           └── request_builders.py
└── frontend
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── postcss.config.js
    └── src
        ├── main.ts
        ├── index.css
        ├── App.vue
        ├── components
        │   ├── ModelSelector.vue
        │   └── OutputPanel.vue
        └── types
            └── api.ts
```

## 3. 快速启动

1. 复制环境变量文件：

```bash
cp .env.example .env
```

2. 修改 `.env` 至少这些项：

- `ACCESS_TOKEN`
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- `LOG_LEVEL`（建议开发环境设为 `DEBUG`）
- 如需图片 URL 绝对路径，设置 `PUBLIC_BASE_URL=https://your-domain.com`

3. 启动：

```bash
docker compose up -d --build
```

4. 访问：

- 前端：`http://<服务器IP或域名>/`
- 模型列表：`http://<服务器IP或域名>/api/models`

## 4. 域名与反向代理

当前架构由根 nginx 统一入口：

- `/` -> `frontend` 容器
- `/api` -> `backend` 容器
- `/uploads` -> 共享卷静态目录

绑定域名时：

- 将 DNS A 记录指向服务器 IP
- 保持 nginx 监听 80（与可选 443）
- TLS 证书可使用你已有方案（例如 certbot / 云厂商证书）
- 若启用 443，请在 `nginx/nginx.conf` 补充 HTTPS server 配置

## 5. API 说明

### `GET /api/models`

返回可用模型：`id,name,type,capabilities,default_params,sort_order`

### `POST /api/upload`

- Header: `X-Access-Token: <ACCESS_TOKEN>`
- Body: `multipart/form-data`，字段名 `files`（支持多文件）
- 返回：`{ "urls": ["/uploads/xxx.png", ...] }`

### `POST /api/invoke`

- Header: `X-Access-Token: <ACCESS_TOKEN>`
- Body:

```json
{
  "model_id": 1,
  "system_prompt": "你是助手",
  "user_message": "你好",
  "images": ["/uploads/a.png"],
  "params": {"temperature": 0.7}
}
```

### `GET /api/jobs/{job_id}`

返回任务状态：`queued/running/completed/failed` 及进度/结果。

## 6. 数据库说明

初始化脚本位于：`mysql/init.sql`

包含三张表：

- `models`
- `jobs`
- `invoke_logs`

并预置 5 个 `mock` 模型（覆盖五类能力），开箱可跑。

## 7. Adapter 可替换说明

当前 Adapter 采用“可配置请求构造”方式：

- 请求 URL：`base_url + endpoint_path`
- 鉴权：`api_auth_type + api_key_header + api_key_enc`
- 参数：`default_params` 与请求 `params` 合并

视频适配器 `VideoGenAdapter` 当前为 mock 轮询逻辑。替换真实供应商时，改造：

1. `create_job(...)`：调用供应商创建任务接口并返回 `provider_job_id`
2. `poll_job(provider_job_id)`：查询供应商任务状态，完成时返回 `video_url/cover_url`

## 8. 安全说明

- 前端不存储真实模型 API Key，仅存用户输入的访问口令。
- 模型 API key 保存在数据库字段 `api_key_enc`。
- `MASTER_KEY` 已预留解密入口（`backend/app/utils/crypto.py`）。
- 目前默认允许明文/`plain:` 前缀；如上生产请替换为真实加解密实现。

## 9. 常见排查

- `401 Invalid X-Access-Token`：前端口令与 `.env` 中 `ACCESS_TOKEN` 不一致。
- 图片无法访问：确认 `uploads_data` 卷已挂载到 nginx 的 `/uploads`。
- 模型调用失败：检查 `models` 表中目标模型的 `base_url/endpoint_path/auth` 配置。
- 追踪调用进度：`docker compose logs -f backend`，按 `request_id` 过滤，查看 `invoke.start -> invoke.adapter_selected -> invoke.success`；视频任务看 `video_job.progress`、`video_job.completed` 或 `video_job.exception`。
