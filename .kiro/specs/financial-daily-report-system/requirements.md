# 需求文档

## 简介

金融日报系统是一个自动化的信息聚合和分析平台，用于从多个信息源收集金融相关资讯，通过AI进行智能总结，并生成每日报告发送给指定用户。系统支持多种数据获取方式（RSS、RSSHub、网络爬虫），提供灵活的信息源管理和个性化报告定制功能。

## 需求

### 需求 1：多源信息获取

**用户故事：** 作为系统管理员，我希望系统能够从多个信息源自动获取金融资讯，以便全面覆盖政治、经济、技术和金融科技等多个层面的信息。

#### 验收标准

1. WHEN 系统启动信息采集任务 THEN 系统 SHALL 按照优先级顺序尝试使用RSS源、RSSHub源、自定义爬虫三种方式获取信息
2. WHEN 使用RSS源获取信息 THEN 系统 SHALL 从配置文件中读取RSS订阅地址并解析内容
3. WHEN RSS源不可用 THEN 系统 SHALL 自动切换到RSSHub源（http://101.42.187.241:1200/）进行获取
4. WHEN RSS和RSSHub均不可用 THEN 系统 SHALL 使用自定义网络爬虫获取信息
5. WHEN 爬取信息 THEN 系统 SHALL 至少获取标题、链接、内容、发布时间四个字段
6. WHEN 爬取完成 THEN 系统 SHALL 验证内容字段的字数以确保信息源有效
7. WHEN 保存到数据库 THEN 系统 SHALL 存储标题、链接、内容、发布时间和保存时间五个字段

### 需求 2：信息源配置管理

**用户故事：** 作为系统管理员，我希望能够在配置文件中管理不同类型的信息源，以便灵活控制数据获取方式。

#### 验收标准

1. WHEN 系统初始化 THEN 系统 SHALL 从config.yaml读取信息源配置
2. WHEN 读取配置 THEN 配置文件 SHALL 按照获取方式（RSS源、RSSHub源、自定义爬虫）分组存储信息源
3. WHEN 配置信息源 THEN 每个信息源 SHALL 包含名称、类别（政治/经济/技术/金融科技）、获取方式、地址等属性
4. WHEN 配置包含以下信息源 THEN 系统 SHALL 支持：
   - 政治层面：新闻联播、工业和信息化部(MIIT)、人民日报、新华社、中国证券监督管理委员会(CSRC)
   - 经济层面：艾瑞咨询(iResearch)、头豹研究院(LeadLeo)、36氪(36Kr)、财新网(Caixin)、虎嗅(Huxiu)
   - 技术层面：量子位(QbitAI)、arXiv计算金融(cs.FI)、机器之心、AI前线、第一财经
   - 金融科技层面：未央网(WeiyangX)

### 需求 3：可扩展的爬虫架构

**用户故事：** 作为开发人员，我希望系统提供可扩展的爬虫基类，以便为新的信息源快速开发专用爬虫。

#### 验收标准

1. WHEN 设计爬虫架构 THEN 系统 SHALL 提供一个基础爬虫类（BaseCrawler）
2. WHEN 添加新信息源 THEN 开发人员 SHALL 能够继承BaseCrawler类创建专用爬虫
3. WHEN 实现专用爬虫 THEN 爬虫 SHALL 重写获取内容的方法并返回标准化数据格式
4. WHEN 爬虫返回数据 THEN 数据格式 SHALL 包含title、link、content、publish_time字段
5. WHEN 系统加载爬虫 THEN 系统 SHALL 自动发现并注册所有继承自BaseCrawler的爬虫类

### 需求 4：数据清洗与过滤

**用户故事：** 作为系统用户，我希望系统只保留相关的金融信息，以便提高报告质量和阅读效率。

#### 验收标准

1. WHEN 数据清洗开始 THEN 系统 SHALL 根据发布时间筛选昨天一天的文章
2. WHEN 过滤时间范围 THEN 系统 SHALL 排除发布时间不在昨天00:00:00到23:59:59之间的内容
3. WHEN 内容过滤 THEN 系统 SHALL 使用AI或关键词匹配去除与金融信息无关的内容
4. WHEN 过滤完成 THEN 系统 SHALL 保留清洗后的数据用于后续处理

### 需求 5：AI智能摘要

**用户故事：** 作为报告阅读者，我希望每篇文章都有简洁的AI摘要和关键词，以便快速了解核心内容。

#### 验收标准

1. WHEN 文章通过清洗 THEN 系统 SHALL 调用DeepSeek API生成摘要
2. WHEN 生成摘要 THEN 摘要 SHALL 控制在100-200字之间
3. WHEN 生成摘要 THEN 系统 SHALL 同时提取3-5个关键词
4. WHEN AI处理完成 THEN 系统 SHALL 将摘要和关键词保存到数据库
5. WHEN API调用失败 THEN 系统 SHALL 记录错误并跳过该文章或使用备用方案

### 需求 6：每日报告生成

**用户故事：** 作为报告接收者，我希望系统能够自动生成结构化的每日金融报告，以便系统性地了解各层面的重要信息。

#### 验收标准

1. WHEN 所有文章摘要完成 THEN 系统 SHALL 按层面（政治、经济、技术、金融科技）分组整理
2. WHEN 生成报告 THEN 系统 SHALL 使用DeepSeek API对每个层面的摘要进行二次总结
3. WHEN 整合内容 THEN 系统 SHALL 生成包含所有层面总结的完整报告
4. WHEN 输出报告 THEN 系统 SHALL 生成HTML格式和Markdown转PDF格式两种版本
5. WHEN 报告生成 THEN 报告 SHALL 包含日期、各层面总结、重要文章链接等信息

