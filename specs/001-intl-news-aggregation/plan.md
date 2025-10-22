# Implementation Plan: International Financial News Aggregation System

**Branch**: `001-intl-news-aggregation` | **Date**: 2025-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-intl-news-aggregation/spec.md`

---

## Technical Stack & Architecture Plan (YAML)

```yaml
tech_stack:
  backend:
    framework: "FastAPI (Python 3.11+)"
    concurrency: "async/await + asyncio + httpx"
    rendering: "Playwright (Chromium headless) for dynamic content"
    rationale: "FastAPI提供原生async支持,httpx用于并发HTTP请求,Playwright处理JS渲染页面"

  crawling:
    feeds: "feedparser (RSS/Atom) + RSSHub API fallback"
    html_parsing: "BeautifulSoup4 + lxml"
    rendering: "Playwright (async) for JavaScript-heavy sites"
    concurrency: "asyncio.gather() + semaphore限流 + 线程池(ThreadPoolExecutor)处理CPU密集型解析"
    politeness:
      - "robots.txt遵守 (robotparser库)"
      - "Sitemap优先级索引"
      - "ETag/Last-Modified条件请求减少重复抓取"
    anti_blocking:
      - "User-Agent轮换池(20+ desktop/mobile UA)"
      - "代理轮换(可选HTTP/SOCKS5代理池,支持按源配置)"
      - "请求间隔抖动(base_delay ± 30%)"
      - "失败重试指数退避(max_retries=3, backoff_factor=2)"

  ai_providers:
    mode: "optional_upgrade"
    default_provider: "DeepSeek"  # 默认使用DeepSeek (成本最低)
    supported:
      - provider: "DeepSeek"
        models: ["deepseek-chat"]
        endpoint: "https://api.deepseek.com/v1"
        cost: "$0.14/1M tokens (input), $0.28/1M tokens (output)"
        priority: 1
      - provider: "OpenAI"
        models: ["gpt-4-turbo", "gpt-3.5-turbo"]
        endpoint: "https://api.openai.com/v1"
        cost: "$0.50/1M tokens (gpt-3.5-turbo)"
        priority: 2
      - provider: "Anthropic Claude"
        models: ["claude-3-opus", "claude-3-sonnet"]
        endpoint: "https://api.anthropic.com/v1"
        cost: "$3.00/1M tokens (claude-3-sonnet)"
        priority: 3
      - provider: "Alibaba Qwen"
        models: ["qwen-turbo", "qwen-plus"]
        endpoint: "https://dashscope.aliyuncs.com/api/v1"
        cost: "¥0.8/1M tokens (qwen-turbo)"
        priority: 4
      - provider: "Google Gemini"
        models: ["gemini-1.5-pro", "gemini-1.5-flash"]
        endpoint: "https://generativelanguage.googleapis.com/v1"
        priority: 5
      - provider: "Cohere"
        models: ["command-r", "command-r-plus"]
        endpoint: "https://api.cohere.ai/v1"
        priority: 6
    routing:
      strategy: "cost_priority_with_fallback"
      rules:
        - "primary: DeepSeek deepseek-chat (默认,成本最低$0.14/1M)"
        - "fallback_1: GPT-3.5-turbo (速度快,成本适中$0.50/1M)"
        - "fallback_2: Claude-3-sonnet (质量高,成本较高$3.00/1M)"
      budget_guard:
        daily_cap: "{{budget_per_day}} USD"
        alert_threshold: "80%"
        action: "达到100%时切换到无AI模式(保留原文)"
    response_metadata:
      mandatory_fields:
        - "is_ai_generated: true"
        - "model_info: {model: str, version: str, timestamp: ISO8601}"
      injection_point: "summary表INSERT时自动注入,不可为空"

  storage:
    mode:
      structured_db: "{{storage_mode}}"  # postgres | sqlite
      object_store: "local"  # local | s3
      cache: "redis"  # redis | none

    adapters:
      db:
        postgres:
          dsn: "postgresql+asyncpg://{{db_user}}:{{db_pass}}@{{db_host}}:5432/{{db_name}}"
          pool: "min=5, max=20, timeout=30s"
          migrations: "alembic"
        sqlite:
          path: "data/llm_daily_report.db"
          wal_mode: true
          journal_mode: "WAL"
          pool: "aiosqlite connection pool (max=10)"

      object_store:
        local:
          base_path: "data/objects/"
          structure: "{type}/{date}/{sha256[:2]}/{sha256[2:4]}/{sha256}.{ext}"
        s3:
          endpoint: "{{s3_endpoint}}"
          bucket: "{{s3_bucket}}"
          region: "{{s3_region}}"
          access_key: "{{s3_access_key}}"
          secret_key: "{{s3_secret_key}}"
          acl: "private"
          structure: "reports/{date}/report_{timestamp}.{ext}"

      cache:
        redis:
          url: "redis://{{redis_host}}:6379/0"
          ttl:
            article_content: "24h"
            api_response: "5min"
            wordcloud_data: "1h"

    data_access:
      pattern: "ports_and_adapters + repository"
      repositories:
        - SourcesRepository:
            methods: ["get_all()", "get_by_id()", "create()", "update_health()", "get_active(authority_min)"]
        - ArticlesRepository:
            methods: ["create_batch()", "get_by_url()", "get_by_time_window(start, end)", "deduplicate(hash)"]
        - SummariesRepository:
            methods: ["create()", "get_by_article_id()", "batch_create_with_ai_metadata()"]
        - ReportsRepository:
            methods: ["create()", "get_by_date()", "get_latest()", "generate_pdf()"]
        - AuditRepository:
            methods: ["log_run()", "export_csv(start, end, filters)", "get_cost_summary()"]
      interface: "抽象基类IRepository,每个adapter实现具体方法"

    cutover_policy:
      phase_1_shadow_read:
        action: "双写postgres+sqlite,读postgres,异步对比结果"
        duration: "7天"
        validation: "数据一致性校验(SHA-256 hash对比),差异率<0.1%"
      phase_2_dual_write:
        action: "双写持续,主读切换为sqlite"
        duration: "3天"
        rollback: "发现问题立即切回postgres读"
      phase_3_switch_read:
        action: "仅写sqlite,postgres保持同步但不读取"
        duration: "7天"
        verification: "业务指标(报告生成成功率/API响应时间)无劣化"
      phase_4_retire_old:
        action: "停止postgres写入,封存为备份"
        backup: "pg_dump导出归档至S3"

    naming_conventions:
      articles: "objects/articles/{YYYY-MM-DD}/{sha256[:2]}/{sha256[2:]}.json"
      reports: "objects/reports/{YYYY-MM-DD}/report_{timestamp}.html"
      checksums: "每个对象存储时计算SHA-256,存入DB metadata字段"

    backups:
      database:
        postgres: "每日02:00 UTC pg_dump,保留30天,存S3"
        sqlite: "每日02:00 UTC文件副本,保留30天,rsync到备份盘"
      object_store:
        local: "每周日rsync到异地存储"
        s3: "启用版本控制 + lifecycle policy(90天后迁移至Glacier)"

  publishing:
    formats:
      html:
        template: "Jinja2模板,响应式设计(移动端适配)"
        features:
          - "双时标显示(UTC + CST北京时间)"
          - "超窗内容标注⏰图标"
          - "AI生成内容标注🤖角标 + model_info悬停提示"
          - "词云可视化(ECharts.js)"
      pdf:
        renderer: "{{pdf_renderer}}"  # playwright | weasyprint
        playwright:
          engine: "Chromium headless打印HTML为PDF"
          options: "A4纸张,边距20mm,打印背景色,页眉页脚"
        weasyprint:
          engine: "CSS Paged Media渲染"
          fonts: "嵌入Noto Sans CJK保证中文显示"
        consistency: "PDF与HTML使用相同Jinja2模板,确保版式一致"
      email:
        provider: "smtp.163.com"  # 网易邮箱 (NetEase Mail)
        config:
          smtp_host: "smtp.163.com"
          smtp_port: 587
          smtp_tls: true
          smtp_user: "{{smtp_user}}"  # 完整邮箱地址,如 example@163.com
          smtp_password: "{{smtp_auth_code}}"  # 授权码(非邮箱密码)
          from_address: "{{smtp_user}}"  # 发件地址与smtp_user相同
          from_name: "金融日报系统 Daily Report"
        features:
          - "HTML邮件嵌入报告摘要"
          - "附件PDF完整报告"
          - "退订链接(List-Unsubscribe header + 底部链接)"
          - "DKIM/SPF签名"

  frontend:
    stack: "Vite + React 18 + TypeScript + Tailwind CSS"
    components:
      wordcloud:
        library: "react-wordcloud (基于d3-cloud)"
        data_source: "GET /api/reports/{date}/wordcloud"
        features: "关键词大小反映频率,点击筛选相关新闻"
      console_params:
        form: "Formik + Yup校验"
        controls:
          - "intl_window_hours: Slider(12-48h)"
          - "intl_quota_total: Number Input(10-100)"
          - "high_authority_min_ratio: Slider(0%-100%)"
        persistence: "POST /api/config,存入DB config表"
      source_management:
        list: "DataTable显示sources表(name/url/region/authority_score/health_status)"
        add_source:
          form: "URL输入 + region下拉选择"
          validation: "POST /api/sources/validate → {reachable, structure_ok, suggested_authority}"
          action: "验证通过后POST /api/sources保存"
        health_indicator: "红绿灯图标(green: >80, yellow: 50-80, red: <50, gray: quarantine)"
      prompt_customization:
        editor: "Monaco Editor (VS Code编辑器组件)"
        templates:
          - "short_summary (60字摘要)"
          - "long_summary (200字摘要)"
          - "keywords_extraction (5-10关键词)"
        versioning: "保存时自动生成P-X.Y.Z版本号,MINOR递增"
        preview: "实时预览(调用AI API测试,不计入生产配额)"
      intl_latest_cards:
        layout: "Grid布局,首屏10条卡片"
        card_content:
          - "标题(支持双语并排,可配置)"
          - "信息源名称 + authority_score徽章"
          - "双时标(UTC灰色小字 + CST粗体)"
          - "60字摘要 + 🤖角标(如AI生成)"
          - "原文链接按钮"
        sorting: "published_at_utc DESC, authority_score DESC"

  observability:
    logging:
      format: "JSON结构化日志"
      fields: ["timestamp", "level", "module", "function", "message", "context"]
      library: "structlog"
      output: "stdout (容器环境) + 文件滚动(本地开发)"
    metrics:
      system: "Prometheus"
      exporter: "prometheus-client (Python)"
      metrics:
        - "crawl_requests_total (counter, labels: source, status)"
        - "crawl_duration_seconds (histogram, labels: source)"
        - "ai_api_calls_total (counter, labels: provider, model)"
        - "ai_api_cost_usd (gauge)"
        - "report_generation_duration_seconds (histogram)"
        - "intl_latest_coverage_ratio (gauge)"
        - "high_authority_ratio (gauge)"
      dashboards: "Grafana预设面板(抓取健康/成本趋势/覆盖率)"
    tracing:
      optional: "OpenTelemetry (可选,用于分布式追踪)"
      exporters: "Jaeger | Zipkin | Cloud Trace"
    audit_export:
      formats: ["CSV", "JSON Lines"]
      endpoint: "GET /api/audit/export?start={date}&end={date}&format={csv|json}"
      fields: ["timestamp", "sources_used", "items_count", "ai_calls", "cost_usd", "coverage_ratio", "authority_ratio"]

