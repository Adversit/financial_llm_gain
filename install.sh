#!/bin/bash

# 金融日报系统安装脚本
# 用于首次部署到 Ubuntu 服务器

set -e

echo "============================================================"
echo "金融日报系统 - 安装脚本"
echo "============================================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}[1/6] 检查系统依赖...${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "安装 Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi
echo -e "${GREEN}✓ Python3: $(python3 --version)${NC}"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "安装 pip3..."
    sudo apt-get install -y python3-pip
fi
echo -e "${GREEN}✓ pip3: $(pip3 --version)${NC}"

echo -e "${YELLOW}[2/6] 创建虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

echo -e "${YELLOW}[3/6] 激活虚拟环境并安装依赖...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"

echo -e "${YELLOW}[4/6] 创建必要的目录...${NC}"
mkdir -p data logs static/images
echo -e "${GREEN}✓ 目录创建完成${NC}"

echo -e "${YELLOW}[5/6] 检查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}创建 .env 配置文件...${NC}"
    cat > .env << 'EOF'
# AI配置
AI_API_KEY=your-api-key-here
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat

# 邮件配置
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
SMTP_USERNAME=your-email@163.com
SMTP_PASSWORD=your-password-here
SMTP_FROM_NAME=金融日报系统

# 数据库配置
DATABASE_URL=sqlite:///./data/financial_daily.db

# 日志配置
LOG_LEVEL=INFO
EOF
    echo -e "${RED}⚠ 请编辑 .env 文件，填入正确的配置信息${NC}"
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

echo -e "${YELLOW}[6/6] 设置脚本执行权限...${NC}"
chmod +x start.sh start_production.sh install.sh
echo -e "${GREEN}✓ 权限设置完成${NC}"

echo ""
echo "============================================================"
echo -e "${GREEN}安装完成！${NC}"
echo "============================================================"
echo ""
echo "下一步操作："
echo "1. 编辑 .env 文件，配置 AI API 和邮件信息"
echo "   nano .env"
echo ""
echo "2. 启动开发服务器："
echo "   ./start.sh"
echo ""
echo "3. 或启动生产服务器："
echo "   ./start_production.sh"
echo ""
echo "4. 配置为系统服务（可选）："
echo "   sudo cp financial-daily.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable financial-daily"
echo "   sudo systemctl start financial-daily"
echo ""
echo "============================================================"
