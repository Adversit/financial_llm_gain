#!/bin/bash

# 金融日报系统启动脚本 (Ubuntu/Linux)
# 使用方法: bash start.sh 或 ./start.sh

set -e

echo "============================================================"
echo "金融日报系统 - Linux启动脚本"
echo "============================================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}[1/5] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python版本: $PYTHON_VERSION${NC}"

echo -e "${YELLOW}[2/5] 检查虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
fi

echo -e "${YELLOW}[3/5] 激活虚拟环境...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"

echo -e "${YELLOW}[4/5] 检查依赖...${NC}"
if [ -f "requirements.txt" ]; then
    echo "正在安装/更新依赖..."
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${RED}警告: requirements.txt 不存在${NC}"
fi

echo -e "${YELLOW}[5/5] 启动服务器...${NC}"
echo ""

# 启动服务器
python3 start_server.py
