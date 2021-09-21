FROM python:3.7.4-slim

WORKDIR /app
COPY requirement.txt requirement.txt
RUN pip install -r requirement.txt -i https://pypi.doubanio.com/simple --no-cache

COPY . .

ENV TZ "Asia/Shanghai"
ENV LOGURU_LEVEL "INFO"
ENV MYSQL_CONN_URL "mysql+pymysql://root:123qwe@10.10.10.104:33060"
ENV MYSQL_DATABASE "py_splendor"
ENV PYTHONPATH "."

ENTRYPOINT ["python", "application/app.py"]