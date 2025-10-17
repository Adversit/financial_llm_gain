"""
金融日报系统启动脚本
支持局域网访问，显示友好的访问地址
"""
import socket
import sys
import warnings
import uvicorn
from app.utils.logger import app_logger

# 过滤 jieba 的 pkg_resources 弃用警告
warnings.filterwarnings("ignore", category=UserWarning, module="jieba")


def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到外部地址（不会真正发送数据）
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def print_startup_info(host: str, port: int):
    """打印启动信息"""
    local_ip = get_local_ip()
    
    print("\n" + "=" * 60)
    print("🚀 金融日报系统启动成功！")
    print("=" * 60)
    print("\n📍 访问地址：")
    print(f"   本机访问:    http://localhost:{port}")
    if local_ip != "127.0.0.1":
        print(f"   局域网访问:  http://{local_ip}:{port}")
    print("\n📚 功能页面：")
    print(f"   - 主页:         http://localhost:{port}/")
    print(f"   - API文档:      http://localhost:{port}/docs")
    print(f"   - 信息源管理:   http://localhost:{port}/sources.html")
    print(f"   - 邮件管理:     http://localhost:{port}/emails.html")
    print("\n💡 提示：")
    print("   - 按 Ctrl+C 停止服务")
    print("   - 日志文件: logs/app.log")
    print("=" * 60 + "\n")


class CustomUvicornServer(uvicorn.Server):
    """自定义Uvicorn服务器，隐藏默认的启动信息"""
    
    def install_signal_handlers(self):
        """安装信号处理器"""
        pass


def main():
    """主函数"""
    host = "0.0.0.0"
    port = 9998
    
    # 打印自定义启动信息
    print_startup_info(host, port)
    
    # 配置uvicorn
    config = uvicorn.Config(
        "app.main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=True,  # 开发环境启用自动重载
    )
    
    # 创建并运行服务器
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
