"""测试邮件发送 API"""
import requests
import json

# API 端点
url = "http://localhost:9998/api/settings/send-email"

# 请求数据
data = {
    "report_date": "2025-10-14",
    "recipients": ["test@example.com"],
    "attach_pdf": False
}

print(f"测试邮件发送 API...")
print(f"URL: {url}")
print(f"数据: {json.dumps(data, indent=2, ensure_ascii=False)}\n")

try:
    response = requests.post(url, json=data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("\n✅ API 调用成功")
    else:
        print(f"\n❌ API 调用失败: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ 请求失败: {e}")
