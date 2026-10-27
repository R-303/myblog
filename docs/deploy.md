#部署手册

## 目标架构

浏览器 -> Nginx -> Gunicorn/Django -> SQLite+media

## 服务器要求

- Ubuntu 22.04 或 24.04
- 2GB 内存左右
- 开放 22、80、443 端口
- 先用服务器 IP 访问，域名以后再加

## 服务器目录

```text
/srv/myblog/
├── data/          # SQLite
├── media/         # 上传图片
├── staticfiles/   # collectstatic
├── .env
└── 项目代码
```

## 首次部署

1. 安装Docker 和 Docker Compose
2. 克隆 Github 仓库到 `/srv/myblog`;
3. 复制环境变量

```bash
cp .env.production.example .env
nano .env
```

4. 创建持久化目录：

```bash
mkdir -p data media staticfiles
```

5. 构建并启动：

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8000/healthz/
```

## 配置 Nginx

```bash
sudo cp deploy/nginx/myblog.conf /etc/nginx/sites-available/myblog
sudo ln -s /etc/nginx/sites-available/myblog /etc/nginx/sites-enabled/myblog
sudo nginx -t
sudo systemctl reload nginx
```

## 验证

- `http://服务器IP/` 能打开首页；
- `http://服务器IP/healthz/` 返回 `{"status": "ok"}`；
- 后台上传图片，前台详情页能显示；
- 容器重启后文章和图片仍然存在。


## 更新代码

```bash
git pull
docker compose up -d --build
```

## 备份

至少备份：

- `data/db.sqlite3`
- `media/`

## HTTPS

有域名后：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名
```

然后把 `.env` 中：

```env
DJANGO_SECURE_SSL_REDIRECT=true
```

并重启：

```bash
docker compose up -d
```