logpress-tornado
================

使用[tornado][tornado],[jinja2][jinja2],[peewee][peewee]开发的基于markdown写作的博客 [站点][demo]

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

[tornado]:http://www.tornadoweb.org/
[jinja2]:http://jinja.pocoo.org/
[peewee]:http://peewee.readthedocs.org/en/latest/index.html
[demo]:http://blog.szgeist.com
