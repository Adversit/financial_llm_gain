# Tasks: International Financial News Aggregation System

**Input**: Design documents from `/specs/001-intl-news-aggregation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are OPTIONAL - not included as specification does not explicitly request TDD approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Path Conventions

- **Backend**: `src/` at repository root
- **Frontend**: `frontend/src/`
- **Tests**: `tests/`
- **Migrations**: `alembic/versions/`
- **Config**: `config/`
- **Data**: `data/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan (src/, frontend/, tests/, alembic/, config/, data/)
- [ ] T002 Initialize Python 3.11+ project with pyproject.toml (FastAPI, httpx, asyncio, feedparser, beautifulsoup4, lxml, playwright, alembic, asyncpg/aiosqlite, redis, prometheus-client, structlog)
- [ ] T003 [P] Configure Git repository with .gitignore (Python, Node, IDE files, data/, .env)
- [ ] T004 [P] Setup CI/CD pipeline in .github/workflows/ci.yml (lint, test, build)
- [ ] T005 [P] Initialize frontend project with Vite + React + TypeScript + Tailwind CSS in frontend/
- [ ] T006 [P] Configure ESLint + Prettier for frontend in frontend/.eslintrc.json
- [ ] T007 Create README.md with project overview, setup instructions, architecture diagram
- [ ] T008 [P] Setup Docker Compose for local development in docker-compose.yml (postgres/sqlite, redis, prometheus, grafana)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Define database schema in alembic/versions/0001_initial_schema.py (sources, articles, summaries, intl_items, reports, audit_logs, config, prompts tables)
- [ ] T010 [P] Create storage adapters interface in src/storage/adapters/base.py (IRepository abstract base class)
- [ ] T011 [P] Implement PostgreSQL adapter in src/storage/adapters/postgres.py (asyncpg connection pool, DSN config)
- [ ] T012 [P] Implement SQLite adapter in src/storage/adapters/sqlite.py (aiosqlite pool, WAL mode)
- [ ] T013 [P] Implement local object store adapter in src/storage/adapters/local_store.py (file path structure, SHA-256 naming)
- [ ] T014 [P] Implement Redis cache adapter in src/storage/adapters/redis_cache.py (connection, TTL config)
- [ ] T015 Create repository implementations in src/repositories/ (sources_repo.py, articles_repo.py, summaries_repo.py, reports_repo.py, audit_repo.py)
- [ ] T016 [P] Implement User-Agent rotation pool in src/crawling/ua_pool.py (20+ desktop/mobile UAs)
- [ ] T017 [P] Implement robots.txt parser in src/crawling/politeness.py (robotparser library integration)
- [ ] T018 [P] Setup structured logging in src/observability/logging.py (structlog JSON output)
- [ ] T019 [P] Setup Prometheus metrics exporter in src/observability/metrics.py (prometheus-client, custom metrics)
- [ ] T020 Create FastAPI app skeleton in src/main.py (app initialization, CORS, middleware)
- [ ] T021 [P] Implement configuration management in src/config/settings.py (environment variables, storage_mode, redis_url, db_dsn)
- [ ] T022 Run database migrations with alembic upgrade head

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 每日国际金融速览生成 (Priority: P1) 🎯 MVP

**Goal**: 系统每日自动聚合国际金融新闻,生成包含双时标(UTC+CST)、信息源与60字摘要的速览列表,优先展示高权威源内容

