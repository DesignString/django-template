FROM python:3.6.9
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /project_name
WORKDIR /project_name
RUN pip install pip -U
RUN pip install gunicorn
COPY requirements.txt /project_name/
RUN pip install -r requirements.txt
COPY . /project_name/
EXPOSE 8002
RUN python manage.py collectstatic --no-input --clear
