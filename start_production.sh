#!/bin/bash

# 金融日报系统生产环境启动脚本
# 使用 gunicorn 作为 WSGI 服务器，性能更好

set -e

echo "============================================================"
echo "金融日报系统 - 生产环境启动"
echo "============================================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 配置参数
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-9998}
WORKERS=${WORKERS:-4}
LOG_LEVEL=${LOG_LEVEL:-info}

echo -e "${YELLOW}检查环境...${NC}"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
else
    echo -e "${RED}错误: 虚拟环境不存在，请先运行 start.sh${NC}"
    exit 1
fi

# 检查 gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "安装 gunicorn..."
    pip install gunicorn
fi

echo -e "${GREEN}启动配置:${NC}"
echo "  - Host: $HOST"
echo "  - Port: $PORT"
echo "  - Workers: $WORKERS"
echo "  - Log Level: $LOG_LEVEL"
echo "============================================================"

# 使用 gunicorn 启动
exec gunicorn app.main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind $HOST:$PORT \
    --log-level $LOG_LEVEL \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5
