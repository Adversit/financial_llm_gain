# Feature Specification: International Financial News Aggregation System

**Feature Branch**: `001-intl-news-aggregation`
**Created**: 2025-10-22
**Status**: Draft
**Input**: User description: "International financial news aggregation with data models for articles, summaries, international items, and daily reports including frontend capabilities for word clouds, console parameters, source management, and personalized prompts"

---

## Specification (YAML Format)

```yaml
feature:
  name: "国际金融新闻聚合系统"
  version: "1.0.0"
  description: "聚合国际金融新闻,提供结构化数据模型与前端管理能力,遵循事实优先与可复现原则"

data_models:
  article:
    description: "原始新闻文章实体,存储从信息源采集的完整内容"
    fields:
      - name: "id"
        type: "uuid"
        description: "文章唯一标识符"
        constraints: "非空,主键"

      - name: "source_id"
        type: "string"
        description: "信息源标识符,关联到sources表"
        constraints: "非空,外键"

      - name: "region"
        type: "string"
        description: "地理区域标识(如US/EU/APAC/JP)"
        constraints: "枚举值,非空"

      - name: "title"
        type: "string"
        description: "文章标题(原始语言)"
        constraints: "非空,最大500字符"

      - name: "url"
        type: "url"
        description: "文章来源URL"
        constraints: "非空,唯一"

      - name: "published_at_utc"
        type: "timestamp"
        description: "发布时间(UTC标准化)"
        constraints: "非空,ISO 8601格式"

      - name: "content_raw"
        type: "text"
        description: "原始HTML/文本内容"
        constraints: "非空"

      - name: "content_clean"
        type: "text"
        description: "清洗后的纯文本正文"
        constraints: "非空,移除广告与无关内容"

  summary:
    description: "AI生成的文章摘要实体,必须包含AI标注信息"
    fields:
      - name: "article_id"
        type: "uuid"
        description: "关联的文章ID"
        constraints: "非空,外键,关联article.id"

      - name: "summary_text"
        type: "text"
        description: "AI生成的摘要文本"
        constraints: "非空,最大500字符"

      - name: "keywords"
        type: "array<string>"
        description: "提取的关键词列表"
        constraints: "0-10个关键词"

      - name: "importance"
        type: "integer"
        description: "重要性评分(1-10)"
        constraints: "1-10整数"

      - name: "is_ai_generated"
        type: "boolean"
        description: "AI生成标识(必须为true)"
        constraints: "非空,恒为true"

      - name: "model_info"
        type: "object"
        description: "AI模型元数据"
        constraints: "非空"
        sub_fields:
          - name: "model"
            type: "string"
            description: "模型名稱(如gpt-4/claude-3)"
            constraints: "非空"

          - name: "version"
            type: "string"
            description: "模型版本(如0613)"
            constraints: "非空"

          - name: "timestamp"
            type: "timestamp"
            description: "生成时间(UTC)"
            constraints: "非空,ISO 8601格式"

  intl_item:
    description: "国际速览条目,最终展示给用户的标准化内容项"
    fields:
      - name: "title"
        type: "string"
        description: "标准化标题(中文或双语)"
        constraints: "非空,最大200字符"

      - name: "source"
        type: "string"
        description: "信息源名稱(如Bloomberg/Reuters)"
        constraints: "非空"

      - name: "published_at_utc"
        type: "timestamp"
        description: "发布时间(UTC)"
        constraints: "非空,ISO 8601格式"

      - name: "published_at_local"
        type: "timestamp"
        description: "发布时间(CST北京时间)"
        constraints: "非空,从UTC转换"

      - name: "summary_60w"
        type: "text"
        description: "60汉字以内摘要"
        constraints: "非空,最大60汉字"

      - name: "url"
        type: "url"
        description: "原文链接"
        constraints: "非空"

      - name: "is_ai_generated"
        type: "boolean"
        description: "摘要是否AI生成"
        constraints: "非空"

      - name: "model_info"
        type: "object | null"
        description: "如is_ai_generated=true,必须包含模型信息"
        constraints: "条件非空"

  report:
    description: "每日金融报告实体,包含所有聚合内容与审计信息"
    fields:
      - name: "date"
        type: "date"
        description: "报告日期(CST北京时间)"
        constraints: "非空,YYYY-MM-DD格式"

      - name: "sections"
        type: "array<section>"
        description: "按主题/地区组织的章节"
        constraints: "0-N个section对象"
        sub_fields:
          - name: "section_title"
            type: "string"
            description: "章节标题(如'美国市场'/'欧洲政策')"

          - name: "items"
            type: "array<intl_item>"
            description: "该章节的新闻条目列表"

      - name: "intl_latest"
        type: "array<intl_item>"
        description: "国际速览(T-24h最新消息,优先高权威)"
        constraints: "非空数组,按时间倒序"

      - name: "wordcloud"
        type: "object"
        description: "词云数据(关键词频率统计)"
        constraints: "非空"
        sub_fields:
          - name: "keywords"
            type: "array<object>"
            description: "关键词与频率对"
            sub_fields:
              - name: "word"
                type: "string"

              - name: "frequency"
                type: "integer"

      - name: "audit_ref"
        type: "string"
        description: "审计日誌引用ID"
        constraints: "非空,关联到audit_logs表"

requirements:
  must_have:
    - id: "MH-001"
      description: "国际最新消息时间窗策略"
      rule: "系统必须优先采集T-24h时间窗内的国际新闻(基于UTC时间戳)"
      fallback: "若T-24h内容不足以满足quota,回填T-48h内容并在intl_item添加标识 'out_of_primary_window: true'"
      acceptance: "报告中95%条目来自T-24h,超窗内容明确标注"

    - id: "MH-002"
      description: "高权威信息源占比下限"
      rule: "首屏(前10条)国际速览中,authority_score≥80的信息源占比必须≥{{high_authority_min_ratio}}(默认70%)"
      enforcement: "筛选阶段优先选择高权威源,低权威源仅在quota允许时补充"
      acceptance: "首屏高权威占比统计≥配置阈值"

    - id: "MH-003"
      description: "AI生成内容强制标注"
      rule: "所有AI生成/改写内容必须在输出中显示角标🤖+model_info"
      format: "HTML/Markdown展示格式: '🤖 AI摘要 (GPT-4, 2025-10-22 03:00 UTC)'"
      metadata: "JSON输出必须包含 is_ai_generated=true 与完整model_info对象"
      acceptance: "任何AI内容缺少标注视为不合规,自动化测试覆盖"

    - id: "MH-004"
      description: "前端词云可视化"
      rule: "系统必须从当日报告提取关键词并生成词云数据结构"
      output: "提供JSON格式词频数据,供前端渲染(技术栈由实现决定)"
      acceptance: "报告的wordcloud字段包含至少20个关键词与频率"

    - id: "MH-005"
      description: "前端控制台参数配置"
      rule: "系统必须提供界面允许调整运行参数: intl_window_hours(12-48), intl_quota_total(10-100), high_authority_min_ratio(0-100%)"
      persistence: "参数修改后持久化,下次运行生效"
      acceptance: "用户可通过界面修改参数,重新生成报告反映新配置"

    - id: "MH-006"
      description: "前端信息源新增与验证"
      rule: "系统必须提供界面新增信息源(URL/region/初始authority_score),并执行可达性验证"
      validation: "验证包括: HTTP可达性检查, 内容解析测试, 初步质量评分"
      acceptance: "新源通过验证后加入registry.yaml,失败则显示具体错误原因"

    - id: "MH-007"
      description: "前端个性化提示词定制"
      rule: "系统必须允许用户编辑AI摘要的提示词模板,保存为versioned prompts"
      versioning: "提示词遵循P-X.Y.Z版本控制,修改触发MINOR版本递增"
      acceptance: "用户修改提示词后,新生成摘要使用新版本,旧摘要保留旧版本引用"

    - id: "MH-008"
      description: "审计导出功能"
      rule: "系统必须提供审计日志导出,支持过滤条件: 来源/日期范围/成本阈值"
      output: "导出格式包括JSON Lines与CSV,包含字段: timestamp/sources_used/items_count/ai_calls/cost/score_distribution"
      acceptance: "用户可导出指定时间范围审计数据,验证cost总和与明细一致"

    - id: "MH-009"
      description: "存储可切换(产品级约束)"
      rule: "系统架构必须支持数据存储层抽象,允许在JSON文件/SQLite/PostgreSQL间切换"
      constraint: "存储切换不影响业务逻辑,仅需修改配置文件"
      acceptance: "在不同存储后端运行相同测试套件,结果一致"

  nice_to_have:
    - id: "NH-001"
      description: "多语言并排标题"
      rule: "intl_item.title支持双语展示(原文+中文翻譯并排)"
      format: "US Market Rally | 美国市场反彈"
      acceptance: "用户可配置是否啟用双语模式,默认仅中文"

    - id: "NH-002"
      description: "影响映射(海外政策→国内板塊)"
      rule: "检测海外重大政策新闻,自动关联可能受影响的国内行业板塊"
      example: "美联储加息 → 标注'可能影响: 出口制造/房地产/金融'"
      acceptance: "对於已知政策模式(利率/貿易/能源),提供影响提示"

acceptance_criteria:
  - id: "AC-001"
    description: "可复现性验证"
    rule: "固定配置(相同源集合/时间窗/提示词版本/去重阈值)下,多次运行产生一致输出"
    tolerance: "允许同分并列条目顺序微差(±1位),但内容与评分必须完全一致"
    test: "使用Mock数据与固定时间戳,运行3次,对比输出hash"

  - id: "AC-002"
    description: "国际速览双时标与摘要"
    rule: "每条intl_item必须包含: published_at_utc/published_at_local(CST)/source/60字摘要"
    format: "展示格式: '2025-10-22 03:00 UTC (CST 11:00) | Bloomberg | 美联储宣布维持利率不变,市场反应...'"
    test: "遍历intl_latest数组,验证每个对象包含必需字段且格式正确"

  - id: "AC-003"
    description: "低权威源隔离与剔除"
    rule: "authority_score<30的源自动进入quarantine状态,不参与常规采集"
    visibility: "隔离源在前端标注'⚠ 隔离中',仅管理员可手动触发采集"
    test: "创建authority_score=25的测试源,验证其不出现在正常报告中"

  - id: "AC-004"
    description: "非投资建议声明"
    rule: "报告输出(HTML/Markdown)必须在顶部显著位置声明: '⚠️ 本报告仅供信息参考,不构成投资建议'"
    prohibition: "系统输出不得包含: '建议买入/卖出', '目标价', '预期收益', '评级上调/下调', '交易信号'"
    test: "正则扫描输出内容,检测禁用词汇,违反则测试失败"

  - id: "AC-005"
    description: "AI内容标注完整性"
    rule: "任何AI生成的summary/title/keyword,输出时必须附带model_info"
    enforcement: "缺少标注的AI内容视为系统缺陷,触发告警"
    test: "遍历所有is_ai_generated=true的条目,验证model_info非空且包含model/version/timestamp"

configuration_variables:
  - name: "intl_window_hours"
    default: 24
    range: "12-48"
    description: "国际新闻时间窗(小时),决定T-Xh的范围"

  - name: "intl_quota_total"
    default: 50
    range: "10-100"
    description: "国际速览条目总数配額"

  - name: "high_authority_min_ratio"
    default: 0.7
    range: "0.0-1.0"
    description: "首屏高权威源最低占比(如0.7表示70%)"

  - name: "semantic_similarity_threshold"
    default: 0.85
    range: "0.70-0.95"
    description: "语义去重相似度阈值(cosine similarity),高于此值视为重复内容,保留authority_score最高的"

  - name: "dedup_clustering_eps"
    default: 0.3
    range: "0.1-0.5"
    description: "DBSCAN主题聚类eps参数,控制簇密度,值越小簇越紧密"

assumptions:
  - "信息源提供RSS或API接口,或可通过HTTP抓取HTML"
  - "AI模型API(GPT-4/Claude)可用且成本在预算内"
  - "用户主要在JST时区使用,默认展示JST时间"
  - "词云关键词提取使用TF-IDF或LLM,具体算法由实现决定"
  - "前端技术栈不限,只要能渲染JSON/Markdown数据"
```

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 每日国际金融速览生成 (Priority: P1)