architecture:
  style: "pipeline + plugin"
  rationale: "管道架构支持各阶段独立测试与替换,插件化允许动态加载信息源解析器与AI提供商"

  modules:
    ingest:
      responsibilities: "从sources表加载活跃源,并发抓取RSS/HTML,Playwright渲染JS页面"
      inputs: "sources (enabled=true, health_status>quarantine)"
      outputs: "raw_articles (url, content_raw, published_at_original, source_id)"
      plugins: "RSSParser, HTMLParser, PlaywrightRenderer (按source.type选择)"

    clean:
      responsibilities: "提取正文,移除广告/导航/版权,标准化时间戳为UTC"
      inputs: "raw_articles"
      outputs: "articles (content_clean, published_at_utc, region)"
      libraries: "newspaper3k | trafilatura (正文提取), dateutil (时间解析)"

    dedup:
      responsibilities: "三层去重: SHA-256哈希 → 语义嵌入(cosine>{{semantic_similarity_threshold}}) → 主题聚类"
      inputs: "articles"
      outputs: "unique_articles (deduplicated)"
      methods:
        - "layer_1: 全文SHA-256哈希,完全相同内容仅保留最早发布的"
        - "layer_2: sentence-transformers嵌入(model: all-MiniLM-L6-v2),余弦相似度>{{semantic_similarity_threshold}}视为重复,保留authority_score最高的"
        - "layer_3: DBSCAN主题聚类(eps={{dedup_clustering_eps}}),同簇内保留代表性文章(最早发布 + 最高authority)"

    relevance:
      responsibilities: "基于关键词/地理区域/主题分类筛选相关文章"
      inputs: "unique_articles"
      outputs: "relevant_articles (is_relevant=true)"
      filters:
        - "关键词匹配(金融/货币/央行/市场/贸易等)"
        - "地理区域(US/EU/APAC/JP优先,排除无关地区)"
        - "主题分类(ML分类器或规则引擎,保留finance/economy/policy类)"

    authority_scoring:
      responsibilities: "计算并更新信息源权威度分数,支持EMA平滑与人工校准"
      inputs: "sources, articles (历史表现)"
      outputs: "sources.authority_score (0-100)"
      algorithm:
        - "S1: 基础分数(预设,Bloomberg=95, 新源=50)"
        - "S2: 成功率(success_rate × 20)"
        - "S3: 延迟惩罚((1 - avg_latency/10s) × 10)"
        - "S4: 内容质量(用户投诉率倒数 × 15)"
        - "S5: 时效性(平均发布延迟 < 1h加分)"
        - "S6: 引用权威(被其他高权威源引用次数 × 5)"
        - "S7: EMA平滑(新分数 = 0.7 × 旧分数 + 0.3 × 当前计算分数)"
      override: "允许管理员手动设置authority_override字段(非0时覆盖算法分数)"
      recalculation: "每日02:00 UTC后台任务重新计算"

    summarize:
      responsibilities: "调用AI API生成摘要与关键词,记录model_info"
      inputs: "relevant_articles"
      outputs: "summaries (summary_text, keywords, importance, is_ai_generated, model_info)"
      prompts:
        short_summary: "请用60个汉字以内总结以下金融新闻,保留关键数字与机构名称: {content_clean}"
        long_summary: "请用200字详细总结以下金融新闻,包含背景与影响分析: {content_clean}"
        keywords: "提取5-10个关键词,优先金融术语与机构名: {content_clean}"
      versioning: "提示词版本存储于prompts表(version: P-X.Y.Z, created_at)"
      ai_metadata_injection: "summary.model_info = {model: 'gpt-4', version: '0613', timestamp: '2025-10-22T03:15:00Z'}"

    compose:
      responsibilities: "组装国际速览,应用ranking与quota规则"
      inputs: "summaries, articles, sources"
      outputs: "intl_latest (排序后的intl_item数组)"
      ranking_and_quota:
        window: "{{intl_window_hours}}h (默认24h)"
        order: "published_at_utc DESC, authority_score DESC, topic_bucket ASC"
        quotas:
          total: "{{intl_quota_total}} (默认50)"
          per_source_cap: 2
          high_authority_min_ratio: "{{high_authority_min_ratio}} (默认0.7)"
        enforcement:
          - "优先选择T-24h内,authority_score≥80的源,直到满足high_authority_min_ratio"
          - "每个源最多贡献2条(per_source_cap),防止单源垄断"
          - "不足quota时回填T-48h内容,标注out_of_primary_window=true"
        fallback: "若T-48h仍不足,允许降低至T-72h,标注'⏰超窗72h'"

    export:
      responsibilities: "生成HTML/PDF/邮件,发布报告"
      inputs: "report (包含intl_latest, wordcloud, sections)"
      outputs: "HTML文件, PDF文件, 邮件发送状态"
      templates: "Jinja2模板(base.html → report.html → email.html)"
      ai_labeling: "模板中检查is_ai_generated=true时自动插入🤖角标与model_info悬停框"

    admin_ui:
      responsibilities: "提供Web界面管理信息源/参数/提示词"
      endpoints:
        - "GET /admin/sources → 源列表页面"
        - "POST /admin/sources/add → 新增源表单"
        - "POST /admin/sources/validate → 验证源可达性"
        - "GET /admin/config → 参数配置页面"
        - "POST /admin/config/update → 更新运行参数"
        - "GET /admin/prompts → 提示词编辑器"
        - "POST /admin/prompts/save → 保存新版本提示词"

    audit_metrics:
      responsibilities: "记录每次运行的审计日志,提供导出与可视化"
      log_entry:
        fields: ["run_id", "timestamp", "config_snapshot", "sources_used", "items_count", "ai_calls", "cost_usd", "coverage_ratio", "authority_ratio", "errors"]
      export: "CSV/JSON导出,支持日期范围与过滤(source/cost_threshold)"
      visualization: "Grafana面板展示成本趋势/覆盖率/权威度时间序列"

