FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /config
RUN mkdir /appcinema
WORKDIR /appcinema
ADD /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt
ADD appcinema/ /appcinema/
WORKDIR /appcinema/appcinema
CMD python3 manage.py migrate --noinput && python3 manage.py loaddata fixture.json && gunicorn appcinema.wsgi -b 0.0.0.0:8000