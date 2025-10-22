# 金融日报系统 Constitution

<!--
Sync Impact Report:
- Version change: [NEW] → 1.0.0
- Modified principles: N/A (initial version)
- Added sections: All (meta, governance, principles, success_metrics, risk_register, documentation)
- Removed sections: N/A
- Templates requiring updates:
  ✅ plan-template.md: Constitution Check section aligns with principles
  ✅ spec-template.md: Requirements align with output contracts and AI labeling
  ✅ tasks-template.md: Task categorization supports modular phases
- Follow-up TODOs:
  - Ownership placeholders (product_owner, tech_owner) require real names
  - Source health thresholds and quarantine automation need concrete implementation
-->

## Constitution (YAML)

```yaml
meta:
  project_name: "金融日报系统"
  version: "1.0.0"
  timezone: "Asia/Shanghai"
  vision: "以客观事实为核心的干货聚合与发布,不提供投资建议或交易信号"
  ownership:
    product_owner: "TODO(PRODUCT_OWNER): Specify product owner name"
    tech_owner: "TODO(TECH_OWNER): Specify technical owner name"

governance:
  decision_forum:
    name: "每日金融最新消息获取与信息源健康巡检"
    schedule: "daily"
    responsibilities:
      - "获取当日金融新闻与事件 (UTC时间窗: T-24h, 展示为CST北京时间)"
      - "巡检信息源健康状态 (可达性/延迟/结构变更)"
      - "失败复盘: 记录失败原因、影响范围、修复措施"
      - "次日配额/权重调整: 基于authority_score与健康状态动态分配"
    outputs:
      - "daily_report: 金融日报 (JSON/HTML/Markdown, 时间展示为CST)"
      - "source_health: 信息源健康报告 (含失败日志与调整建议)"

  change_control:
    rfc_triggers:
      - "输出契约变更 (JSON schema, HTML结构, Markdown格式)"
      - "信息源策略调整 (新增/移除源, authority_score阈值变更)"
      - "预算并发限制变更 (AI调用频率, API配额)"
      - "外部接口变更 (上游数据源API, 下游消费者契约)"
      - "去重策略调整 (内容哈希算法, 语义嵌入模型, 主题聚类参数)"
    approval_process:
      - "RFC文档提交至 .specify/rfcs/[###-rfc-title].md"
      - "技术负责人审核影响范围与回滚方案"
      - "产品负责人审核业务价值与风险接受度"
      - "批准后记录至 CHANGELOG.md 并更新契约版本"

  versioning:
    system: "SemVer (MAJOR.MINOR.PATCH)"
    components:
      system_version:
        format: "X.Y.Z"
        rules:
          MAJOR: "输出契约破坏性变更, 信息源策略重构"
          MINOR: "新增信息源, 新增输出格式, 功能增强"
          PATCH: "Bug修复, 性能优化, 配置调整"
      prompts_version:
        format: "P-X.Y.Z"
        scope: "AI提示词独立版本控制"
        storage: ".specify/prompts/versions/P-X.Y.Z/"
        rules:
          MAJOR: "提示词结构重构 (影响输出格式)"
          MINOR: "新增提示词模板, 优化现有模板"
          PATCH: "措辞优化, 错别字修正"
      contracts_version:
        format: "C-X.Y.Z"
        scope: "输出契约独立版本控制"
        storage: ".specify/contracts/versions/C-X.Y.Z/"
        rules:
          MAJOR: "JSON schema破坏性变更"
          MINOR: "新增可选字段, 新增输出格式"
          PATCH: "文档更新, 示例补充"

principles:
  - name: "I. 事实优先与AI标注 (NON-NEGOTIABLE)"
    description: |
      任何AI生成或改写的内容必须显式标注模型名称、版本与生成时间。

      **规则**:
      - 原始新闻内容优先保留,AI仅用于摘要/翻译/去重
      - AI生成内容必须包含元数据: `ai_generated: {model: "gpt-4", version: "0613", timestamp: "2025-10-22T03:00:00Z"}`
      - 输出HTML/Markdown必须在AI内容旁显示标注: "🤖 AI摘要 (GPT-4, 2025-10-22 03:00 UTC)"
      - 禁止AI改写事实数据 (数字/日期/人名/机构名)

      **理由**:
      确保透明度,用户明确区分原始事实与AI加工内容,避免误导。

  - name: "II. 非投资目的声明 (NON-NEGOTIABLE)"
    description: |
      系统不提供投资建议、交易信号或收益预测。

      **规则**:
      - 输出HTML/Markdown必须显著声明: "⚠️ 本报告仅供信息参考,不构成投资建议"
      - 禁止包含"建议买入/卖出", "目标价", "预期收益"等投资导向措辞
      - 禁止个性化推荐 (基于用户持仓/偏好的定制内容)

      **理由**:
      明确法律责任边界,避免监管风险与用户误用。

  - name: "III. 模块化解耦 (NON-NEGOTIABLE)"
    description: |
      采用管道架构,各阶段独立可测试、可替换。

      **模块清单**:
      1. 采集 (Fetch): 从信息源抓取原始内容
      2. 清洗 (Clean): 提取正文/移除广告/标准化时间
      3. 去重 (Dedup): 内容哈希 + 语义嵌入 + 主题聚类
      4. 筛选 (Filter): 基于authority_score/时间窗/关键词
      5. 摘要 (Summarize): AI生成简短摘要 (含标注)
      6. 组装 (Assemble): 按主题/时间排序,生成最终报告
      7. 发布 (Publish): 输出JSON/HTML/Markdown
      8. 审计 (Audit): 记录处理日志与性能指标
      9. 前端UI: 可热插拔的显示层 (不影响后端管道)

      **接口规范**:
      - 每个模块定义契约 (input schema + output schema)
      - 模块间通过JSON传递数据,禁止直接调用内部函数
      - 测试时可Mock任意模块 (例如Mock AI摘要以节省成本)

      **理由**:
      便于测试、替换组件 (例如切换AI模型或新增去重策略) 且不影响其他模块。

  - name: "IV. 可复现与审计 (NON-NEGOTIABLE)"
    description: |
      相同输入(信息源集合/时间窗/配置/提示词版本)必须产生一致输出。

      **规则**:
      - 记录每次运行的配置快照: 信息源列表/时间窗/提示词版本/去重阈值
      - 统一UTC存储时间,JST展示 (避免时区混淆)
      - 内容去重使用确定性哈希 (SHA-256) + 语义嵌入 (固定模型版本)
      - 主题去重使用确定性聚类参数 (固定算法/阈值)
      - 审计日志包含: 输入快照/处理时间/输出哈希/AI调用次数/成本

      **理由**:
      支持问题复现、历史对比、成本追溯与合规审计。

  - name: "V. 信息源权威分级与动态调整"
    description: |
      基于权威分数(authority_score)分配配额与展示权重。

      **权威级别 (authority_bands)**:
      - **high (80-100)**: 主流金融媒体 (Bloomberg, Reuters, FT)
        - 动作: 优先采集,首屏展示,配额不限
      - **normal (50-79)**: 区域性媒体/专业博客
        - 动作: 正常采集,按主题混合展示,配额按健康状态分配
      - **watch (30-49)**: 新加入源/历史失败率偏高
        - 动作: 降低采集频率,二屏展示,配额减半,7日观察期
      - **quarantine (0-29)**: 频繁失败/内容质量差
        - 动作: 暂停采集,仅手动触发,14日隔离期后重评

      **动态调整规则**:
      - 每日巡检更新健康分数: success_rate (70%) + latency (20%) + content_quality (10%)
      - authority_score每周重新计算: 基于健康分数历史与用户反馈
      - 新源默认normal级别,探索配额20%,7日后根据表现调整

      **理由**:
      平衡高权威源的可靠性与新源的探索机会,避免单一源依赖。

  - name: "VI. 去重策略三层防护"
    description: |
      防止近重复内容降低报告价值。

      **去重层级**:
      1. **内容哈希去重**: SHA-256全文哈希,完全相同内容仅保留一条
      2. **语义去重**: 使用嵌入模型 (例如sentence-transformers) 计算相似度
         - 阈值: cosine_similarity > 0.85 视为近重复,保留authority_score最高的
      3. **主题去重**: 同主题聚类内,保留代表性内容 (最早发布 + 最高authority_score)
         - 聚类算法: DBSCAN或层次聚类,eps参数可配置

      **保留策略**:
      - 重复内容合并为单条,附注"另见N个相似报道"
      - 保留原始URL列表供审计

      **理由**:
      提升信息密度,避免用户阅读疲劳。

  - name: "VII. 时区标准化与展示分离"
    description: |
      统一UTC存储,CST(北京时间)展示,避免时区混淆。

      **规则**:
      - 采集时记录原始时间戳与源时区
      - 立即转换为UTC存储 (ISO 8601格式)
      - 展示时转换为CST北京时间 (UTC+8, Asia/Shanghai)
      - 时间窗查询始终基于UTC (例如T-24h = 当前UTC时间 - 24小时)

      **理由**:
      确保跨时区源的时间一致性,避免重复采集或遗漏。

  - name: "VIII. 成本与并发控制"
    description: |
      预算守门与流量整形,防止AI成本失控。

      **规则**:
      - 设定每日AI调用上限 (例如1000次GPT-4调用)
      - 优先高authority_score源,低分源在预算允许时处理
      - 实现降级策略: 预算不足时跳过摘要,仅保留原文
      - 并发限制: 单个API并发不超过5请求/秒 (避免rate limit)

      **理由**:
      可预测的成本与合规的API使用。

success_metrics:
  - id: "SM-001"
    name: "准时率"
    target: "99%"
    definition: "每日CST 08:00前发布报告的天数比例"
    measurement: "统计过去30天的发布时间,计算准时率"

  - id: "SM-002"
    name: "时效覆盖率"
    target: "95%"
    definition: "报告包含T-24h内发布的新闻比例"
    measurement: "新闻时间戳落在(当前UTC - 24h, 当前UTC]区间的条目数 / 总条目数"

  - id: "SM-003"
    name: "近重复率"
    target: "≤5%"
    definition: "语义相似度>0.85的内容对数量占比"
    measurement: "去重阶段检测到的近重复对数 / 总内容对数"

  - id: "SM-004"
    name: "成本守门达标率"
    target: "100%"
    definition: "每日AI成本不超过预算上限的天数比例"
    measurement: "过去30天成本未超标天数 / 30"

  - id: "SM-005"
    name: "首屏高权威占比"
    target: "≥70%"
    definition: "首屏(前10条)内容来自authority_score≥80源的比例"
    measurement: "首屏高权威源条目数 / 10"

risk_register:
  - id: "RISK-001"
    name: "信息源结构变更/反爬"
    impact: "High"
    probability: "Medium"
    mitigation:
      - "实现自适应解析器: 检测HTML结构变更并告警"
      - "多源冗余: 同一主题至少3个信息源"
      - "人工审核流程: 失败率>20%时触发人工介入"
      - "版本控制解析规则: 回滚至上一个工作版本"

  - id: "RISK-002"
    name: "跨时区时间解析错误"
    impact: "Medium"
    probability: "Low"
    mitigation:
      - "强制UTC标准化: 采集后立即转换"
      - "时间戳验证: 检测未来时间或过早时间(>7天前)并告警"
      - "审计日志: 记录原始时间戳与转换结果"

  - id: "RISK-003"
    name: "AI限流/成本波动"
    impact: "High"
    probability: "Medium"
    mitigation:
      - "多模型备份: GPT-4失败时降级至Claude/Gemini"
      - "本地缓存: 相同内容24小时内不重复调用AI"
      - "成本预警: 达到预算80%时发送告警"
      - "降级策略: 预算不足时跳过摘要,仅保留原文"

  - id: "RISK-004"
    name: "高权威源挤压新源探索"
    impact: "Medium"
    probability: "High"
    mitigation:
      - "探索配额: 预留20%配额给authority_score<50的新源"
      - "冷却期机制: 高权威源连续失败3次后进入24h冷却,释放配额给新源"
      - "定期评审: 每月审核新源表现,优秀者提升至normal级别"

documentation:
  - id: "DOC-001"
    name: "信息源目录"
    location: ".specify/sources/registry.yaml"
    content:
      - "信息源列表: 名称/URL/region/authority_score/健康状态"
      - "准入标准: 最低authority_score (30), 7日试用期"
      - "淘汰标准: 健康分数<30持续14天, 或内容质量差(用户投诉>5次/月)"
      - "健康指标: success_rate/avg_latency/content_quality_score"

  - id: "DOC-002"
    name: "输出契约与提示词版本手册"
    location: ".specify/contracts/"
    content:
      - "JSON契约: schemas/daily_report_vC-X.Y.Z.json"
      - "HTML模板: templates/report_vC-X.Y.Z.html"
      - "Markdown模板: templates/report_vC-X.Y.Z.md"
      - "提示词版本: prompts/summarize_vP-X.Y.Z.txt (含AI标注规则)"
      - "变更日志: CHANGELOG.md (记录每个版本的breaking changes)"

  - id: "DOC-003"
    name: "运行手册"
    location: "docs/operations/"
    content:
      - "SLO定义: 准时率99%, 可用性99.5%, 时效覆盖率95%"
      - "回滚程序: 配置回滚/提示词回滚/数据恢复步骤"
      - "告警规则: 失败率>10%, 延迟>5s, 成本超标, 准时率未达标"
      - "日常巡检清单: 信息源健康/成本趋势/去重效果/用户反馈"

  - id: "DOC-004"
    name: "审计导出说明"
    location: "docs/audit/"
    content:
      - "审计日志格式: JSON Lines, 包含timestamp/config_snapshot/sources_used/items_count/ai_calls/cost"
      - "导出命令: `python scripts/export_audit.py --start=2025-10-01 --end=2025-10-31 --format=csv`"
      - "合规报告模板: 月度成本报告/信息源健康报告/AI使用统计"
```

