from pymongo import MongoClient
import config

from utils import initial_logger

class NewMongoDB:
    def __init__(self, log_name):
        self.logger = initial_logger('main.database.mongoDB', log_name)
        self.logger.info('initialize mongoDB...')
        # 根据环境不同切换主机地址
        host = config.DEV_HOST if config.settings.MODE == 'DEV' else config.PRD_HOST
        self.logger.info('Connecting to ' + host + ':' + str(config.PORT))
        self.client = MongoClient(config.DEV_HOST, config.PORT)
        self.logger.info('Connect successfully')
        self.db = self.client[config.DATABASE]

    def changeDB(self, database):
        self.db = self.client[database]

    def insert(self, doc, collection=config.COLLECTION):
        col = self.db[collection]
        if isinstance(doc, list):
            insert_result = col.insert_many(doc)
        else:
            insert_result = col.insert_one(doc)

        self.logger.info(f'{insert_result}')
        return insert_result