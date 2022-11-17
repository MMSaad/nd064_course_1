# Set base image
FROM python:3.8
COPY . /app/
WORKDIR /app
RUN python init_db.py
RUN pip install -r requirements.txt
EXPOSE 3111
CMD ["python","app.py"]