## Governance

This constitution is the foundational governance document for the 金融日报系统 (Financial Daily Report System). All development decisions, feature specifications, implementation plans, and operational procedures MUST align with the principles and policies defined herein.

### Amendment Procedure

1. Amendments MUST be proposed via RFC (Request for Comments) in `.specify/rfcs/[###-rfc-title].md`
2. Technical owner reviews technical feasibility and impact on existing components
3. Product owner reviews business value and risk acceptance
4. Approved amendments trigger:
   - Constitution version increment (following SemVer rules)
   - Propagation to dependent templates (plan, spec, tasks)
   - Update to CHANGELOG.md
   - Migration plan for existing implementations

### Compliance Review

- All feature specifications (spec.md) MUST reference relevant principles
- All implementation plans (plan.md) MUST include Constitution Check gate
- All pull requests MUST verify compliance with principles
- Monthly governance review to assess adherence and identify improvements

### Version Control

- **Constitution version**: Independent versioning following SemVer
  - MAJOR: Removal or backward-incompatible changes to principles
  - MINOR: Addition of new principles or governance sections
  - PATCH: Clarifications, wording improvements, non-semantic fixes

- **Cross-artifact sync**: Changes to constitution trigger automatic validation of:
  - `.specify/templates/plan-template.md` (Constitution Check alignment)
  - `.specify/templates/spec-template.md` (Requirements alignment)
  - `.specify/templates/tasks-template.md` (Task categorization alignment)

### Runtime Development Guidance

For day-to-day development guidance and agent-specific instructions, refer to:
- `.specify/templates/agent-file-template.md` (if exists)
- This constitution for non-negotiable principles
- Individual template files for workflow-specific guidance

---

**Version**: 1.0.0
**Ratified**: 2025-10-22
**Last Amended**: 2025-10-22
