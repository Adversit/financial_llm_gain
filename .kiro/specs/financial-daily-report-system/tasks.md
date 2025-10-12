# 实施计划

- [x] 1. 项目初始化和基础设施搭建



  - 创建项目目录结构
  - 创建requirements.txt文件，包含所有必要依赖（FastAPI、SQLAlchemy、feedparser、requests、beautifulsoup4、pyyaml、apscheduler等）
  - 创建config.yaml配置文件模板
  - 创建.env.example环境变量示例文件
  - 设置日志配置模块（app/utils/logger.py）
  - _需求: 1.1, 2.1, 2.2_

- [x] 2. 数据库层实现





  - [ ] 2.1 创建数据库连接和配置
    - 实现app/database.py，配置SQLAlchemy引擎和会话
    - 创建Base类用于模型继承


    - _需求: 12.1, 12.2_
  
  - [ ] 2.2 实现数据模型
    - 创建Source模型（app/models/source.py）
    - 创建Article模型（app/models/article.py）
    - 创建Summary模型（app/models/summary.py）
    - 创建DailyReport模型（app/models/daily_report.py）


    - 创建EmailSubscription模型（app/models/email_subscription.py）





    - 创建UserConfig模型（app/models/user_config.py）
    - _需求: 12.3, 12.4_
  
  - [x] 2.3 创建数据库初始化脚本


    - 实现scripts/init_db.py，创建所有表
    - 实现scripts/seed_data.py，填充初始信息源数据
    - _需求: 2.1, 2.2, 2.3_

- [x] 3. 爬虫模块核心实现


  - [ ] 3.1 实现基础爬虫类
    - 创建BaseCrawler抽象类（app/crawlers/base.py）
    - 实现validate_content方法进行内容验证
    - 定义Article数据类用于返回标准化数据

    - _需求: 1.5, 1.6, 3.1, 3.2, 3.4_

  
  - [ ] 3.2 实现RSS爬虫
    - 创建RSSCrawler类（app/crawlers/rss_crawler.py）

    - 使用feedparser解析RSS源

    - 提取标题、链接、内容、发布时间





    - 实现错误处理和重试机制
    - _需求: 1.1, 1.2, 1.5_
  
  - [ ] 3.3 实现RSSHub爬虫
    - 创建RSSHubCrawler类（app/crawlers/rsshub_crawler.py）

    - 构建RSSHub URL并获取RSS

    - 复用RSS解析逻辑
    - _需求: 1.1, 1.3, 1.5_
  



  - [ ] 3.4 实现爬虫工厂
    - 创建CrawlerFactory类（app/crawlers/factory.py）
    - 根据配置动态创建爬虫实例
    - 支持自定义爬虫类的动态加载
    - _需求: 3.3, 3.5_
  
  - [x] 3.5 创建自定义爬虫示例

    - 创建工业和信息化部爬虫（app/crawlers/custom/miit_crawler.py）

    - 创建中国证监会爬虫（app/crawlers/custom/csrc_crawler.py）
    - 使用requests和BeautifulSoup4实现网页解析
    - _需求: 1.4, 2.4, 3.1, 3.2, 3.3_

- [ ] 4. 数据处理服务实现
  - [ ] 4.1 实现数据清洗服务
    - 创建DataCleaner类（app/services/cleaner_service.py）
    - 实现按日期过滤功能（仅保留昨天的文章）
    - 实现内容相关性过滤（去除非金融内容）
    - 实现去重逻辑（基于链接和标题）
    - _需求: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 4.2 实现爬虫服务
    - 创建CrawlerService类（app/services/crawler_service.py）
    - 实现批量爬取所有启用的信息源
    - 集成爬虫工厂和数据清洗器
    - 实现并发爬取控制
    - 保存爬取结果到数据库
    - _需求: 1.1, 1.7, 2.1, 2.2_

- [x] 5. AI分析服务实现
  - [x] 5.1 实现DeepSeek客户端
    - 创建DeepSeekClient类（app/services/ai_service.py）
    - 实现HTTP请求封装
    - 实现summarize_article方法生成摘要和关键词
    - 实现generate_daily_report方法生成每日总报告
    - 实现错误处理和重试机制
    - 实现速率限制控制
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 5.2 集成AI服务到数据流程

    - 在CrawlerService中调用AI服务生成摘要
    - 保存摘要和关键词到数据库
    - 实现批量处理逻辑
    - _需求: 5.4_