系统每日自动聚合国际金融新闻,生成包含双时标(UTC+CST)、信息源与60字摘要的速览列表,优先展示高权威源(Bloomberg/Reuters等)内容,确保用户在CST早晨8點前获得T-24h全球金融动态。

**Why this priority**: 核心MVP功能,提供日报的基本價值。无此功能,系统无法交付任何用户價值。

**Independent Test**: 配置测试信息源(3个高权威+2个普通权威),设置时间窗T-24h,运行报告生成流程,验证输出包含至少30条新闻且首屏高权威占比≥70%。

**Acceptance Scenarios**:

1. **Given** 系统配置10个国际信息源(8个高权威,2个普通权威),时间窗T-24h, **When** 每日UTC 23:00触发报告生成, **Then** 系统生成包含40-50条新闻的intl_latest数组,95%条目时间戳在T-24h内,首屏10条中至少7条来自高权威源
2. **Given** 某日仅5条新闻在T-24h内, **When** quota设为50条, **Then** 系统回填T-48h新闻至50条,超窗内容标注 `out_of_primary_window: true`,用户界面显示⏰图标
3. **Given** 用户打開报告HTML, **When** 查看任意新闻条目, **Then** 每条新闻显示"2025-10-22 03:00 UTC (CST 11:00) | Bloomberg | 60字摘要",双时标清晰可读

