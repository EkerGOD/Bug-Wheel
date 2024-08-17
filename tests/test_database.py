from database import MongoDB

def test_mongoDB():
    mongoDB = MongoDB()
    mongoDB.insert('crawl_data', {"title":"test", "content":"test content", "time": "2024/7/19"})
