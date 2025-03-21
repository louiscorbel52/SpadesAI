FROM tensorflow/tensorflow:1.15.5-py3

EXPOSE 80

WORKDIR /code

COPY . .

# workaround to copy the root-config (optional, we want it for GA build.yml workflow)
# https://stackoverflow.com/a/46801962
# COPY .gitignore root-config* /root/

# RUN mkdir -p /root/.ssh && ssh-keyscan github.com >> /root/.ssh/known_hosts

# WORKDIR /code

RUN pip install --no-cache-dir --upgrade -r requirements.txt

HEALTHCHECK --interval=10s --timeout=5s --retries=3 CMD curl -f http://localhost/health || exit 1

CMD python -m uvicorn main:app --host=0.0.0.0 --port=80 --workers=4