**Independent Test**: 配置测试信息源(3个高权威+2个普通权威),运行报告生成,验证输出包含至少30条新闻且首屏高权威占比≥70%

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create Source model in src/models/source.py (id, name, url, type, region, authority_score, health_status, health_metrics, last_crawled_at, enabled, created_at)
- [ ] T024 [P] [US1] Create Article model in src/models/article.py (id, source_id, region, title, url, published_at_utc, content_raw, content_clean, content_hash, topic_bucket, is_relevant, created_at)
- [ ] T025 [P] [US1] Create IntlItem model in src/models/intl_item.py (id, article_id, summary_id, title, source_name, published_at_utc, published_at_local, summary_60w, url, out_of_primary_window, authority_score)
- [ ] T026 [P] [US1] Create Report model in src/models/report.py (id, date, intl_latest, sections, wordcloud, audit_ref, html_path, pdf_path, generated_at, published)
- [ ] T027 [US1] Implement RSS parser plugin in src/crawling/parsers/rss_parser.py (feedparser integration, extract title/url/published_at/content)
- [ ] T028 [P] [US1] Implement HTML parser plugin in src/crawling/parsers/html_parser.py (BeautifulSoup4 + lxml, extract正文)
- [ ] T029 [P] [US1] Implement Playwright renderer plugin in src/crawling/parsers/playwright_renderer.py (async Chromium headless, JS-heavy sites)
- [ ] T030 [US1] Implement ingest module in src/pipeline/ingest.py (load active sources, concurrent fetch with asyncio.gather + semaphore, robots.txt compliance, ETag/Last-Modified handling)
- [ ] T031 [US1] Implement clean module in src/pipeline/clean.py (newspaper3k/trafilatura正文提取, dateutil时间标准化为UTC, 移除广告/导航)
- [ ] T031a [US1] Implement timestamp validation in src/pipeline/clean.py (detect future timestamps: published_at_utc > now, reject article; warn if published_at_utc < now - 7 days, log to audit as stale content; covers constitution RISK-002 mitigation)
- [ ] T032 [US1] Implement dedup module in src/pipeline/dedup.py (layer 1: SHA-256哈希去重, layer 2: sentence-transformers语义嵌入cosine>{{semantic_similarity_threshold}}去重, layer 3: DBSCAN主题聚类eps={{dedup_clustering_eps}}, load thresholds from config table)
- [ ] T033 [P] [US1] Implement relevance module in src/pipeline/relevance.py (关键词匹配金融/央行/市场, 地理区域US/EU/APAC/JP筛选)
- [ ] T034 [US1] Implement authority scoring module in src/pipeline/authority_scoring.py (S1-S7算法: 基础分/成功率/延迟惩罚/内容质量/时效性/引用权威/EMA平滑, authority_override支持)
- [ ] T035 [US1] Implement compose module in src/pipeline/compose.py (ranking: published_at_utc DESC + authority_score DESC + topic_bucket ASC, quotas: total/per_source_cap/high_authority_min_ratio enforcement, T-48h fallback with out_of_primary_window标注)
- [ ] T036 [US1] Implement time window filtering in src/pipeline/compose.py (intl_window_hours默认24h, T-24h优先, 不足回填T-48h)
- [ ] T037 [US1] Implement dual timestamp conversion in src/utils/timezone.py (UTC存储, CST北京时间展示, ISO 8601格式, UTC+8 Asia/Shanghai)
- [ ] T038 [US1] Create API endpoint GET /api/intl-latest in src/api/endpoints/intl_latest.py (query params: window, limit, authority_min, return intl_item array)
- [ ] T039 [US1] Create API endpoint GET /api/reports/{date} in src/api/endpoints/reports.py (return report object with intl_latest/wordcloud/sections)
- [ ] T040 [US1] Create API endpoint POST /api/reports/generate in src/api/endpoints/reports.py (admin auth, trigger report generation for given date)
- [ ] T041 [US1] Implement HTML template for report in src/templates/report.html (Jinja2, 响应式设计, 双时标显示UTC+CST, 超窗标注⏰)
- [ ] T042 [US1] Implement report export service in src/services/export_service.py (generate HTML from template, save to object store)
- [ ] T042a [US1] Implement compliance validator in src/services/compliance_validator.py (scan output for prohibited terms: 建议买入|卖出|目标价|预期收益|评级上调|下调|交易信号, raise ComplianceException if found, integrate into export_service.py before HTML generation, covers FR-020)
- [ ] T043 [US1] Create scheduled job for daily report generation in src/jobs/daily_report_job.py (cron: UTC 23:00触发, 生成次日CST报告, 确保CST 08:00前完成)
- [ ] T044 [US1] Load seed sources from data/seed_sources.yaml (35个中文源: 政府官方6个90-95分/主流财经4个75-88分/金融科技6个65-78分/AI科技6个70-78分/科技综合7个68-75分/科技应用3个58-65分/学术2个70-75分/国际1个70分, 包含RSS/RSSHub/自定义爬虫三种类型, 需实现CSRCCrawler和YicaiCrawler)

