# Database-keepalive
各类数据保活

为了安全起见，不要将数据库密码直接写在代码里。请在 GitHub 仓库的 Settings -> Secrets and variables -> Actions 中添加以下 Repository Secrets：
Secret Name,示例格式,说明
MONGO_URI,mongodb+srv://user:pass@cluster.xxx.mongodb.net/,MongoDB 连接字符串
REDIS_HOST,redis-12345.c1.region.cloud.redislabs.com,Redis 地址
REDIS_PORT,12345,Redis 端口
REDIS_PASSWORD,your_redis_password,Redis 密码
REDIS_USERNAME,Redis 用户名	如果是默认用户通常是 default，或者是云厂商分配的特定用户名
PG_DSN,postgres://user:pass@host:5432/dbname,Postgres 连接串
