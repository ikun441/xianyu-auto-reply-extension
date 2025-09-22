**生如夏花，死如秋叶。 ---泰戈尔**
# xianyu-auto-reply扩展
## 项目介绍 
- 在使用[xianyu-auto-reply](https://github.com/zhinianboke/xianyu-auto-reply)（简称：“xy”）的过程中，我同时部署了cloudreve的服务，但也察觉到了xianyu-auto-reply对于api仅支持静态的请求，所以本项目将会为它添加额外的能力，通过本项目，你将能通过静态的api请求，获取临时性的可以被任意指定参数的分享链接。
- 本项目为xy和cloudreve之间提供了一个第三方的本地中转服务器，所以不会产生任何隐私问题（除非您尝试将其暴露在公网中）
- 我们建议您关闭cloudreve的验证码和其他如2FA等的验证方式，便于登陆，且开放直链获取和关闭用户注册功能。

## 快速开始
### 拉取项目
```bash
# 克隆项目（请替换为实际的仓库地址）
git clone https://github.com/ikun441y/xianyu-auto-reply-extension.git
cd xianyu-auto-reply-extension
```

### 安装依赖(以conda为例)
```bash
conda create -n xy-extension python=3.9
conda activate xy-extension
pip install -r requirements.txt
```

### 配置
请根据您的实际情况，修改`config.yaml`文件中的配置项：
```yaml
server:
  host: localhost  # 服务器监听地址
  port: 9191  # 服务器监听端口
auth: jwt_token
cloudreve:
  name: your_own_email_name  # Cloudreve账号邮箱
  password: your_own_password  # Cloudreve账号密码
  url: https://your_cloudreve_url  # Cloudreve服务地址
```

### 运行
#### 直接运行
```bash
python run.py
```

#### 使用Docker运行
```bash
# 构建Docker镜像
docker build -t xy-extension .

# 运行Docker容器
docker run -d -p 9191:9191 --name xy-extension xy-extension
```

## API接口说明
### 根路径
- **地址**: `/`
- **方法**: GET
- **作用**: 检查服务是否正常运行
- **返回示例**: 
  ```json
  {
    "status": "running", 
    "message": "服务运行中，请使用/get_share_link接口获取分享链接"
  }
  ```

### 获取分享链接接口
- **地址**: `/get_share_link`
- **方法**: GET
- **作用**: 通过静态文件地址获取动态的分享链接
- **参数说明**: 
  - `file_uri` (必填): 云盘文件URI，格式为`cloudreve://my/文件路径`
  - `download_limit` (选填): 下载次数限制，默认为1次（下载后链接失效）
  - `expire_seconds` (选填): 过期时间（秒），默认为86400秒（1天）
  - `is_private` (选填): 是否生成随机密码，默认为True
- **返回示例**: 
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {
      "share_url": "https://your_cloudreve_url/s/abcd1234",
      "share_id": "abcd1234",
      "password": "5678",
      "expire": 86400,
      "download_count": 0,
      "download_limit": 1
    }
  }
  ```

## 测试脚本使用
项目包含了一个api.md文档，你可以在[此处](api.md)查看需要填写的headers和payload规范。

## xianyu-auto-reply API参数设置
在xianyu-auto-reply中配置API参数：
- **API地址**: `http://localhost:9191/get_share_link` (请将localhost替换为实际运行地址)
- **请求方法**: GET
- **参数**: 
  - `file_uri`: 您要分享的文件URI
  - 其他可选参数可根据需要添加

## 注意事项
1. 确保config.yaml中的Cloudreve账号信息正确，并且已经关闭了验证码和2FA验证
2. 本服务默认仅监听本地地址，如需外部访问，请修改config.yaml中的host为0.0.0.0
3. 在生产环境中，请考虑使用反向代理如Nginx来提供更好的安全性和性能
4. 如果遇到登录问题，请检查Cloudreve服务是否正常运行，以及账号信息是否正确