data_contracts:
  source:
    fields:
      - id: "UUID primary key"
      - name: "VARCHAR(255) 信息源名称"
      - url: "TEXT 信息源URL"
      - type: "ENUM(rss, html, playwright) 解析类型"
      - region: "VARCHAR(10) 地理区域(US/EU/APAC/JP)"
      - authority_score: "INT(0-100) 权威度分数"
      - health_status: "ENUM(healthy, degraded, quarantine) 健康状态"
      - health_metrics: "JSONB {success_rate, avg_latency, last_error, error_count}"
      - last_crawled_at: "TIMESTAMP 最后抓取时间"
      - enabled: "BOOLEAN 是否启用"
      - created_at: "TIMESTAMP 创建时间"

  article:
    fields:
      - id: "UUID primary key"
      - source_id: "UUID foreign key → sources.id"
      - region: "VARCHAR(10)"
      - title: "VARCHAR(500)"
      - url: "TEXT unique"
      - published_at_utc: "TIMESTAMP 发布时间(UTC)"
      - content_raw: "TEXT 原始HTML/文本"
      - content_clean: "TEXT 清洗后正文"
      - content_hash: "CHAR(64) SHA-256哈希"
      - embedding: "VECTOR(384) 语义嵌入向量(可选,用于去重)"
      - topic_bucket: "VARCHAR(50) 主题分类(finance/economy/policy)"
      - is_relevant: "BOOLEAN 是否相关"
      - created_at: "TIMESTAMP"

  summary:
    fields:
      - id: "UUID primary key"
      - article_id: "UUID foreign key → articles.id"
      - summary_text: "TEXT 摘要文本(60-200字)"
      - keywords: "TEXT[] 关键词数组"
      - importance: "INT(1-10) 重要性评分"
      - is_ai_generated: "BOOLEAN 必须为true"
      - model_info: "JSONB {model, version, timestamp} 非空"
      - prompt_version: "VARCHAR(20) P-X.Y.Z版本号"
      - created_at: "TIMESTAMP"

  intl_item:
    fields:
      - id: "UUID primary key"
      - article_id: "UUID foreign key → articles.id"
      - summary_id: "UUID foreign key → summaries.id"
      - title: "VARCHAR(200) 标准化标题"
      - source_name: "VARCHAR(255)"
      - published_at_utc: "TIMESTAMP"
      - published_at_local: "TIMESTAMP CST北京时间"
      - summary_60w: "TEXT 60字摘要"
      - url: "TEXT 原文链接"
      - is_ai_generated: "BOOLEAN"
      - model_info: "JSONB nullable"
      - out_of_primary_window: "BOOLEAN 是否超窗"
      - authority_score: "INT 信息源权威度快照"

  report:
    fields:
      - id: "UUID primary key"
      - date: "DATE CST日期"
      - intl_latest: "JSONB intl_item数组"
      - sections: "JSONB 按主题分组的章节"
      - wordcloud: "JSONB {keywords: [{word, frequency}]}"
      - audit_ref: "UUID foreign key → audit_logs.id"
      - html_path: "TEXT 对象存储路径"
      - pdf_path: "TEXT nullable"
      - generated_at: "TIMESTAMP"
      - published: "BOOLEAN 是否已发布"

  audit_log:
    fields:
      - id: "UUID primary key"
      - run_id: "VARCHAR(50) 运行标识"
      - timestamp: "TIMESTAMP 运行时间"
      - config_snapshot: "JSONB 运行时配置"
      - sources_used: "TEXT[] 使用的信息源ID"
      - items_count: "INT 生成条目数"
      - ai_calls: "INT AI调用次数"
      - cost_usd: "DECIMAL(10,4) 成本"
      - coverage_ratio: "DECIMAL(5,4) T-24h覆盖率"
      - authority_ratio: "DECIMAL(5,4) 首屏高权威占比"
      - errors: "JSONB 错误日志"
      - duration_seconds: "INT 运行耗时"

