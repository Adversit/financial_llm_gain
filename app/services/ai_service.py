"""AI分析服务 - 支持多种AI模型提供商"""
import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, List
import httpx
from app.utils.logger import ai_logger


class BaseAIClient(ABC):
    """AI客户端基类 - 定义统一接口"""
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict], **kwargs) -> str:
        """
        聊天补全接口
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
        
        Returns:
            AI响应文本
        """
        pass


class OpenAICompatibleClient(BaseAIClient):
    """
    OpenAI兼容的API客户端
    支持DeepSeek、OpenAI、Azure OpenAI等兼容OpenAI格式的API
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = ai_logger
    
    def chat_completion(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        调用聊天补全API
        
        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
        
        Returns:
            AI响应文本
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    return content.strip()
                    
            except httpx.HTTPStatusError as e:
                self.logger.error(f"API请求失败 (状态码 {e.response.status_code}): {e}")
                if e.response.status_code == 429:  # 速率限制
                    wait_time = 2 ** attempt
                    self.logger.warning(f"速率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                raise
            except httpx.TimeoutException:
                self.logger.error(f"API请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
            except Exception as e:
                self.logger.error(f"API请求异常: {e}")
                raise
        
        raise Exception(f"API请求失败，已重试 {self.max_retries} 次")


class AIService:
    """AI分析服务 - 提供文章摘要和报告生成功能"""
    
    def __init__(
        self,
        provider: str,
        api_key: str,
        base_url: str,
        model: str,
        prompt_dir: str = "prompts",
        **kwargs
    ):
        """
        初始化AI服务
        
        Args:
            provider: 提供商（deepseek/openai/azure/custom）
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            prompt_dir: 提示词目录
            **kwargs: 其他参数
        """
        self.provider = provider
        self.prompt_dir = Path(prompt_dir)
        self.logger = ai_logger
        
        # 创建AI客户端
        self.client = self._create_client(
            provider, api_key, base_url, model, **kwargs
        )
        
        # 加载提示词模板
        self.prompts = self._load_prompts()
    
    def _create_client(
        self,
        provider: str,
        api_key: str,
        base_url: str,
        model: str,
        **kwargs
    ) -> BaseAIClient:
        """
        创建AI客户端
        
        Args:
            provider: 提供商
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            **kwargs: 其他参数
        
        Returns:
            AI客户端实例
        """
        # 目前所有支持的提供商都使用OpenAI兼容格式
        if provider in ['deepseek', 'openai', 'azure', 'custom']:
            return OpenAICompatibleClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                **kwargs
            )
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
    
    def _load_prompts(self) -> Dict[str, str]:
        """
        加载提示词模板
        
        Returns:
            提示词字典
        """
        prompts = {}
        
        # 加载文章摘要提示词
        article_prompt_path = self.prompt_dir / "article_summary.txt"
        if article_prompt_path.exists():
            with open(article_prompt_path, 'r', encoding='utf-8') as f:
                prompts['article_summary'] = f.read()
        else:
            self.logger.warning(f"提示词文件不存在: {article_prompt_path}")
            prompts['article_summary'] = self._get_default_article_prompt()
        
        # 加载每日报告提示词
        report_prompt_path = self.prompt_dir / "daily_report.txt"
        if report_prompt_path.exists():
            with open(report_prompt_path, 'r', encoding='utf-8') as f:
                prompts['daily_report'] = f.read()
        else:
            self.logger.warning(f"提示词文件不存在: {report_prompt_path}")
            prompts['daily_report'] = self._get_default_report_prompt()
        
        return prompts
    
    def _get_default_article_prompt(self) -> str:
        """获取默认的文章摘要提示词"""
        return """请为以下金融资讯生成100-200字的摘要，并提取3-5个关键词。

标题：{title}
内容：{content}

请以JSON格式返回：
{{
  "summary": "摘要内容",
  "keywords": ["关键词1", "关键词2", "关键词3"]
}}"""
    
    def _get_default_report_prompt(self) -> str:
        """获取默认的每日报告提示词"""
        return """请根据以下各层面的金融资讯摘要，生成一份综合性的每日金融报告。

政治层面：
{political_summaries}

经济层面：
{economic_summaries}

技术层面：
{technical_summaries}

金融科技层面：
{fintech_summaries}