**Checkpoint**: User Story 1 (MVP) should be fully functional and testable independently - daily international financial news aggregation with dual timestamps and authority-based ranking

---

## Phase 4: User Story 2 - AI摘要生成与透明标注 (Priority: P2)

**Goal**: 使用AI模型生成60字中文摘要与关键词,所有AI内容必须显示🤖角标与model_info

**Independent Test**: 提供5篇英文原文,调用AI API,验证summary对象包含summary_text/keywords/model_info,HTML显示🤖标注

### Implementation for User Story 2

- [ ] T045 [P] [US2] Create Summary model in src/models/summary.py (id, article_id, summary_text, keywords, importance, is_ai_generated, model_info, prompt_version, created_at)
- [ ] T046 [P] [US2] Create Prompt model in src/models/prompt.py (id, name, version, template, created_at, created_by, is_active)
- [ ] T047 [US2] Implement AI provider interface in src/ai/providers/base.py (IAIProvider abstract class: generate_summary, generate_keywords methods)
- [ ] T048 [P] [US2] Implement OpenAI provider in src/ai/providers/openai_provider.py (API client, gpt-4-turbo/gpt-3.5-turbo models)
- [ ] T049 [P] [US2] Implement Claude provider in src/ai/providers/claude_provider.py (Anthropic API, claude-3-opus/sonnet models)
- [ ] T050 [P] [US2] Implement Gemini provider in src/ai/providers/gemini_provider.py (Google API, gemini-1.5-pro/flash models)
- [ ] T051 [P] [US2] Implement DeepSeek provider in src/ai/providers/deepseek_provider.py (DeepSeek API, deepseek-chat model, DEFAULT PROVIDER, endpoint: https://api.deepseek.com/v1, cost: $0.14/1M input tokens)
- [ ] T052 [P] [US2] Implement Qwen provider in src/ai/providers/qwen_provider.py (Alibaba DashScope API, qwen-turbo/plus models)
- [ ] T053 [P] [US2] Implement Cohere provider in src/ai/providers/cohere_provider.py (Cohere API, command-r/command-r-plus models)
- [ ] T054 [US2] Implement AI router in src/ai/router.py (cost_priority_with_fallback strategy: DeepSeek deepseek-chat as PRIMARY default, GPT-3.5-turbo fallback1, Claude-3-sonnet fallback2, auto-switch on API failure or budget limit)
- [ ] T055 [US2] Implement budget guard in src/ai/budget_guard.py (daily_cap monitoring, 80% alert threshold, 100% switch to no-AI mode)
- [ ] T056 [US2] Create prompt templates in data/prompts/ (short_summary_v1.0.0.txt: "请用60个汉字以内总结...", keywords_v1.0.0.txt: "提取5-10个关键词...")
- [ ] T057 [US2] Implement summarize module in src/pipeline/summarize.py (call AI API, inject is_ai_generated=true + model_info={model, version, timestamp}, handle fallback on budget exceed)
- [ ] T058 [US2] Update HTML template in src/templates/report.html (add 🤖角标 for AI content, model_info悬停提示框)
- [ ] T059 [US2] Implement cost tracking in src/observability/metrics.py (ai_api_calls_total counter, ai_api_cost_usd gauge by provider/model)
- [ ] T060 [US2] Create Grafana dashboard for AI cost trends in config/grafana/dashboards/ai_costs.json (daily cost line chart, provider breakdown pie chart)

**Checkpoint**: User Story 2 complete - AI summarization with transparent labeling, multi-provider routing, and budget control

---

## Phase 5: User Story 3 - 前端管理控制台 (Priority: P3)

**Goal**: Web界面管理信息源/参数/提示词,新增源验证,参数修改持久化

**Independent Test**: 通过UI新增信息源验证可达性,修改参数重新生成报告反映新配置,编辑提示词生成新版本

### Implementation for User Story 3

- [ ] T061 [US3] Create Config model in src/models/config.py (key, value, updated_at, updated_by)
- [ ] T062 [P] [US3] Setup frontend routing in frontend/src/App.tsx (React Router: /admin/sources, /admin/config, /admin/prompts)
- [ ] T063 [P] [US3] Create API endpoint GET /api/sources in src/api/endpoints/sources.py (query params: region, enabled, authority_min, return source array)
- [ ] T064 [P] [US3] Create API endpoint POST /api/sources in src/api/endpoints/sources.py (admin auth, body: name/url/type/region/initial_authority_score, return source_id)
- [ ] T065 [P] [US3] Create API endpoint POST /api/sources/validate in src/api/endpoints/sources.py (admin auth, body: url/type, return: reachable/structure_ok/suggested_authority/region/errors)
- [ ] T066 [US3] Implement source validation service in src/services/source_validation_service.py (HTTP reachability check, RSS/HTML structure parse test, suggest authority based on domain/structure)
- [ ] T067 [P] [US3] Create frontend Sources管理页面 in frontend/src/pages/SourcesManagement.tsx (DataTable显示sources, health indicator红绿灯, 新增/编辑/禁用按钮)
- [ ] T068 [P] [US3] Create frontend Source验证Modal in frontend/src/components/SourceValidationModal.tsx (URL输入, region下拉, 点击验证显示reachable/suggested_authority, 确认保存)
- [ ] T069 [US3] Create API endpoint GET /api/config in src/api/endpoints/config.py (return all config key-value pairs)
- [ ] T070 [P] [US3] Create API endpoint POST /api/config in src/api/endpoints/config.py (admin auth, body: key/value, update config table)
- [ ] T071 [P] [US3] Create frontend参数配置页面 in frontend/src/pages/ConfigManagement.tsx (Formik form: intl_window_hours Slider 12-48h, intl_quota_total Number Input 10-100, high_authority_min_ratio Slider 0-100%, Yup validation)
- [ ] T072 [US3] Implement config persistence in src/services/config_service.py (load from config table, apply to pipeline at runtime)
- [ ] T073 [P] [US3] Create API endpoint GET /api/prompts in src/api/endpoints/prompts.py (return active prompts with versions)
- [ ] T074 [P] [US3] Create API endpoint POST /api/prompts in src/api/endpoints/prompts.py (admin auth, body: name/template, auto-generate P-X.Y.Z version MINOR increment, set is_active)
- [ ] T075 [P] [US3] Create frontend提示词编辑器 in frontend/src/pages/PromptEditor.tsx (Monaco Editor for template editing, version history list, preview button)
- [ ] T076 [US3] Implement prompt versioning service in src/services/prompt_service.py (SemVer P-X.Y.Z管理, MINOR递增on save, keep old versions with is_active=false)
- [ ] T077 [US3] Implement prompt preview in src/api/endpoints/prompts.py (POST /api/prompts/preview: call AI API with test article, return sample summary, don't count toward production quota)

**Checkpoint**: User Story 3 complete - full admin UI for sources/config/prompts management with validation and versioning

---

## Phase 6: User Story 4 - 词云可视化与审计导出 (Priority: P3)

**Goal**: 从报告提取关键词生成词云数据,提供审计日志导出CSV/JSON

**Independent Test**: 生成报告验证wordcloud包含≥20关键词,导出审计日志CSV包含完整字段

### Implementation for User Story 4

- [ ] T078 [P] [US4] Create AuditLog model in src/models/audit_log.py (id, run_id, timestamp, config_snapshot, sources_used, items_count, ai_calls, cost_usd, coverage_ratio, authority_ratio, errors, duration_seconds)
- [ ] T079 [US4] Implement wordcloud generator in src/services/wordcloud_service.py (TF-IDF extraction from article content, top 20-50 keywords with frequency, return {keywords: [{word, frequency}]})
- [ ] T080 [US4] Integrate wordcloud into compose module in src/pipeline/compose.py (call wordcloud_service, store in report.wordcloud JSONB field)
- [ ] T081 [P] [US4] Create API endpoint GET /api/reports/{date}/wordcloud in src/api/endpoints/reports.py (return wordcloud data for given report date)
- [ ] T082 [P] [US4] Create frontend词云可视化组件 in frontend/src/components/WordCloud.tsx (react-wordcloud library, fetch data from /api/reports/{date}/wordcloud, render with font size proportional to frequency, click keyword to filter related news)
- [ ] T083 [US4] Implement audit logging in src/pipeline/compose.py (create audit_log entry after report generation, record config_snapshot/sources_used/items_count/ai_calls/cost/coverage_ratio/authority_ratio/errors/duration, config_snapshot MUST include: intl_window_hours/intl_quota_total/high_authority_min_ratio/active_sources[]/prompt_version/semantic_similarity_threshold/dedup_eps for FR-016 compliance)
- [ ] T084 [P] [US4] Create API endpoint GET /api/audit/{date} in src/api/endpoints/audit.py (admin auth, return audit_log for given date)
- [ ] T085 [P] [US4] Create API endpoint GET /api/audit/export in src/api/endpoints/audit.py (admin auth, query params: start/end date, format csv|json, source_filter, return file download)
- [ ] T086 [US4] Implement audit export service in src/services/audit_export_service.py (query audit_logs by date range, apply filters, export to CSV with headers: timestamp/sources_used/items_count/ai_calls/cost_usd/coverage_ratio/authority_ratio, or JSON Lines)
- [ ] T087 [P] [US4] Create frontend审计导出页面 in frontend/src/pages/AuditExport.tsx (date range picker, format selector CSV/JSON, source filter dropdown, export button triggers /api/audit/export download)
- [ ] T088 [US4] Create Grafana dashboard for audit metrics in config/grafana/dashboards/audit_metrics.json (coverage_ratio time series, authority_ratio gauge, cost_usd line chart, sources_used bar chart)

**Checkpoint**: User Story 4 complete - wordcloud visualization and comprehensive audit export functionality

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T089 [P] Implement PDF generation in src/services/pdf_service.py (Playwright print_pdf或WeasyPrint, A4纸张, 边距20mm, 使用与HTML相同Jinja2模板确保版式一致, 嵌入Noto Sans CJK字体)
- [ ] T090 [P] Create API endpoint GET /api/reports/{date}/pdf in src/api/endpoints/reports.py (generate PDF, cache in object store, return application/pdf download)
- [ ] T091 [P] Implement email sending service in src/services/email_service.py (网易邮箱SMTP: smtp.163.com:587 TLS, use smtp_user + smtp_auth_code from config, HTML email with report summary, PDF attachment, List-Unsubscribe header, from_name: "金融日报系统 Daily Report")
- [ ] T092 [P] Create frontend国际速览首屏卡片 in frontend/src/pages/IntlLatest.tsx (Grid layout, 10 cards per screen, card content: title/source_name+authority_score徽章/双时标UTC+CST/summary_60w/🤖角标if AI/原文链接, sorting by published_at_utc DESC)
- [ ] T093 [P] Implement storage cutover phase 1 in src/storage/adapters/dual_write.py (shadow read: 双写postgres+sqlite, 读postgres, 异步对比SHA-256 hash, 记录差异)
- [ ] T094 [P] Add comprehensive metrics in src/observability/metrics.py (crawl_requests_total, crawl_duration_seconds, report_generation_duration_seconds, intl_latest_coverage_ratio, high_authority_ratio)
- [ ] T095 [P] Create Grafana dashboard for crawling health in config/grafana/dashboards/crawling_health.json (requests by source/status, latency histogram, error rate)
- [ ] T096 [P] Implement A/B testing framework in src/services/ab_test_service.py (route 10% traffic to new authority scoring algorithm, compare scores, statistical significance test p<0.05)
- [ ] T097 [P] Add frontend integration tests in frontend/tests/integration/ (Playwright E2E: navigate to /admin/sources, add new source, verify in DataTable)
- [ ] T098 [P] Create deployment documentation in docs/deployment.md (Docker Compose setup, environment variables, database migrations, Redis config, Prometheus/Grafana setup, 网易邮箱授权码获取步骤: 登录mail.163.com → 设置 → POP3/SMTP/IMAP → 开启SMTP服务 → 生成授权码)
- [ ] T099 [P] Implement quickstart validation script in scripts/validate_quickstart.sh (run through quickstart.md步骤, verify each checkpoint passes)
- [ ] T100 [P] Code cleanup and refactoring (remove dead code, add type hints, improve error messages)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational - No dependencies on other stories ✅ MVP
  - US2 (Phase 4): Can start after Foundational - Integrates with US1 but independently testable
  - US3 (Phase 5): Can start after Foundational - Management UI for US1/US2 but not blocking
  - US4 (Phase 6): Can start after Foundational - Analytics on top of US1/US2 data
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: ✅ MVP - No dependencies on other stories, can deploy independently
- **User Story 2 (P2)**: Enhances US1 with AI summaries, but US1 can work without it (display original content)
- **User Story 3 (P3)**: Management UI for configuring US1/US2, but initial config can be done via files
- **User Story 4 (P3)**: Analytics/visualization on top of US1/US2 data, purely additive

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T008)
- All Foundational adapter implementations marked [P] can run in parallel (T010-T014, T016-T019)
- Within US1: Models (T023-T026), Parsers (T028-T029), relevance+scoring (T033) can run in parallel
- Within US2: All provider implementations (T048-T053) can run in parallel
- Within US3: API endpoints (T063-T065, T069-T070, T073-T074) + frontend pages (T067-T068, T071, T075) can run in parallel
- Within US4: wordcloud service (T079) + audit export service (T086) + frontend components (T082, T087) can run in parallel
- All Polish tasks (T089-T100) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch models in parallel:
Task T023: Create Source model in src/models/source.py
Task T024: Create Article model in src/models/article.py
Task T025: Create IntlItem model in src/models/intl_item.py
Task T026: Create Report model in src/models/report.py

# After models, launch parsers in parallel:
Task T028: HTML parser in src/crawling/parsers/html_parser.py
Task T029: Playwright renderer in src/crawling/parsers/playwright_renderer.py

# After parsers, can do relevance + authority scoring in parallel while ingest is being built:
Task T033: Relevance module in src/pipeline/relevance.py (parallel with T034)
Task T034: Authority scoring module in src/pipeline/authority_scoring.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Recommended for 1-Week Sprint

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T022) - CRITICAL, blocks everything
3. Complete Phase 3: User Story 1 (T023-T044)
4. **STOP and VALIDATE**: Run independent test - configure 5 sources, generate report, verify ≥30 items, ≥70% high authority on first screen, dual timestamps displayed correctly
5. Deploy MVP - functional daily international financial news aggregation

