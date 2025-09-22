import http.client
import json
import yaml


class Config:
    def __init__(self,config_path):
        self.config_path = config_path  # 保存配置文件路径
        with open(config_path,'r',encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    def get(self,key):
        return self.config.get(key)
    def update(self,key,value):
        self.config[key] = value
        with open(self.config_path,'w',encoding='utf-8') as f:  # 使用保存的配置文件路径
            yaml.dump(self.config,f,encoding='utf-8',allow_unicode=True)
    def save(self):
        with open(self.config_path,'w',encoding='utf-8') as f:
            yaml.dump(self.config,f,encoding='utf-8',allow_unicode=True)
    def set(self,key,value):
        self.config[key] = value
        self.save()

class User:
    def __init__(self,name,password,url):
        self.name = name
        self.password = password
        self.url = url
    def login(self):
        try:
            conn = http.client.HTTPSConnection(self.url)
            payload = json.dumps({
                "email": self.name,
                "password": self.password
            })
            headers = {
                'Content-Type': 'application/json'
            }
            conn.request("POST", "/api/v4/session/token", payload, headers)
            res = conn.getresponse()
            
            # 检查HTTP状态码
            if res.status != 200:
                print(f"登录请求失败，状态码: {res.status}, 原因: {res.reason}")
                return "{}"  # 返回空JSON对象
            
            data = res.read()
            
            # 检查响应是否为空
            if not data:
                print("登录响应为空")
                return "{}"
            
            return data.decode("utf-8")
        except Exception as e:
            print(f"登录过程中发生错误: {str(e)}")
            return "{}"
    def get_token(self):
        try:
            data = self.login()
            
            # 确保数据不为空
            if not data or data.isspace():
                print("登录数据为空")
                return None
            
            # 修复嵌套键访问方式
            try:
                login_data = json.loads(data)
                token = login_data.get('data', {}).get('token', {}).get('access_token')
                return token
            except json.JSONDecodeError as e:
                print(f"解析登录数据失败: {str(e)}, 数据内容: {data}")
                return None
        except Exception as e:
            print(f"获取token过程中发生错误: {str(e)}")
            return None
    def get_header(self):
        try:
            token = self.get_token()
            # 直接返回token字符串，而不是字典
            return token
        except Exception as e:
            print(f"获取请求头过程中发生错误: {str(e)}")
            return None

class NetManager:
    def __init__(self,payload,headers,url):  # 添加url参数
        self.payload = payload
        self.headers = headers
        self.url = url  # 初始化url属性
    def create_url(self):
        conn = http.client.HTTPSConnection(self.url)
        conn.request("PUT", "/api/v4/share", self.payload, self.headers)
        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8")
    def get_url(self):
        data = self.create_url()
        url = json.loads(data).get('data')
        return url
