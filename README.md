# Flask-VulnApp
Based on OWASP TOP 10, we build a web service that allows you to simulate and hack web applications.

## test user informaion
id : testtest  
pw : testtest

## DB

```shell
flask db init
flask db migrate
flask db upgrade
```
처음 실행 전에 db위 명령을 입력해서 DB를 생성하고, `__init__.py`에 다음 부분에 주석을 해제하고 실행합니다.
```python
    #from .init_data import insert_default_boards
    #with app.app_context():
    #    insert_default_boards()
```

## admin
```shell
flask admin create
```
위 명령어로 admin 계정을 생성할 수 있습니다.  
명령어 입력 시 password를 입력받습니다.  
admin 계정의 기본 username은 admin 입니다.  

```shell
flask admin delete
```
위 명령어로 admin 계정을 제거할 수 있습니다.