
# 第一个阶段：构建阶段
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app
COPY . /app
# 复制 requirements.txt 并运行 pip install 在单独的镜像层中
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["gunicorn",  "-c", "gu_docker.py", "main.wsgi:application"]
