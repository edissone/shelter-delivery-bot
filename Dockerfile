FROM python:3.8-slim
WORKDIR bot-application
COPY requirements.txt /src ./src/
RUN pip install -r ./src/requirements.txt
COPY resources ./resources
COPY main.py .
RUN ls -la
CMD [ "python3", "./main.py" ]