---

### User Story 2 - AI摘要生成与透明标注 (Priority: P2)

系统使用AI模型(GPT-4/Claude)为原始新闻生成60字以内中文摘要与关键词,所有AI生成内容必须显示🤖角标与模型信息(模型名/版本/生成时间),确保用户明确区分原始事实与AI加工内容。

**Why this priority**: 提升阅读效率(60字摘要vs全文),同时遵循憲法原则I(事实优先与AI标注),是合规的必需功能。

**Independent Test**: 提供5篇英文原文,调用AI摘要API,验证生成的summary对象包含summary_text(≤60汉字)/keywords(3-5个)/model_info(model/version/timestamp),HTML输出显示🤖标注。

**Acceptance Scenarios**:

1. **Given** 一篇英文新闻"Fed keeps rates steady, signals cautious approach", **When** 系统生成AI摘要, **Then** summary_text为"美联储維持利率不变并释放谨慎信號,市场静待下一步动作"(60字内),keywords包含["美联储","利率","谨慎"],model_info记錄 `{model:"gpt-4", version:"0613", timestamp:"2025-10-22T03:15:00Z"}`
2. **Given** 用户查看HTML报告, **When** 鼠标悬停在摘要上, **Then** 显示"🤖 AI摘要 (GPT-4, 2025-10-22 03:15 UTC)"工具提示
3. **Given** 某条新闻未使用AI摘要(人工编辑), **When** 查看JSON输出, **Then** is_ai_generated=false,model_info为null,无🤖角标

