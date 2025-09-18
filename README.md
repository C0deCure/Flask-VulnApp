# Flask-VulnApp
Based on OWASP TOP 10, we build a web service that allows you to simulate and hack web applications.

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