# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9

EXPOSE 8001

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY CPTSdal-1.0.1-py3-none-any.whl .
RUN pip install ./CPTSdal-1.0.1-py3-none-any.whl

WORKDIR /app
COPY . /app

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["uvicorn", "main:main", "--host", "0.0.0.0", "--port", "8001", "--timeout-keep-alive", "120", "--workers", "4"]