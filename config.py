from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="settings.toml",
)
"""
数据库配置
"""
# 默认地址
PRD_HOST = "mongodb://43.139.177.84"
# 开发版本地址
DEV_HOST = "mongodb://localhost"


# 默认端口
PORT = 27017

# 默认数据库
DATABASE = "foodSafetyInfo"

# 默认数据集
COLLECTION = "crawl_data"

"""
文件路径配置
"""
# 历史记录文件
HISTORY_PATH = 'json/history.json'

# 站点数据文件
SITE_PATH = 'json/site.json'

"""
搬运工配置
"""
# 初始搬运工数量
PORTER_NUM = 5

# 等待队列超时时间
QUEUE_TIMEOUT = 10

"""
队列控制器配置
"""
# 队列控制器检测间隔
MONITOR_INTERNAL = 10