- [ ] 6. 报告生成服务实现
  - [ ] 6.1 创建报告模板
    - 创建HTML报告模板（templates/report.html）
    - 使用Jinja2模板语法


    - 设计响应式布局和样式
    - _需求: 6.4_
  
  - [ ] 6.2 实现报告生成器
    - 创建ReportGenerator类（app/services/report_service.py）
    - 实现generate_html方法使用Jinja2渲染
    - 实现generate_pdf方法将HTML转换为PDF

    - 实现generate_markdown方法生成Markdown格式
    - 按层面分组整理文章摘要
    - 调用AI服务生成各层面总结
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.5_





  
  - [ ] 6.3 实现报告数据聚合
    - 从数据库查询指定日期的所有文章和摘要
    - 按层面（政治、经济、技术、金融科技）分组
    - 构建报告数据结构
    - 保存报告到数据库

    - _需求: 6.1, 6.2, 12.3_







- [ ] 7. 邮件发送服务实现
  - [ ] 7.1 实现邮件发送器
    - 创建EmailSender类（app/services/email_service.py）
    - 配置网易邮箱SMTP连接

    - 实现send_report方法发送HTML邮件和PDF附件
    - 支持多收件人发送


    - 实现错误处理和重试机制
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 7.2 创建邮件模板
    - 创建邮件HTML模板（templates/email_template.html）
    - 设计邮件样式





    - _需求: 7.4_

- [ ] 8. 任务调度实现
  - [ ] 8.1 实现任务调度器
    - 创建TaskScheduler类（app/scheduler/tasks.py）
    - 使用APScheduler配置定时任务

    - 实现run_daily_pipeline方法执行完整流程

    - 配置每日执行时间（默认早上8点）
    - _需求: 1.1, 4.1, 5.1, 6.1, 7.1_
  
  - [ ] 8.2 集成完整数据流程
    - 在pipeline中依次调用：数据采集 -> 数据清洗 -> AI摘要 -> 报告生成 -> 邮件发送
    - 实现流程错误处理和日志记录
    - _需求: 1.1, 4.1, 5.1, 6.1, 7.1_


- [ ] 9. Pydantic模式定义
  - 创建Source相关模式（app/schemas/source.py）
  - 创建Article相关模式（app/schemas/article.py）
  - 创建Email相关模式（app/schemas/email.py）

  - 创建CustomReport相关模式（app/schemas/custom_report.py）
  - 定义请求和响应模型
  - _需求: 8.1, 8.2, 9.1, 10.1, 11.1_

- [ ] 10. Web API实现 - 报告相关
  - [ ] 10.1 实现报告API路由
    - 创建reports路由（app/api/reports.py）

    - 实现GET /reports - 获取报告列表
    - 实现GET /reports/{date} - 获取指定日期报告
    - 实现GET /articles/{date}/{category} - 获取指定日期和层面的文章
    - 实现GET /article/{article_id} - 获取文章详情
    - _需求: 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 11. Web API实现 - 信息源管理

  - [ ] 11.1 实现信息源API路由
    - 创建sources路由（app/api/sources.py）
    - 实现GET /sources - 获取所有信息源列表
    - 实现POST /sources/{source_id}/toggle - 启用/停用信息源
    - 实现POST /sources/add - 添加新信息源
    - 实现POST /sources/test - 测试信息源可用性
    - _需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_



  
  - [ ] 11.2 实现信息源测试功能
    - 在sources服务中实现test_source方法
    - 自动测试RSS和RSSHub方式
    - 返回测试结果和建议
    - _需求: 9.6, 9.7, 9.8_

- [ ] 12. Web API实现 - 邮件管理
  - 创建emails路由（app/api/emails.py）
  - 实现GET /emails - 获取邮件订阅列表
  - 实现POST /emails/add - 添加订阅邮箱
  - 实现DELETE /emails/{email_id} - 删除订阅邮箱

  - 实现邮箱格式验证
  - _需求: 10.1, 10.2, 10.3, 10.4_

- [ ] 13. Web API实现 - 个性化报告
  - 创建custom_reports路由（app/api/custom_reports.py）
  - 实现POST /custom-report - 生成个性化报告
  - 支持选择信息源
  - 支持自定义AI提示词（可选）
  - 保存用户配置到数据库
  - _需求: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_


