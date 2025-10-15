"""
测试新添加的自定义爬虫
"""
import sys
from app.crawlers.factory import CrawlerFactory
from app.utils.logger import setup_logger

logger = setup_logger('test_crawlers')

def test_crawler(crawler_class: str, source_name: str, url: str):
    """测试单个爬虫"""
    print(f"\n{'='*80}")
    print(f"测试爬虫: {source_name} ({crawler_class})")
    print(f"{'='*80}")
    
    try:
        # 创建爬虫实例
        crawler = CrawlerFactory.create_crawler(
            source_type='custom',
            source_name=source_name,
            url=url,
            crawler_class=crawler_class
        )
        
        # 执行爬取
        articles = crawler.fetch()
        
        if articles:
            print(f"✅ 成功爬取 {len(articles)} 篇文章")
            print(f"\n前3篇文章:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n{i}. {article.get('title', 'N/A')}")
                print(f"   链接: {article.get('link', 'N/A')}")
                print(f"   时间: {article.get('published', 'N/A')}")
            return True
        else:
            print(f"⚠️  爬取成功但未获取到文章")
            return False
            
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """测试所有新爬虫"""
    print("="*80)
    print("测试新添加的自定义爬虫")
    print("="*80)
    
    crawlers = [
        ("EastMoneyCrawler", "东方财富网", "https://finance.eastmoney.com/"),
        ("XinhuaCrawler", "新华社", "http://www.news.cn/"),
        ("Kr36Crawler", "36氪", "https://36kr.com/"),
        ("CACCrawler", "国家互联网信息办公室", "http://www.cac.gov.cn/"),
    ]
    
    results = []
    for crawler_class, source_name, url in crawlers:
        success = test_crawler(crawler_class, source_name, url)
        results.append((source_name, success))
    
    # 打印总结
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for source_name, success in results:
        status = "✅ 可用" if success else "❌ 不可用"
        print(f"{status:12} {source_name}")
    
    print(f"\n总计: {success_count}/{total_count} 个爬虫可用")
    print(f"成功率: {success_count/total_count*100:.1f}%")


if __name__ == "__main__":
    main()