---

### User Story 3 - 前端管理控制台(信息源/参数/提示词) (Priority: P3)

系统提供Web界面,允许管理员新增/验证信息源(输入URL,自动检测region与可达性),调整运行参数(时间窗/配额/权威阈值),定制AI提示词模板(保存为versioned prompts),所有修改持久化并在下次报告生成时生效。

**Why this priority**: 增强系统靈活性,減少手动配置文件编辑,适合非技術用户。但MVP可先通过配置文件管理,故优先级P3。

**Independent Test**: 通过UI新增信息源"https://example.com/rss",触发验证流程,系统返回HTTP 200与初步质量评分,保存至registry.yaml;修改intl_quota_total从50→30,重新生成报告,验证输出仅30条。

**Acceptance Scenarios**:

1. **Given** 管理员在控制台输入新信息源URL "https://new-source.com/feed", **When** 点击"验证", **Then** 系统发送HTTP请求,解析RSS/HTML,返回"✓ 可达,region: US, 建议authority_score: 65",管理员确认后保存至registry.yaml
2. **Given** 管理员修改提示词模板为"請用50字簡述新闻要點", **When** 保存, **Then** 系统创建新提示词版本P-1.1.0,下次摘要生成使用新模板,舊摘要仍引用P-1.0.0
3. **Given** 管理员将high_authority_min_ratio从70%调至80%, **When** 重新生成报告, **Then** 首屏10条中至少8条来自authority_score≥80的源,或系统告警"高权威源不足,无法满足80%阈值"

