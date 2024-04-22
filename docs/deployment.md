## 后端部署使用

Python版本 >= 3.10 !!! 

这是一个`Fastapi`后端项目，使用的工具链：

### **1.FastAPI**

- **作用**: FastAPI 是一个现代、快速的Web框架，专为构建API而设计，强调速度和易用性，同时自动提供数据验证和交互式文档。
- **用途**: 在本项目中，FastAPI 用于构建和维护所有后端API服务，提供数据处理和业务逻辑的实现。

### 2. **Uvicorn**

- **作用**: Uvicorn 是一个轻量级的 ASGI 兼容的 Web 服务器，它能够运行异步Python Web代码，提供出色的并发支持。
- **用途**: 本项目使用 Uvicorn 作为 FastAPI 框架的 Web 服务器，负责处理入站的 HTTP 请求。

### 3. **Systemd**

- **作用**: Systemd 是一个广泛使用的 Linux 初始化系统和服务管理器，它允许你配置和管理系统服务。
- **用途**: 在本项目中，Systemd 用于管理 Uvicorn 服务的启动、停止、重启以及在系统重启后自动启动。

### 4. **Nginx**

- **作用**: Nginx 是一个高性能的 Web 和反向代理服务器，它处理静态内容、负载均衡和HTTP缓存的效率非常高。
- **用途**: 本项目中，Nginx 用作反向代理服务器，增加了缓存处理，负载均衡，并且处理来自 Internet 的 HTTPS 请求，提高安全性和性能。

### 5. **Certbot**

- **作用**: Certbot 是一个自动化的工具，用于获取和更新 Let's Encrypt 提供的 SSL/TLS 证书，简化了 HTTPS 的实现过程。
- **用途**: 本项目利用 Certbot 自动为 Nginx 配置的 HTTPS 服务获取和维护 SSL/TLS 证书，确保通信的加密和安全。

## 部署流程

### 步骤 1: 准备应用环境

1. **安装并设置 FastAPI 应用**： 确保你的 FastAPI 应用已经安装在 `/home/ubuntu/paradigm-reboot-prober-backend` 目录中，并且所有依赖都已通过 `pip` 安装在该目录下的虚拟环境中。
2. **虚拟环境**： 应用应该在一个 Python 虚拟环境中运行。这个虚拟环境通常位于应用目录内，例如 `/home/ubuntu/paradigm-reboot-prober-backend/venv`。

然后进入虚拟环境：

```apl
source venv/bin/activate
```

安装依赖：

```apl
pip install -r requirements.txt
```

手动启动项目：

```apl
uvicorn backend.main:app --port 8000 --log-level debug
```

### 步骤 2: 配置 systemd 服务文件

1. **基本配置**：
	- `Description`：简要描述服务。
	- `After`：指定服务启动依赖，`network.target` 表示在网络服务启动后启动此服务。
2. **服务运行参数**：
	- `User` 和 `Group`：指定运行服务的用户和用户组。
	- `WorkingDirectory`：设置服务的工作目录。
	- `ExecStart`：定义启动服务的命令，包括 Uvicorn 的路径、模块和应用名称，端口和日志级别。
	- `Restart`：出错时自动重启服务。
	- `KillSignal`：指定终止服务的信号。
	- `TimeoutStopSec`：服务停止超时时间。
	- `PrivateTmp`：为服务提供独立的临时空间。
3. **环境变量**：
	- `Environment`：定义必要的环境变量，如数据库 URL 和安全密钥。

配置文件：

```ini
[Unit]
Description=Uvicorn Server for FastAPI
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/paradigm-reboot-prober-backend  
ExecStart=/home/ubuntu/paradigm-reboot-prober-backend/venv/bin/uvicorn backend.main:app --port 8000 --log-level debug
Restart=always
KillSignal=SIGTERM
TimeoutStopSec=5
PrivateTmp=true
Environment="PRP_DATABASE_URL=postgresql://<Username>:<Password>@<Host>/<DB>"
Environment="PRP_SECRETE_KEY=xxxx"   // 一个hex32的key, 具体内容请进入Server查看

[Install]
WantedBy=multi-user.target
```

首先创建配置文件：

```apl
sudo nano /etc/systemd/system/uvicorn.service
```

然后填入上述内容，Ctrl+O保存，Ctrl+X退出。其中，`SECRETE_KEY`可以使用`SSL`生成：

```apl
openssl rand -hex 32
```

### 步骤 3: 使用Nginx和Cerbot建立Https服务

**安装Nginx**