db_schema_additions:
  sources_table:
    new_columns:
      - authority_override: "INT DEFAULT 0 (非0时覆盖算法分数)"
      - last_scored_at: "TIMESTAMP 最后评分时间"
      - health_metrics: "JSONB {success_rate, avg_latency, last_error, error_count_24h}"
    indexes:
      - "CREATE INDEX idx_sources_authority ON sources(authority_score DESC)"
      - "CREATE INDEX idx_sources_enabled ON sources(enabled) WHERE enabled=true"

  articles_table:
    new_columns:
      - content_hash: "CHAR(64) UNIQUE SHA-256哈希"
      - embedding: "VECTOR(384) (可选,需pg_vector扩展)"
      - topic_bucket: "VARCHAR(50) 主题分类"
    indexes:
      - "CREATE INDEX idx_articles_published ON articles(published_at_utc DESC)"
      - "CREATE INDEX idx_articles_hash ON articles(content_hash)"
      - "CREATE INDEX idx_articles_source_time ON articles(source_id, published_at_utc)"

  config_table:
    purpose: "存储运行参数配置"
    schema:
      - key: "VARCHAR(100) PRIMARY KEY"
      - value: "TEXT"
      - updated_at: "TIMESTAMP"
      - updated_by: "VARCHAR(100) 操作用户"
    examples:
      - "{key: 'intl_window_hours', value: '24'}"
      - "{key: 'intl_quota_total', value: '50'}"
      - "{key: 'high_authority_min_ratio', value: '0.7'}"

  prompts_table:
    purpose: "提示词版本管理"
    schema:
      - id: "UUID PRIMARY KEY"
      - name: "VARCHAR(100) 提示词名称(short_summary/long_summary/keywords)"
      - version: "VARCHAR(20) P-X.Y.Z版本号"
      - template: "TEXT 提示词模板"
      - created_at: "TIMESTAMP"
      - created_by: "VARCHAR(100)"
      - is_active: "BOOLEAN 是否当前使用版本"