---

### User Story 4 - 词雲可视化与审计导出 (Priority: P3)

系统从每日报告提取关键词生成词云数据(JSON格式,包含词频),前端渲染为可视化词云;提供审计日志导出功能,支持按日期范围/信息源/成本过滤,输出CSV或JSON Lines格式,供合规审查与成本分析。

**Why this priority**: 增强数据可视化与运營透明度,但非核心业务流程,故P3。

**Independent Test**: 生成包含100条新闻的报告,提取关键词,验证wordcloud对象包含至少20个关键词与频率;导出2025-10-01至2025-10-31审计日誌,验证CSV包含31行(每日一行)与成本总和字段。

**Acceptance Scenarios**:

1. **Given** 当日报告包含50条新闻,提及"美联储"15次、"加息"10次、"通脹"8次, **When** 生成词雲数据, **Then** wordcloud.keywords包含 `[{word:"美联储", frequency:15}, {word:"加息", frequency:10}, {word:"通脹", frequency:8}, ...]`,前端渲染为字体大小反映频率的词雲图
2. **Given** 管理员选择导出2025-10月审计日誌,过滤条件"仅Bloomberg源", **When** 點擊导出CSV, **Then** 下载文件包含31行,每行包含date/sources_used(仅Bloomberg)/items_count/ai_calls/cost列
3. **Given** 审计日誌显示某日AI调用成本$50超标, **When** 查看该日明細, **Then** 可追溯至具体文章ID与model_info,定位高成本原因

---

### Edge Cases