**MVP Deliverable**: Daily automated aggregation of international financial news with:
- ✅ RSS/HTML crawling from multiple sources
- ✅ Content cleaning and deduplication
- ✅ Authority-based ranking
- ✅ Dual timestamps (UTC + CST北京时间)
- ✅ Time window filtering (T-24h primary, T-48h fallback)
- ✅ HTML report generation
- ✅ API endpoints for programmatic access

### Incremental Delivery (Add Stories Sequentially)

1. Complete Setup + Foundational (T001-T022) → Foundation ready
2. Add User Story 1 (T023-T044) → Test independently → Deploy MVP ✅
3. Add User Story 2 (T045-T060) → Test independently → Deploy with AI summaries
4. Add User Story 3 (T061-T077) → Test independently → Deploy with admin UI
5. Add User Story 4 (T078-T088) → Test independently → Deploy with analytics
6. Polish (T089-T100) → Refinements and cross-cutting concerns

Each story adds value without breaking previous stories.

### Parallel Team Strategy (If Multiple Developers Available)

With 3-4 developers:

1. **Week 1**: Team completes Setup + Foundational together (T001-T022)
2. **Week 2** (once Foundational done):
   - Developer A: User Story 1 (T023-T044) - MVP priority
   - Developer B: User Story 2 (T045-T060) - AI integration
   - Developer C: User Story 3 (T061-T077) - Admin UI
3. **Week 3**:
   - Developer A: User Story 4 (T078-T088) - Analytics
   - Developer B+C: Polish (T089-T100) - PDF/Email/Frontend cards
4. Integration testing and deployment

---

## Notes

- **[P] markers**: 52 tasks can run in parallel out of 100 total (52% parallelizable)
- **[Story] labels**: US1(22), US2(16), US3(17), US4(11) = 66 story-specific tasks
- Each user story is independently completable and testable per spec requirements
- Foundational phase (T009-T022) is critical path - must complete before any story work
- MVP can be delivered with just Phase 1-3 (T001-T044) = 44 tasks ≈ 5-7 days for single developer
- Storage cutover演练 (T093) validates postgres↔sqlite switching without code changes
- No test tasks included as spec does not explicitly request TDD approach - focus on implementation
- Commit after each task or logical group for easier rollback
- Stop at any checkpoint to validate story independently before proceeding