api_surface:
  endpoints:
    - method: "GET"
      path: "/api/intl-latest"
      params: "?window={{intl_window_hours}}h&limit={{intl_quota_total}}&authority_min=80"
      response: "intl_item[] (排序后的国际速览列表)"
      auth: "optional (公开只读)"

    - method: "GET"
      path: "/api/reports/{date}"
      params: "date: YYYY-MM-DD (CST日期)"
      response: "report对象(含intl_latest/wordcloud/sections)"
      auth: "optional"

    - method: "GET"
      path: "/api/reports/{date}/pdf"
      params: "date: YYYY-MM-DD (CST日期)"
      response: "application/pdf (下载PDF文件)"
      auth: "optional"

    - method: "POST"
      path: "/api/reports/generate"
      body: "{date: 'YYYY-MM-DD', force: boolean}"
      response: "{report_id, status, generated_at}"
      auth: "required (管理员)"

    - method: "GET"
      path: "/api/sources"
      params: "?region=US&enabled=true&authority_min=50"
      response: "source[] (信息源列表)"
      auth: "optional"

    - method: "POST"
      path: "/api/sources"
      body: "{name, url, type, region, initial_authority_score}"
      response: "{source_id, created_at}"
      auth: "required (管理员)"

    - method: "POST"
      path: "/api/sources/validate"
      body: "{url, type}"
      response: "{reachable: boolean, structure_ok: boolean, suggested_authority: int, region: str, errors: []}"
      auth: "required (管理员)"

    - method: "GET"
      path: "/api/audit/{date}"
      params: "date: YYYY-MM-DD"
      response: "audit_log对象"
      auth: "required (管理员)"

    - method: "GET"
      path: "/api/audit/export"
      params: "?start=YYYY-MM-DD&end=YYYY-MM-DD&format=csv&source_filter=bloomberg"
      response: "text/csv | application/json"
      auth: "required (管理员)"

    - method: "GET"
      path: "/api/metrics"
      response: "prometheus格式指标文本"
      auth: "optional (Prometheus抓取)"