- **时区跨日边界**: 当UTC 23:50获取新闻时,部分源可能已进入次日,需确保时间窗计算基於UTC而非CST,避免重複或遗漏
- **信息源结构变更**: 某源HTML结构改变导致解析失敗,系统应记錄错误至audit_logs,降低该源health_score,次日调整配額
- **AI API限流**: GPT-4达到rate limit时,系统应降级至Claude或跳过摘要(保留原文),标注"摘要暂不可用"
- **同分并列排序**: 兩条新闻authority_score与时间戳相同时,排序可能微差,但需保证可复现(使用穩定排序算法如ID字典序)
- **超長标题**: 某些源标题超过500字符,系统应截断至500并标注"...(原文更長)"
- **多语言混杂**: 日文源标题包含日文+英文混合,词雲提取需支持多语言分词或依赖LLM

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统必须每日自动采集配置的国际信息源(RSS/API/HTML),提取标题/URL/发布时间/正文内容,存储为article实体
- **FR-002**: 系统必须将所有原始时间戳(无论源时区)转换为UTC标准时间,存储于published_at_utc字段,展示时再转换为CST北京时间
- **FR-003**: 系统必须清洗原始内容,移除广告/导航栏/版权声明,保留纯文本正文存入content_clean
- **FR-004**: 系统必须对article执行三层去重(SHA-256哈希/语义嵌入相似度>{{semantic_similarity_threshold}}/DBSCAN主题聚类eps={{dedup_clustering_eps}}),保留authority_score最高的版本
- **FR-005**: 系统必须根据时间窗(默认T-24h)与配额(默认50条)筛选文章,优先高权威源,不足时回填T-48h并标注
- **FR-006**: 系统必须调用AI API生成summary实体(60字摘要/关键词/重要性评分),记录完整model_info
- **FR-007**: 系统必须为每个summary标记is_ai_generated=true,禁止输出未标注的AI内容
- **FR-008**: 系统必须组装intl_item列表,包含双时标(UTC+CST)/信息源名/60字摘要/原文URL
- **FR-009**: 系统必须生成report实体,包含日期/sections(按主题分组)/intl_latest(时间倒序)/wordcloud(关键词频率)/audit_ref
- **FR-010**: 系统必须输出JSON/HTML/Markdown三种格式报告,HTML/Markdown包含"⚠️ 本报告仅供信息参考,不构成投资建议"声明
- **FR-011**: 系统必须在HTML/Markdown中为AI内容显示🤖角标+模型信息,如"🤖 AI摘要 (GPT-4, 2025-10-22 03:15 UTC)"
- **FR-012**: 系统必须提供前端界面新增信息源,输入URL后自动检测HTTP可达性/region/初步质量评分,验证通过后保存至registry.yaml
- **FR-013**: 系统必须提供前端界面调整参数intl_window_hours(12-48)/intl_quota_total(10-100)/high_authority_min_ratio(0-100%),修改后持久化
- **FR-014**: 系统必须提供前端界面编辑AI提示词模板,保存时创建新版本(P-X.Y.Z),修改触发MINOR递增
- **FR-015**: 系统必须从报告提取关键词(TF-IDF或LLM),生成wordcloud对象(包含至少20个关键词与频率),供前端渲染
- **FR-016**: 系统必须记录每次运行的审计日志(timestamp/config_snapshot/sources_used/items_count/ai_calls/cost/score_distribution)
- **FR-017**: 系统必须提供审计日志导出功能,支持过滤条件(日期范围/信息源/成本阈值),输出CSV或JSON Lines格式
- **FR-018**: 系统必须支持数据存储层抽象,允许在JSON文件/SQLite/PostgreSQL间切换,仅需修改配置文件
- **FR-019**: 系统必须将authority_score<30的信息源标记为quarantine状态,不参与常规采集,仅管理员可手动触发
- **FR-020**: 系统必须扫描输出内容,禁止包含投资建议词汇("建议买入/卖出"/"目标价"/"预期收益"/"评级"/"交易信号"),违反则抛出异常

### Key Entities *(include if feature involves data)*

- **Article**: 原始新闻文章,包含id/source_id/region/title/url/published_at_utc/content_raw/content_clean,代表从信息源采集的未加工内容
- **Summary**: AI生成摘要,关联article_id,包含summary_text/keywords/importance/is_ai_generated/model_info,必须标注AI元数据
- **IntlItem**: 标准化展示条目,包含title/source/published_at_utc/published_at_local/summary_60w/url/is_ai_generated/model_info,面向最終用户
- **Report**: 每日金融报告,包含date/sections(主题分组)/intl_latest(速览列表)/wordcloud(词频数据)/audit_ref,聚合所有内容
- **Source**: 信息源元数据(存储於registry.yaml),包含source_id/name/url/region/authority_score/health_status,决定采集优先级
- **AuditLog**: 审计日誌记錄,包含timestamp/config_snapshot/sources_used/items_count/ai_calls/cost,支持合规审查与成本追溯

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 系统每日在CST 08:00前成功生成并发布金融报告,准时率达99%(每月最多1次延遲)
- **SC-002**: 国际速览包含95%以上条目来自T-24h时间窗,超窗内容明确标注,用户可一目了然
- **SC-003**: 首屏(前10条)新闻中,高权威源(authority_score≥80)占比达70%以上,确保信息质量
- **SC-004**: 近重複内容(语义相似度>0.85)控制在5%以内,避免用户阅读疲勞
- **SC-005**: 每日AI成本不超过预算上限(如$100/天),成本守門达标率100%,无超标日
- **SC-006**: 所有AI生成内容(摘要/关键词)100%附帶🤖角标与model_info,自动化测試覆盖率100%
- **SC-007**: 用户通过前端控制台新增信息源,验证成功率≥90%(排除无效URL),验证失敗时提供清晰错误信息
- **SC-008**: 固定配置下多次运行,输出一致性达100%(允许同分并列顺序±1位微差),支持问题复现
- **SC-009**: 审计日誌导出功能响应时间<5秒(查詢30天数据),导出文件格式正确率100%
- **SC-010**: 词雲包含至少20个有意义关键词(排除停用词),频率统计准确率100%,前端渲染成功率≥95%