- [ ] 14. FastAPI应用主入口
  - 创建app/main.py
  - 初始化FastAPI应用
  - 注册所有API路由
  - 配置静态文件服务
  - 配置CORS中间件
  - 启动时初始化数据库
  - 启动时启动任务调度器
  - 配置异常处理器
  - _需求: 8.1_

- [ ] 15. 前端页面实现 - 主页和报告展示
  - [x] 15.1 创建主页模板


    - 创建templates/index.html
    - 显示每日报告列表（按日期）
    - 实现日期选择器
    - 显示每日总结报告
    - _需求: 8.2, 8.6_
  
  - [ ] 15.2 创建报告详情页面
    - 创建templates/report_detail.html
    - 按层面展示文章列表
    - 实现层面折叠/展开
    - 点击文章显示详情（标题、链接、内容、摘要、关键词）
    - _需求: 8.3, 8.4, 8.5_

- [ ] 16. 前端页面实现 - 信息源管理
  - 创建templates/sources.html
  - 显示所有信息源列表

  - 显示信息源状态（启用/停用）
  - 实现启停按钮
  - 实现添加信息源表单
  - 实现信息源测试功能
  - 显示测试结果
  - _需求: 9.1, 9.2, 9.3, 9.5, 9.6, 9.7, 9.8_

- [ ] 17. 前端页面实现 - 邮件和个性化配置
  - [ ] 17.1 创建邮件管理页面
    - 创建templates/emails.html
    - 显示订阅邮箱列表
    - 实现添加邮箱表单
    - 实现删除邮箱功能
    - _需求: 10.1, 10.2, 10.3_
  
  - [ ] 17.2 创建个性化报告页面
    - 创建templates/custom_report.html
    - 实现信息源多选框
    - 实现提示词编辑器（可选）
    - 提供默认模板
    - 实现生成报告按钮
    - _需求: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 18. 前端静态资源
  - 创建CSS样式文件（static/css/style.css）
  - 创建JavaScript交互文件（static/js/main.js）
  - 实现AJAX请求处理
  - 实现前端表单验证
  - 实现加载动画和提示信息
  - _需求: 8.1, 9.1, 10.1, 11.1_

- [ ] 19. 配置文件和环境变量
  - 完善config.yaml配置文件
  - 添加所有信息源配置
  - 配置DeepSeek API
  - 配置邮件SMTP
  - 配置任务调度时间
  - 创建配置加载模块（app/config.py）
  - 支持从环境变量覆盖配置
  - _需求: 2.1, 2.2, 2.3, 2.4, 5.1, 7.2_

- [ ] 20. 错误处理和日志
  - 实现全局异常处理器
  - 为每个模块配置专用logger
  - 实现日志轮转
  - 记录关键操作和错误
  - 实现错误重试机制
  - _需求: 1.7, 5.5, 7.5_

- [ ]* 21. 测试实现
  - [ ]* 21.1 单元测试
    - 编写爬虫模块测试（tests/test_crawlers.py）
    - 编写数据清洗测试（tests/test_cleaner.py）
    - 编写报告生成测试（tests/test_report.py）
    - 使用pytest和mock
    - _需求: 1.1, 4.1, 6.1_
  
  - [ ]* 21.2 集成测试
    - 编写API端点测试（tests/test_api.py）
    - 编写完整流程测试（tests/test_pipeline.py）
    - 使用测试数据库
    - Mock外部API调用
    - _需求: 8.1, 9.1, 10.1, 11.1_

- [ ] 22. 文档和部署
  - [ ] 22.1 创建项目文档
    - 编写README.md
    - 编写安装指南
    - 编写使用说明
    - 编写API文档
    - _需求: 13.1_
  
  - [ ] 22.2 创建部署配置
    - 创建Dockerfile
    - 创建docker-compose.yml（可选）
    - 创建部署脚本
    - _需求: 13.1_

- [ ] 23. 系统集成和验证
  - 运行完整的数据采集流程
  - 验证所有信息源可用性
  - 测试AI摘要生成
  - 测试报告生成（HTML和PDF）
  - 测试邮件发送
  - 测试Web界面所有功能
  - 修复发现的问题
  - _需求: 1.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1, 11.1_