execution_plan:
  phase_0_foundation:
    duration: "3-4天"
    goals: "基础设施搭建,契约定稿,存储与监控就绪"
    tasks:
      - "T001: 创建Git仓库,配置CI/CD(GitHub Actions/GitLab CI)"
      - "T002: 编写数据契约JSON Schema (source/article/summary/intl_item/report/audit_log)"
      - "T003: 设计插件接口 (ISourceParser, IAIProvider, IStorageAdapter)"
      - "T004: 初始化数据库(PostgreSQL/SQLite),运行alembic迁移"
      - "T005: 部署Redis实例(Docker Compose本地 | ElastiCache生产)"
      - "T006: 配置代理池与UA轮换列表(20+ User-Agents,可选HTTP代理)"
      - "T007: 搭建Prometheus + Grafana监控栈,定义基础面板"
      - "T008: 实现结构化日志(structlog),输出JSON格式"
    deliverables:
      - "Git仓库含README/架构图/数据契约文档"
      - "DB迁移脚本(0001_initial_schema.sql)"
      - "Redis连接配置与健康检查"
      - "CI/CD管道运行成功(lint + 单元测试)"
    acceptance:
      - "DB表创建成功,外键约束生效"
      - "Redis可读写,TTL策略验证通过"
      - "Prometheus抓取到基础系统指标(CPU/内存)"

  phase_1_pipeline:
    duration: "5-6天"
    goals: "实现核心管道,抓取→清洗→去重→权威度评分→国际速览生成"
    tasks:
      - "T009: 实现ingest模块(并发抓取RSS/HTML,Playwright渲染)"
      - "T010: 实现clean模块(正文提取newspaper3k,时间标准化dateutil)"
      - "T011: 实现dedup模块(SHA-256哈希 + sentence-transformers嵌入 + DBSCAN聚类)"
      - "T012: 实现relevance模块(关键词匹配 + 地理区域筛选)"
      - "T013: 实现authority_scoring模块(S1-S7算法,EMA平滑,人工override)"
      - "T014: 实现compose模块(ranking与quota规则,T-24h窗口 + T-48h回填)"
      - "T015: 测试数据准备(10个模拟信息源,100篇测试文章)"
      - "T016: 端到端集成测试(从抓取到生成intl_latest数组)"
    deliverables:
      - "Pipeline各模块单元测试覆盖率>80%"
      - "集成测试通过:输入10源100篇→输出50条intl_latest"
      - "首屏高权威占比≥70%验证通过"
      - "T-24h覆盖率≥95%验证通过"
    acceptance:
      - "并发抓取10源<30s完成"
      - "去重率达到预期(语义重复<5%)"
      - "权威度评分稳定(重复运行分数波动<5分)"
      - "回填逻辑触发正确(T-24h不足时自动回填T-48h)"

  phase_2_publish_ui:
    duration: "4-5天"
    goals: "实现HTML/PDF/邮件发布,前端UI四项功能"
    tasks:
      - "T017: 实现export模块(Jinja2模板,HTML生成,双时标/超窗/AI角标)"
      - "T018: 集成PDF渲染器(Playwright print_pdf | WeasyPrint)"
      - "T019: 实现邮件发送(SMTP配置,HTML邮件 + PDF附件,退订链接)"
      - "T020: 前端搭建(Vite + React + Tailwind,路由配置)"
      - "T021: 实现国际速览首屏卡片(Grid布局,双时标,🤖角标)"
      - "T022: 实现词云可视化(react-wordcloud,数据从/api/reports/{date}/wordcloud)"
      - "T023: 实现控制台参数配置(Formik表单,Slider/Input组件,POST /api/config)"
      - "T024: 实现信息源管理(列表/新增/验证,DataTable + Modal)"
      - "T025: 实现提示词定制(Monaco编辑器,版本管理,预览功能)"
    deliverables:
      - "HTML报告样例(包含10条新闻,词云,双时标)"
      - "PDF报告与HTML版式一致(A4纸张,页眉页脚)"
      - "前端四项功能演示视频(词云/参数/源管理/提示词)"
      - "邮件测试成功(收件箱收到HTML邮件 + PDF附件)"
    acceptance:
      - "HTML/PDF双时标显示正确(UTC灰色 + CST粗体)"
      - "AI角标🤖悬停显示model_info"
      - "超窗内容标注⏰图标"
      - "前端参数修改后重新生成报告反映新配置"
      - "新增信息源验证返回可达性 + 建议权威度"

  phase_3_ai_optional:
    duration: "3-4天"
    goals: "集成AI提供商,实现路由与预算守门,生成摘要"
    tasks:
      - "T026: 实现AI路由器(支持OpenAI/Claude/Gemini/DeepSeek/Qwen/Cohere)"
      - "T027: 实现预算守门(daily_cap监控,达到80%告警,100%降级)"
      - "T028: 编写摘要提示词模板(short_summary 60字,long_summary 200字,keywords)"
      - "T029: 实现summarize模块(调用AI API,回写is_ai_generated + model_info)"
      - "T030: 测试AI降级策略(模拟预算耗尽,验证跳过摘要保留原文)"
      - "T031: 成本统计与可视化(Grafana面板展示每日AI成本趋势)"
    deliverables:
      - "AI路由器支持6个提供商,切换无缝"
      - "预算守门触发告警(模拟达到80%阈值)"
      - "摘要生成成功,model_info字段非空"
      - "HTML/PDF中🤖角标显示正确模型信息"
    acceptance:
      - "DeepSeek/Qwen优先调用(成本最低)"
      - "主提供商失败时自动切换fallback"
      - "预算100%时跳过AI,报告仍正常生成(无摘要)"
      - "所有AI生成内容100%标注is_ai_generated=true"

  phase_4_observability:
    duration: "3-4天"
    goals: "完善监控指标,审计导出,灰度发布与A/B测试"
    tasks:
      - "T032: 实现覆盖率指标(T-24h条目占比,Prometheus gauge)"
      - "T033: 实现回填指标(T-48h回填次数,counter)"
      - "T034: 实现近重复指标(语义相似度>0.85对数,gauge)"
      - "T035: 实现权威度指标(首屏高权威占比,gauge)"
      - "T036: 实现成本可视化(每日AI成本折线图,Grafana)"
      - "T037: 实现审计导出(GET /api/audit/export,支持CSV/JSON,日期范围过滤)"
      - "T038: 灰度发布测试(10%流量使用新权威度算法,对比旧算法)"
      - "T039: A/B测试框架(前端参数A/B,统计用户点击率)"
    deliverables:
      - "Grafana面板包含5个核心指标(覆盖率/回填/重复/权威/成本)"
      - "审计导出CSV包含30天数据,字段完整"
      - "灰度发布无业务影响(新旧算法分数差异<10分)"
      - "A/B测试统计显著性验证通过(p<0.05)"
    acceptance:
      - "所有指标实时更新(延迟<1分钟)"
      - "审计导出文件可用Excel打开,无乱码"
      - "灰度流量路由正确(10% vs 90%)"
      - "A/B测试结果可导出报告"