---

## Constitutional Alignment

本规范遵循`.specify/memory/constitution.md`定义的以下原则:

- **原则 I - 事实优先与AI标注**: 所有AI生成内容强制标注model_info(FR-007/MH-003/AC-005)
- **原则 II - 非投资目的声明**: 输出包含免责声明,禁止投资建议词汇(FR-010/FR-020/AC-004)
- **原则 III - 模塊化解耦**: 数据模型清晰分离(article/summary/intl_item/report),存储层可插拔(FR-018/MH-009)
- **原则 IV - 可复现与审计**: 审计日誌记錄完整配置快照,支持问题复现(FR-016/AC-001)
- **原则 V - 信息源权威分级**: 高权威占比阈值(MH-002),quarantine机制(FR-019/AC-003)
- **原则 VI - 去重策略三层防护**: 哈希/语义/主题去重(FR-004),近重複率≤5%(SC-004)
- **原则 VII - 时区标准化**: UTC存储+CST展示(FR-002/AC-002)
- **原则 VIII - 成本与并发控制**: 每日成本守門(SC-005),降级策略(边緣案例-AI限流)

---

## Assumptions

1. 信息源主要为中文财经/科技媒体(35个源),包含三种类型: RSS订阅源(24个)/RSSHub路由(9个)/自定义爬虫(2个),分类覆盖: 政府官方(6)/主流财经(4)/金融科技(6)/AI科技(13)/学术组织(2)/国际源(1),初始权威分数范围58-95分
2. AI模型API默认使用DeepSeek(deepseek-chat,成本最低约$0.14/1M tokens),备选OpenAI GPT-3.5-turbo($0.5/1M)和Anthropic Claude-3-sonnet($3/1M),平均响应时间<3秒,每日配額足夠处理50-100条摘要
3. 用户主要在中国使用系统,默认展示CST北京时间(UTC+8, Asia/Shanghai),但支持UTC查看
4. 邮件发送使用网易邮箱SMTP服务(smtp.163.com端口587,TLS加密),需配置发件邮箱账号与授权码(非密码)
5. 前端技術棧不限,只要能消費JSON API与渲染Markdown/HTML,词雲可使用任意可视化庫(如D3.js/ECharts/Canvas)
6. 数据存储初期使用JSON文件或SQLite,未来可升级至PostgreSQL,存储接口抽象保证切換无痛
7. 关键词提取使用TF-IDF算法(scikit-learn TfidfVectorizer),过滤停用词后提取top 20-50关键词,质量要求:至少90%关键词需与金融术语相关(验证方法:人工抽查30个样本,金融相关性≥90%),备选方案:LLM提取(成本更高但质量更稳定)
8. 信息源健康巡检与配額调整由外部调度器(如cron/Airflow)触发,本规范聚焦数据模型与业务逻辑
9. 用户具备基本金融新闻阅读能力,能理解双时标与信息源概念,无需过多UI引导

---

## Notes

- 本规范采用YAML格式清晰定义数据模型,便於后续生成JSON Schema与数据庫遷移腳本
- 配置变量(intl_window_hours/intl_quota_total/high_authority_min_ratio)保留占位符`{{...}}`,实际值由部署环境配置文件提供
- 前端四项能力(词雲/控制台参数/信息源管理/提示词定制)可分階段实现,P1优先核心报告生成,P3后续迭代增强管理体验
- 审计导出功能支持合规审查与成本分析,对於企业级部署尤为重要,建议納入MVP范圍
- 多语言并排标题(NH-001)与影响映射(NH-002)为增值功能,可根据用户反饋决定优先级

---

**Next Steps**:
- 使用 `/speckit.clarify` 解决任何剩餘的不明确需求
- 使用 `/speckit.plan` 生成实现计划(包含技術架构/数据模型设计/API契約)
- 使用 `/speckit.tasks` 生成任务清单(按User Story优先级组織)
