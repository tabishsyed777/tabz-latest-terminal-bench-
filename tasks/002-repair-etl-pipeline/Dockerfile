FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . /workspace
ENV PYTHONPATH=/workspace/src

RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash"]