```apl
sudo apt update
sudo apt install nginx
nginx -v					//检查 Nginx 是否已安装
sudo systemctl status nginx // 检查 Nginx 是否在运行
```

**安装必要的软件包**

Certbot 依赖一些软件包，需要确保这些包在系统中可用。

```apl
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo apt-get update
```

这些工具将帮助自动化从 Let’s Encrypt 获取证书并配置 Nginx。

```apl
sudo apt-get install certbot python3-certbot-nginx
```

**使用 Certbot 配置 SSL 证书**

Certbot 会修改 Nginx 配置以安全地提供 HTTPS 服务。这个过程包括生成新的 SSL 证书并更新 Nginx 配置以使用这些证书。

```apl
sudo certbot --nginx
```

在运行过程中，Certbot 会提示你选择一个或多个域名，为其配置证书。它还可能询问是否重定向 HTTP 流量到 HTTPS，这是推荐的做法。

**设置证书自动续期**

SSL 证书有有效期，通常是 90 天。Certbot 提供了自动续期的功能。

```apl
sudo certbot renew --dry-run
```

这个命令会测试自动续期过程，以确保在证书到期前自动更新。

**测试 SSL 证书安装**

```apl
openssl s_client -connect api.prp.icel.site:443 -servername api.prp.icel.site
```

这条命令会显示 SSL 握手的详细信息，包括证书链和任何错误。

**Nginx 配置为使用 SSL/TLS 证书**

为 Nginx 配置了 SSL/TLS 支持。

```js
server {
    listen 443 ssl;
    server_name api.prp.icel.site;
    ssl_certificate /etc/letsencrypt/live/api.prp.icel.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.prp.icel.site/privkey.pem;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

`listen 443 ssl;`: 监听 443 端口，启用 SSL。

`ssl_certificate` 和 `ssl_certificate_key`: 指定 Let's Encrypt 提供的 SSL 证书和密钥文件的路径。

`proxy_pass http://localhost:8000;`: 将所有传入请求代理到本地的 8000 端口，即 Uvicorn 服务器。

`proxy_set_header`: 设置一些重要的 HTTP 头部，确保正确的客户端信息被传递给后端应用。

通常，Nginx 默认配置文件会在 `/etc/nginx/sites-enabled/default` 中，可能会与你的自定义配置冲突。禁用默认配置的方法如下：

- **创建配置文件**

```apl
sudo nano /etc/nginx/sites-available/api.prp.icel.site
```

- **启用配置**

```apl
sudo ln -s /etc/nginx/sites-available/api.prp.icel.site /etc/nginx/sites-enabled/
```

- **移除默认站点的链接**

```apl
sudo rm /etc/nginx/sites-enabled/default
```

- **检查 Nginx 配置语法**

```apl
sudo nginx -t
```

- **重载 Nginx**

```apl
sudo systemctl reload nginx
```

如果一切顺利，项目将能够在HTTPS下访问。

### 步骤 4: 启动和管理服务

**启动服务**：

```apl
sudo systemctl start uvicorn.server
```

**启用服务自启**： 使服务在系统启动时自动启动。

```apl
sudo systemctl enable uvicorn.server
```

**检查服务状态**： 确保服务正在运行。

```apl
sudo systemctl status uvicorn.server
```

**查看服务日志**： 查看服务的详细运行日志，以便于调试和监控。

```apl
sudo journalctl -u uvicorn.server
```

**重新启动**`Uvicorn`服务，输入以下命令：

```apl
sudo systemctl daemon-reload
sudo systemctl restart uvicorn.service
```

### 步骤 5: 维护和更新

本后端使用`Github Workflow`来进行自动化部署，在repo的`Secrets`加入以下三个变量：

```apl
secrets.SERVER_IP			// 服务器IP
secrets.SERVER_USER			// 服务器用户名
secrets.SSH_PRIVATE_KEY		// RSA私钥
```

然后使用以下工作流，添加至项目目录下`/.github/workflow/`：

```yml
name: CI/CD Pipeline for FastAPI

on:
  push:
    branches:
      - master

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: SSH and Deploy
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_IP }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /home/ubuntu/paradigm-reboot-prober-backend 
          git reset --hard
          git clean -fd
          git fetch
          git pull
          source venv/bin/activate
          pip install -r requirements.txt
          sudo systemctl daemon-reload
          sudo systemctl restart uvicorn.service
          sudo systemctl status uvicorn.service
```

之后，任何**push到master分支**的行为都将使得服务器进行自我更新，无需手动上传。

------