acceptance_gate:
  timeliness:
    metric: "CST 08:00准时率"
    target: "99% (30天内最多1次延迟)"
    verification: "统计过去30天报告generated_at时间戳,计算准时率"

  coverage:
    metric: "T-24h覆盖率"
    target: "95%"
    verification: "intl_latest数组中,published_at_utc在(now-24h, now]区间的条目占比"

  authority:
    metric: "首屏高权威占比"
    target: "{{high_authority_min_ratio}} (默认70%)"
    verification: "intl_latest前10条中,authority_score≥80的条目数 / 10"

  ai_labeling:
    metric: "AI内容标注完整性"
    target: "100%"
    verification: "遍历所有is_ai_generated=true的summary,检查model_info非空且包含model/version/timestamp"

  frontend_features:
    metric: "前端四项功能可用性"
    target: "100%"
    verification:
      - "词云渲染成功,关键词≥20个"
      - "参数配置保存后重新生成报告反映新值"
      - "新增信息源验证返回可达性与建议权威度"
      - "提示词编辑保存后生成新版本P-X.Y.Z"

  storage_cutover:
    metric: "存储切换演练通过"
    target: "业务无改代码"
    phases:
      - phase_1_shadow_read: "双写postgres+sqlite,读postgres,对比一致性>99.9%"
      - phase_2_dual_write: "双写持续,主读切换sqlite,业务指标无劣化"
      - phase_3_switch_read: "仅写sqlite,postgres封存备份,运行7天无问题"
      - phase_4_retire_old: "停止postgres写入,pg_dump备份至S3"
    rollback: "任何阶段发现问题,立即切回postgres,业务不中断"
    verification: "切换前后报告内容SHA-256哈希一致,API响应时间无明显增加"

variables:
  budget_per_day: "{{budget_per_day}}"  # 例如: 100 USD
  smtp_user: "{{smtp_user}}"  # 网易邮箱地址,如 example@163.com
  smtp_auth_code: "{{smtp_auth_code}}"  # 网易邮箱授权码(非密码,在邮箱设置中生成)
  storage_mode: "{{storage_mode}}"  # postgres | sqlite
  pdf_renderer: "{{pdf_renderer}}"  # playwright | weasyprint (推荐playwright)
  intl_window_hours: "{{intl_window_hours}}"  # 默认24
  intl_quota_total: "{{intl_quota_total}}"  # 默认50
  high_authority_min_ratio: "{{high_authority_min_ratio}}"  # 默认0.7
```

---

## Next Steps

使用 `/speckit.tasks` 生成详细任务清单,按Phase 0-4分解为可执行任务列表。