### 需求 7：邮件发送功能

**用户故事：** 作为报告订阅者，我希望每天自动收到金融日报邮件，以便及时获取最新资讯。

#### 验收标准

1. WHEN 报告生成完成 THEN 系统 SHALL 使用网易邮箱SMTP服务发送邮件
2. WHEN 配置邮件 THEN 系统 SHALL 从配置文件读取发件人邮箱和密码
3. WHEN 发送邮件 THEN 系统 SHALL 支持发送给多个收件人地址
4. WHEN 邮件内容 THEN 邮件 SHALL 包含HTML格式报告正文和PDF附件
5. WHEN 发送失败 THEN 系统 SHALL 记录错误日志并支持重试机制

### 需求 8：Web前端界面

**用户故事：** 作为系统用户，我希望通过Web界面查看历史报告和管理信息源，以便灵活使用系统功能。

#### 验收标准

1. WHEN 访问系统 THEN 系统 SHALL 提供基于FastAPI的Web界面
2. WHEN 进入主页 THEN 用户 SHALL 能够按日期选择查看每日报告
3. WHEN 浏览报告 THEN 用户 SHALL 能够按层面（政治、经济、技术、金融科技）展开查看
4. WHEN 查看层面 THEN 用户 SHALL 能够看到该层面下所有信息源的文章列表
5. WHEN 点击文章 THEN 系统 SHALL 显示原始内容、AI摘要和关键词
6. WHEN 查看主页 THEN 主页 SHALL 显示每日生成的总结报告

### 需求 9：信息源管理功能

**用户故事：** 作为系统管理员，我希望能够启用/停用信息源和添加新信息源，以便灵活控制数据采集范围。

#### 验收标准

1. WHEN 访问管理界面 THEN 用户 SHALL 看到所有信息源的列表和启停状态
2. WHEN 系统初始化 THEN 所有信息源 SHALL 默认为启用状态
3. WHEN 点击启停按钮 THEN 系统 SHALL 切换该信息源的启用/停用状态
4. WHEN 信息源被停用 THEN 系统 SHALL 在采集任务中跳过该信息源
5. WHEN 添加新信息源 THEN 用户 SHALL 能够输入信息源名称、RSS地址、RSSHub路径
6. WHEN 提交新信息源 THEN 系统 SHALL 自动测试RSS和RSSHub方式是否可用
7. WHEN 测试成功 THEN 系统 SHALL 自动将新信息源集成到配置文件
8. WHEN 测试失败 THEN 系统 SHALL 提示"需要自行构建爬虫文件"并提供爬虫模板

### 需求 10：邮件订阅管理

**用户故事：** 作为系统管理员，我希望能够管理邮件订阅列表，以便控制报告的发送对象。

#### 验收标准

1. WHEN 访问邮件管理界面 THEN 用户 SHALL 能够查看当前所有订阅邮箱
2. WHEN 添加邮箱 THEN 用户 SHALL 能够输入新的邮箱地址并保存
3. WHEN 删除邮箱 THEN 用户 SHALL 能够从订阅列表中移除指定邮箱
4. WHEN 修改配置 THEN 系统 SHALL 实时更新邮件发送列表

### 需求 11：个性化报告定制

**用户故事：** 作为高级用户，我希望能够自定义报告内容和AI提示词，以便生成符合个人需求的报告。

#### 验收标准

1. WHEN 访问定制界面 THEN 用户 SHALL 能够选择要包含的信息源
2. WHEN 选择信息源 THEN 系统 SHALL 仅使用选中的信息源生成报告
3. WHEN 定制提示词 THEN 用户 SHALL 能够修改单篇文档总结的AI提示词（可选功能）
4. WHEN 定制提示词 THEN 用户 SHALL 能够修改单日总报告的AI提示词（可选功能）
5. WHEN 未自定义提示词 THEN 系统 SHALL 使用默认模板
6. WHEN 保存定制配置 THEN 系统 SHALL 将配置保存为用户个人配置
7. WHEN 生成个性化报告 THEN 系统 SHALL 按照用户配置生成并发送报告

### 需求 12：数据持久化

**用户故事：** 作为系统，我需要持久化存储所有爬取的原始内容和AI总结结果，以便历史查询和数据分析。

#### 验收标准

1. WHEN 系统初始化 THEN 系统 SHALL 创建SQLite数据库
2. WHEN 爬取内容 THEN 系统 SHALL 保存原始文章内容到数据库
3. WHEN AI总结完成 THEN 系统 SHALL 保存摘要和关键词到数据库
4. WHEN 存储数据 THEN 数据库 SHALL 包含文章表、摘要表、信息源表、用户配置表
5. WHEN 查询历史 THEN 系统 SHALL 支持按日期、信息源、层面等条件查询

### 需求 13：系统扩展性预留

**用户故事：** 作为开发人员，我希望系统架构具有良好的扩展性，以便未来添加新功能。

#### 验收标准

1. WHEN 设计系统架构 THEN 系统 SHALL 采用模块化设计
2. WHEN 设计API THEN API SHALL 预留扩展接口
3. WHEN 设计数据库 THEN 数据库 SHALL 预留扩展字段
4. WHEN 设计前端 THEN 前端 SHALL 预留功能模块入口
5. WHEN 添加新功能 THEN 系统 SHALL 支持插件式扩展而不影响现有功能
