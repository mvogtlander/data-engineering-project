FROM apache/spark:4.0.3-scala2.13-java17-python3-r-ubuntu

USER root
RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv pip install --system --no-cache -e .

COPY . .

EXPOSE 8888

CMD ["jupyter", "notebook", "--no-browser", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--notebook-dir=/app"]