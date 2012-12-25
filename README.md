logpress-tornado
================

使用tornado,jinja2,peewee开发的基于markdown写作的博客

1. **创建数据库**

    ```
    python manager.py --cmd=syncdb
    ```
    
    默认采用Sqlite3数据库，如需使用mysql 请修改config.py
    
    DB_ENGINE = 'peewee.SqliteDatabase' 
    
    修改成
    
    DB_ENGINE = 'peewee.MySQLDatabase'
    
2. **创建用户**

    ```
    python manager.py --cmd=createuser
    ```
    
3. **运行**

    ```
    python manager.py
    ```
    
    ***指定端口***
    
    ```
    python manager.py --port=8080
    ```
    
4. **配置**

