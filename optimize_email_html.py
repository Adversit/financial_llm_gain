"""优化邮件 HTML 格式"""
import re

def optimize_html_for_email(html_content: str) -> str:
    """
    优化 HTML 以适配邮件客户端
    - 增加段落间距
    - 优化列表显示
    - 添加内联样式
    """
    # 为段落添加间距
    html_content = html_content.replace('<p>', '<p style="margin-bottom: 15px; line-height: 1.8;">')
    
    # 为标题添加间距
    html_content = html_content.replace(
        '<h3>',
        '<h3 style="margin-top: 25px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #ecf0f1; color: #2c3e50;">'
    )
    html_content = html_content.replace(
        '<h4>',
        '<h4 style="margin-top: 20px; margin-bottom: 12px; color: #34495e;">'
    )
    
    # 为列表添加间距
    html_content = html_content.replace('<ul>', '<ul style="margin-top: 10px; margin-bottom: 20px; margin-left: 25px;">')
    html_content = html_content.replace('<ol>', '<ol style="margin-top: 10px; margin-bottom: 20px; margin-left: 25px;">')
    html_content = html_content.replace('<li>', '<li style="margin-bottom: 12px; line-height: 1.8;">')
    
    # 为分隔线添加间距
    html_content = html_content.replace('<hr>', '<hr style="margin: 30px 0; border: none; border-top: 2px solid #ecf0f1;">')
    
    # 为 strong 标签添加样式
    html_content = html_content.replace('<strong>', '<strong style="color: #2c3e50;">')
    
    return html_content


# 测试
if __name__ == "__main__":
    test_html = """
    <p>这是一段测试文本</p>
    <h3>标题3</h3>
    <ul>
        <li>列表项1</li>
        <li>列表项2</li>
    </ul>
    <hr>
    <strong>粗体文本</strong>
    """
    
    optimized = optimize_html_for_email(test_html)
    print("优化后的 HTML:")
    print(optimized)
