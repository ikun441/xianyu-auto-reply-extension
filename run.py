from utils.utils import *
import fastapi
import uvicorn
import json
from log.log import Log
import http.client

# 确保yaml模块正确导入
yaml = __import__('yaml')

log = Log(__name__)
app = fastapi.FastAPI()

# 全局配置和用户对象
config = None
user = None
headers = None

@app.on_event("startup")
async def startup_event():
    """应用启动时执行登录操作"""
    global config, user, headers
    try:
        # 加载配置
        log.info("开始加载配置文件...")
        config = Config("config.yaml")
        log.info("配置文件加载成功")
        
        # 获取Cloudreve配置
        cloudreve_config = config.get("cloudreve")
        if not cloudreve_config:
            log.error("配置文件中未找到cloudreve配置")
            return
        
        # 获取配置信息
        name = cloudreve_config.get("name")
        password = cloudreve_config.get("password")
        url = cloudreve_config.get("url")
        
        if not name or not password or not url:
            log.error("Cloudreve配置不完整，请检查name、password和url")
            return
        
        log.info(f"Cloudreve配置信息 - URL: {url}, 用户名: {name}")
        
        # 移除URL中的协议头
        url_without_protocol = url.replace("https://", "").replace("http://", "")
        log.info(f"处理后的URL: {url_without_protocol}")
        
        # 创建用户对象并登录
        user = User(
            name=name,
            password=password,
            url=url_without_protocol
        )
        
        # 获取认证头
        log.info(f"正在尝试登陆，用户名：{name}")
        # 解析token并设置请求头
        try:
            log.info("开始获取认证token...")
            token = user.get_header()
            
            # 详细记录token获取结果
            if token:
                log.info(f"成功获取到token，长度: {len(token)} 字符")
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                log.info("登录成功，已获取认证token和设置请求头")
                log.info(f'获取到的headers为:{headers},正在准备写入config.yaml')
                # 写入config.yaml
                config.set("auth", headers)
                config.save()
                log.info(f'headers已成功写入config.yaml')
            else:
                log.error("登录失败，未获取到token")
        except json.JSONDecodeError as e:
            log.error(f"解析登录结果失败: {str(e)}")
        except Exception as inner_e:
            log.error(f"获取token过程中发生异常: {str(inner_e)}")
    except Exception as e:
        log.error(f"启动时发生错误: {str(e)}")

@app.get("/get_share_link")
async def get_share_link(file_uri: str, download_limit: int = 1, expire_seconds: int = 86400, is_private: bool = True):
    """
    获取文件的动态分享链接
    
    参数:
    - file_uri: 云盘文件URI，格式为cloudreve://my/文件路径
    - download_limit: 下载次数限制，默认为1次
    - expire_seconds: 过期时间（秒），默认为86400秒（1天）
    - is_private: 是否生成随机密码，默认为True
    
    返回:
    - 分享链接信息或错误消息
    """
    global headers, user, config
    
    # 检查是否已登录
    if not headers:
        log.error("未登录，请检查配置和登录状态")
        return {"code": 401, "message": "未登录，请检查配置和登录状态"}
    
    # 验证参数
    if not file_uri.startswith("cloudreve://"):
        log.error(f"无效的文件URI格式: {file_uri}")
        return {"code": 400, "message": "无效的文件URI格式，必须以cloudreve://开头"}
    
    try:
        # 构造请求体
        payload = json.dumps({
            "permissions": {
                "anonymous": "BQ==",
                "everyone": "AQ=="
            },
            "uri": file_uri,
            "downloads": download_limit,
            "expire": expire_seconds,
            "is_private": is_private
        })
        
        # 获取Cloudreve URL
        cloudreve_url = config.get("cloudreve").get("url").replace("https://", "").replace("http://", "").replace("/", "")
        log.info(f"处理后的URL: {cloudreve_url}")
        
        # 创建分享链接
        conn = http.client.HTTPSConnection(cloudreve_url)
        conn.request("PUT", "/api/v4/share", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        
        log.info(f"创建分享链接响应: {data}")
        
        # 解析响应
        result = json.loads(data)
        if result.get("code") == 0:
            share_data = result.get("data", {})
            
            # 检查share_data的类型，如果是字符串直接使用它作为完整链接
            if isinstance(share_data, str):
                return {
                    "code": 0,
                    "message": "success",
                    "data": {
                        "share_url": share_data,
                        "share_id": "",  # 无法从字符串中提取share_id
                        "password": "",
                        "expire": expire_seconds,
                        "download_count": 0,
                        "download_limit": download_limit
                    }
                }
            else:
                # 原始逻辑：当share_data是对象时
                share_url = f"{config.get('cloudreve').get('url')}/s/{share_data.get('share_id')}"
                return {
                    "code": 0,
                    "message": "success",
                    "data": {
                        "share_url": share_url,
                        "share_id": share_data.get("share_id"),
                        "password": share_data.get("password"),
                        "expire": share_data.get("expire"),
                        "download_count": share_data.get("downloads"),
                        "download_limit": download_limit
                    }
                }
        else:
            log.error(f"创建分享链接失败: {result.get('message')}")
            return {"code": result.get("code"), "message": result.get("message")}
            
    except Exception as e:
        log.error(f"创建分享链接时发生错误: {str(e)}")
        return {"code": 500, "message": f"服务器内部错误: {str(e)}"}

@app.get("/")
async def root():
    """根路径，用于检查服务是否运行"""
    global headers
    status = "running"
    if not headers:
        status = "running (未登录)"
    return {"status": status, "message": "服务运行中，请使用/get_share_link接口获取分享链接"}

if __name__ == "__main__":
    # 从配置文件读取服务器设置
    config = Config("config.yaml")
    server_config = config.get("server")
    host = server_config.get("host", "localhost")
    port = server_config.get("port", 9191)
    
    log.info(f"启动服务，监听地址: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

