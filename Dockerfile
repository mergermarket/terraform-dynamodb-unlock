FROM python:3.7-alpine
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
ADD unlock.py /unlock.py
ENTRYPOINT ["python", "-u", "/unlock.py"]
