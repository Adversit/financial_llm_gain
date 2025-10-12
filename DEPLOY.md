# Ubuntu 部署指南

本文档介绍如何在 Ubuntu 服务器上部署金融日报系统。

## 快速开始

### 1. 首次安装

```bash
# 克隆或上传项目到服务器
cd /opt
sudo git clone <your-repo-url> financial-daily-system
# 或使用 scp 上传项目文件

# 进入项目目录
cd financial-daily-system

# 运行安装脚本
bash install.sh
```

### 2. 配置系统

编辑 `.env` 文件，填入必要的配置：

```bash
nano .env
```

必须配置的项目：
- `AI_API_KEY`: AI 服务的 API 密钥
- `SMTP_USERNAME`: 邮件发送账号
- `SMTP_PASSWORD`: 邮件密码或授权码

### 3. 启动服务

#### 开发模式（带自动重载）

```bash
./start.sh
```

#### 生产模式（使用 gunicorn）

```bash
./start_production.sh
```

#### 后台运行（使用 nohup）

```bash
nohup ./start_production.sh > logs/nohup.log 2>&1 &
```

## 系统服务配置

将应用配置为 systemd 服务，实现开机自启和自动重启。

### 1. 修改服务文件

编辑 `financial-daily.service`，修改以下内容：

```ini
# 修改用户和组（建议使用非 root 用户）
User=your-username
Group=your-username

# 修改工作目录为实际路径
WorkingDirectory=/path/to/your/financial-daily-system
Environment="PATH=/path/to/your/financial-daily-system/venv/bin"
ExecStart=/path/to/your/financial-daily-system/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 9998

# 修改日志路径
StandardOutput=append:/path/to/your/financial-daily-system/logs/service.log
StandardError=append:/path/to/your/financial-daily-system/logs/service_error.log
ReadWritePaths=/path/to/your/financial-daily-system/data /path/to/your/financial-daily-system/logs
```

### 2. 安装服务

```bash
# 复制服务文件
sudo cp financial-daily.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable financial-daily

# 启动服务
sudo systemctl start financial-daily

# 查看服务状态
sudo systemctl status financial-daily
```

### 3. 服务管理命令

```bash
# 启动服务
sudo systemctl start financial-daily

# 停止服务
sudo systemctl stop financial-daily

# 重启服务
sudo systemctl restart financial-daily

# 查看日志
sudo journalctl -u financial-daily -f

# 查看最近 100 行日志
sudo journalctl -u financial-daily -n 100
```

## Nginx 反向代理配置

如果需要通过域名访问或使用 HTTPS，可以配置 Nginx 反向代理。

### 1. 安装 Nginx

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### 2. 创建 Nginx 配置

创建文件 `/etc/nginx/sites-available/financial-daily`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:9998;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /opt/financial-daily-system/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/financial-daily /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 4. 配置 HTTPS（可选）

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书并自动配置
sudo certbot --nginx -d your-domain.com

# 证书会自动续期，可以测试续期
sudo certbot renew --dry-run
```

## 防火墙配置

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 如果直接访问应用端口
sudo ufw allow 9998/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

## 性能优化

### 1. 使用 Gunicorn 多进程

编辑 `start_production.sh`，调整 worker 数量：

```bash
# 推荐 worker 数量 = (CPU 核心数 * 2) + 1
WORKERS=5  # 例如 2 核 CPU
```

### 2. 数据库优化

如果数据量大，考虑迁移到 PostgreSQL：

```bash
# 安装 PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# 修改 .env 中的 DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost/financial_daily
```

### 3. 日志轮转

创建 `/etc/logrotate.d/financial-daily`：

```
/opt/financial-daily-system/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload financial-daily > /dev/null 2>&1 || true
    endscript
}
```

## 监控和维护

### 1. 查看应用日志

```bash
# 实时查看日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看服务日志
sudo journalctl -u financial-daily -f
```

### 2. 数据库备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/financial-daily"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp data/financial_daily.db $BACKUP_DIR/financial_daily_$DATE.db
# 保留最近 30 天的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
EOF

chmod +x backup.sh

# 添加到 crontab（每天凌晨 2 点备份）
crontab -e
# 添加: 0 2 * * * /opt/financial-daily-system/backup.sh
```

### 3. 健康检查

```bash
# 检查服务是否运行
curl http://localhost:9998/health

# 检查调度器状态
curl http://localhost:9998/scheduler/status
```

## 故障排查

### 服务无法启动

```bash
# 查看详细错误信息
sudo journalctl -u financial-daily -n 50

# 检查端口是否被占用
sudo netstat -tlnp | grep 9998

# 检查配置文件
python -c "from app.config import get_config; print(get_config())"
```

### 数据库问题

```bash
# 检查数据库文件权限
ls -la data/financial_daily.db

# 重新初始化数据库
rm data/financial_daily.db
python -c "from app.database import init_db; init_db()"
```

### 内存不足

```bash
# 查看内存使用
free -h

# 减少 worker 数量
# 编辑 start_production.sh，设置 WORKERS=2
```

## 更新部署

```bash
# 停止服务
sudo systemctl stop financial-daily

# 拉取最新代码
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start financial-daily
```

## 安全建议

1. **不要使用 root 用户运行服务**
2. **定期更新系统和依赖包**
3. **使用强密码和密钥**
4. **启用防火墙，只开放必要端口**
5. **定期备份数据库**
6. **使用 HTTPS 加密传输**
7. **限制 API 访问频率**
8. **定期查看日志，监控异常**

## 技术支持

如有问题，请查看：
- 应用日志: `logs/app.log`
- 系统日志: `sudo journalctl -u financial-daily`
- API 文档: `http://your-server:9998/docs`
