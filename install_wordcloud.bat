@echo off
echo ========================================
echo 安装词云功能依赖
echo ========================================
echo.

echo 正在安装依赖包...
pip install wordcloud pillow jieba

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 词云功能已就绪，可以启动系统测试。
echo.
echo 启动命令: python start_server.py
echo 访问地址: http://localhost:5000/wordcloud.html
echo.
pause
