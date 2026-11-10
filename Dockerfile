FROM python:3.12-slim
WORKDIR /sandbox
RUN pip install --no-cache-dir pandas numpy
RUN useradd --create-home --shell /usr/sbin/nologin sandboxuser
USER sandboxuser
CMD ["python", "--version"]