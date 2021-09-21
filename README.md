# py_splendor
python实现桌游璀璨宝石
* backend: fast-api + uvicorn + websocket
* orm: SQLAlchemy
* database: mysql

***

# param
## 后端启动时
* LOGURU_LEVEL: loguru日志等级, 默认"INFO"
* MYSQL_CONN_URL: 后端数据库连接"mysql+pymysql://<user>:<pwd>@<host>:<port>"
* MYSQL_DATABASE: 后端数据库名称"<database_name>"

## 游戏时
游戏中所以流程都通过websocket传参控制, 参数为json类型

分为三部分: chat(聊天), system(系统), game(游戏)
### chat
控制房间中的聊天信息, 例:
```json
{
  "chat": 1,
  "say": "hello py_splendor"
}
```
### system
控制游戏开始, 例:
```json
{
  "system": 1,
  "instruct": "start"
}
```
### game
控制游戏实际操作, 例:
```json
{
  "game": 1,
  "instruct": "take_coin",
  "coin_color_list": [
    "红色",
    "黑色",
    "白色"
  ]
}
```

***

# run
## local
python版本3.7.4

```bash
python application/app.py
```

## docker
```bash
docker run -itd -p 9999:9999 samael0119/py_splendor:0.0.1
```
