## V1.0

- 完成爬虫基础架构

## V1.1

- 重建爬虫配置文件格式，可以适配更复杂的网站

## V2.0

- 重新构筑项目结构，之前是通过项目主线程调度各个爬虫线程，整个爬虫项目不由服务器系统控制。这样配置缺点在于只能在开始整个爬虫项目的控制台中控制该项目，一旦退出没有控制台就没有办法监控。
- 从textual制作的伪控制台输出执行状况，改变成用logging输出日志，这样更符合项目整体架构，且相较之前非常容易维护。
- 爬虫之后需要通过corn或者corntab进行调度，定时执行
- 可以通过任意打开的控制台访问指令来控制爬虫的执行

## V2.1

- 将项目轻量化，减少不必要的模块
- 生成部分控制台指令，可以通过控制台实现查询 修改部分配置文件的功能

## v2.2(ing)

- 适配更多网站