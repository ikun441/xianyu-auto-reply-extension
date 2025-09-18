# 本文档给出你可能需要用到的参数，[参考文档](https://cloudrevev4.apifox.cn/create-share-link-306853462e0)
## 必填参数
### 请求头
- `Authorization`：（**必填**）字符串，即请求头参数，内容为xy的api请求头参数，在项目运行后，将会自动生成这个参数,此项请不要轻易修改，在config.yaml中，你可以看到它的值，请不要轻易泄露此项的值。
- `Content-Type`：字符串，即请求头参数，内容为`application/json`
### 请求体
- `payload`：json格式的字符串，即请求参数
```python
payload = json.dumps({
   "permissions": {
      "anonymous": "BQ==",
      "everyone": "AQ=="
   },
   "uri": "your_cloudreve_file_uri", #必填，格式为cloudreve://my/Inspirations
   "downloadS": 1, # 选填，即下载多少次后过期，填写为0则不限制下载次数
   "expire": 86400 , #选填,单位为秒,填写为0则代表不限制过期时间
   "is_private": True, # 选填，是否随机生成密码
})
```