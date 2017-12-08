FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /appcinema
WORKDIR /appcinema
ADD requirements.txt /appcinema/
RUN pip install -r requirements.txt
ADD appcinema/ /appcinema/
WORKDIR /appcinema/appcinema