请生成一份结构化的报告，包括：
1. 各层面的核心要点
2. 层面之间的关联分析
3. 重要趋势和风险提示"""
    
    def summarize_article(
        self,
        title: str,
        content: str,
        prompt_template: Optional[str] = None
    ) -> Dict[str, any]:
        """
        生成文章摘要和关键词
        
        Args:
            title: 文章标题
            content: 文章内容
            prompt_template: 自定义提示词模板（可选）
        
        Returns:
            包含summary和keywords的字典
        """
        try:
            # 使用自定义或默认提示词
            template = prompt_template or self.prompts['article_summary']
            
            # 截断过长的内容（避免超过token限制）
            max_content_length = 3000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            # 构建提示词
            prompt = template.format(title=title, content=content)
            
            # 调用AI
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages)
            
            # 记录原始响应（用于调试）
            self.logger.debug(f"AI原始响应: {response[:500]}")
            
            # 解析JSON响应
            result = self._parse_json_response(response)
            
            # 验证结果
            if 'summary' not in result or 'keywords' not in result:
                raise ValueError("AI响应格式不正确")
            
            self.logger.info(f"成功生成摘要: {title[:30]}...")
            
            return result
            
        except Exception as e:
            self.logger.error(f"生成摘要失败: {e}", exc_info=True)
            # 返回默认值
            return {
                "summary": f"摘要生成失败: {str(e)}",
                "keywords": []
            }
    
    def generate_daily_report(
        self,
        summaries_by_category: Dict[str, List[str]],
        articles_data: Optional[List[Dict]] = None,
        prompt_template: Optional[str] = None
    ) -> str:
        """
        生成每日总报告
        
        Args:
            summaries_by_category: 按层面分组的摘要字典
            articles_data: 文章数据列表（包含标题、摘要、关键词）
            prompt_template: 自定义提示词模板（可选）
        
        Returns:
            总报告文本
        """
        try:
            # 使用自定义或默认提示词
            template = prompt_template or self.prompts['daily_report']
            
            # 准备各层面的摘要文本
            political = self._format_summaries(
                summaries_by_category.get('政治', [])
            )
            economic = self._format_summaries(
                summaries_by_category.get('经济', [])
            )
            technical = self._format_summaries(
                summaries_by_category.get('技术', [])
            )
            fintech = self._format_summaries(
                summaries_by_category.get('金融科技', [])
            )
            
            # 提取国内外信息
            domestic_summaries = []
            foreign_summaries = []
            
            if articles_data:
                for article in articles_data:
                    keywords = article.get('keywords', [])
                    summary = article.get('summary', '')
                    title = article.get('title', '')
                    
                    # 从关键词中判断国内外
                    is_domestic = False
                    is_foreign = False
                    
                    for kw in keywords:
                        if isinstance(kw, dict):
                            word = kw.get('word', '')
                            kw_type = kw.get('type', '')
                            if kw_type == '国内外信息':
                                if word == '国内':
                                    is_domestic = True
                                elif word == '国外':
                                    is_foreign = True
                    
                    # 添加到对应列表
                    if is_domestic and summary:
                        domestic_summaries.append(f"{title}: {summary}")
                    if is_foreign and summary:
                        foreign_summaries.append(f"{title}: {summary}")
            
            # 格式化国内外摘要
            domestic = self._format_summaries(domestic_summaries)
            foreign = self._format_summaries(foreign_summaries)
            
            # 构建提示词
            prompt = template.format(
                domestic_summaries=domestic,
                foreign_summaries=foreign,
                political_summaries=political,
                economic_summaries=economic,
                technical_summaries=technical,
                fintech_summaries=fintech
            )
            
            # 记录输入内容（用于调试）
            self.logger.debug(f"报告生成输入 - 国内信息: {len(domestic_summaries)} 条")
            self.logger.debug(f"报告生成输入 - 国外信息: {len(foreign_summaries)} 条")
            self.logger.debug(f"报告生成输入 - 政治层面: {political[:200]}...")
            self.logger.debug(f"报告生成输入 - 经济层面: {economic[:200]}...")
            self.logger.debug(f"报告生成输入 - 技术层面: {technical[:200]}...")
            self.logger.debug(f"报告生成输入 - 金融科技层面: {fintech[:200]}...")
            self.logger.info(f"完整提示词长度: {len(prompt)} 字符")
            
            # 调用AI
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages,
                max_tokens=3000  # 报告可能较长
            )
            
            self.logger.info("成功生成每日报告")
            
            return response
            
        except Exception as e:
            self.logger.error(f"生成每日报告失败: {e}", exc_info=True)
            return f"报告生成失败: {str(e)}"
    
    def _format_summaries(self, summaries: List[str]) -> str:
        """
        格式化摘要列表
        
        Args:
            summaries: 摘要列表
        
        Returns:
            格式化后的文本
        """
        if not summaries:
            return "（本层面暂无内容）"
        
        # 限制摘要数量，避免内容过多导致超时
        max_summaries = 15
        if len(summaries) > max_summaries:
            self.logger.warning(f"摘要数量过多({len(summaries)})，仅使用前{max_summaries}条")
            summaries = summaries[:max_summaries]
        
        formatted = []
        for i, summary in enumerate(summaries, 1):
            # 限制单条摘要长度
            max_length = 300
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            formatted.append(f"{i}. {summary}")
        
        return "\n".join(formatted)
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        解析JSON响应
        
        Args:
            response: AI响应文本
        
        Returns:
            解析后的字典
        """
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 移除可能的 markdown 代码块标记
            cleaned = response.strip()
            if cleaned.startswith('```'):
                # 移除开头的 ```json 或 ```
                lines = cleaned.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                # 移除结尾的 ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned = '\n'.join(lines)
            
            # 尝试解析清理后的内容
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # 尝试提取JSON部分
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = cleaned[start:end]
                    return json.loads(json_str)
                raise ValueError(f"无法解析JSON响应: {response[:200]}")
