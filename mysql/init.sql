-- Active: 1772617893426@@127.0.0.1@3308@llm_aggregator
CREATE TABLE IF NOT EXISTS models (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(32) NOT NULL,
  provider VARCHAR(64) NOT NULL,
  model_code VARCHAR(128) NULL,
  base_url VARCHAR(255) NULL,
  api_key_enc TEXT NULL,
  api_auth_type VARCHAR(32) NOT NULL DEFAULT 'bearer',
  api_key_header VARCHAR(64) NULL,
  endpoint_path VARCHAR(255) NULL,
  timeout_ms INT NOT NULL DEFAULT 60000,
  is_enabled TINYINT(1) NOT NULL DEFAULT 1,
  sort_order INT NOT NULL DEFAULT 0,
  capabilities JSON NULL,
  default_params JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_models_type_enabled (type, is_enabled),
  INDEX idx_models_sort (sort_order)
);

CREATE TABLE IF NOT EXISTS jobs (
  job_id VARCHAR(64) PRIMARY KEY,
  model_id INT NOT NULL,
  status VARCHAR(32) NOT NULL,
  progress INT NOT NULL DEFAULT 0,
  result JSON NULL,
  error_message TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_jobs_status (status),
  INDEX idx_jobs_model (model_id)
);

CREATE TABLE IF NOT EXISTS invoke_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  request_id VARCHAR(64) NOT NULL,
  model_id INT NOT NULL,
  status VARCHAR(32) NOT NULL,
  latency_ms INT NOT NULL,
  error_message TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_logs_request (request_id),
  INDEX idx_logs_model (model_id),
  INDEX idx_logs_created (created_at)
);

INSERT INTO models (
  id, name, type, provider, model_code, base_url, api_key_enc,
  api_auth_type, api_key_header, endpoint_path, timeout_ms,
  is_enabled, sort_order, capabilities, default_params
) VALUES
  (
    1, 'qwen3-max', 'chat', 'Qwen', 'mock-chat', "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", "sk-c8a3217c817e4942b7e4cafc8a805c9b",
    'none', NULL, NULL, 60000,
    1, 10,
    JSON_OBJECT('supports_text', true),
    JSON_OBJECT('temperature', 0.7)
  ),
  (
    2, 'doubao-seed-1-6-251015', 'vision', 'Doubao', 'mock-vision', "https://ark.cn-beijing.volces.com/api/v3/chat/completions", "7480055d-8747-4774-9e1c-49be5f264873",
    'none', NULL, NULL, 60000,
    1, 20,
    JSON_OBJECT('supports_images', true, 'supports_text', true),
    JSON_OBJECT('temperature', 0.2)
  ),
  (
    3, 'doubao-seedream-4-5-251128', 'image_gen', 'Doubao', 'mock-image', "https://ark.cn-beijing.volces.com/api/v3/images/generations", "7480055d-8747-4774-9e1c-49be5f264873",
    'none', NULL, NULL, 90000,
    1, 30,
    JSON_OBJECT('image_output', true),
    JSON_OBJECT('size', '1024x1024')
  ),
  (
    4, 'doubao-seedance-1-5-pro-251215', 'video_gen', 'Doubao', 'mock-video', "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks", "7480055d-8747-4774-9e1c-49be5f264873",
    'none', NULL, NULL, 120000,
    1, 40,
    JSON_OBJECT('async_job', true, 'video_output', true),
    JSON_OBJECT('duration_seconds', 5)
  ),
  (
    5, 'gemini-3-pro-image-preview', 'overseas_image_gen', 'laozhang', 'mock-overseas-image', "https://api.laozhang.ai/v1beta/models/gemini-3-pro-image-preview:generateContent", "sk-3Ofgxw6KPpXoSthEB058B9Eb969542909644D2A606A8D40d",
    'none', NULL, NULL, 90000,
    1, 50,
    JSON_OBJECT('image_output', true, 'overseas', true),
    JSON_OBJECT('size', '1024x1024', 'style', 'photorealistic')
  )
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  type = VALUES(type),
  provider = VALUES(provider),
  model_code = VALUES(model_code),
  base_url = VALUES(base_url),
  api_key_enc = VALUES(api_key_enc),
  api_auth_type = VALUES(api_auth_type),
  api_key_header = VALUES(api_key_header),
  endpoint_path = VALUES(endpoint_path),
  timeout_ms = VALUES(timeout_ms),
  is_enabled = VALUES(is_enabled),
  sort_order = VALUES(sort_order),
  capabilities = VALUES(capabilities),
  default_params = VALUES(default_params);
