# 개요
* 개발, 운영 설정을 .env파일로 분리

# 실행방법
* 개발
```shell
# 리눅스
uvicorn app.main:app --reload

```

* 운영
```shell
# 리눅스
MODE=prod uvicorn app.main:app --reload

```