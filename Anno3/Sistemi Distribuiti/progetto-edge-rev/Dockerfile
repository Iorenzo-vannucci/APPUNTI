FROM python:3.10

#utente no privilegi
RUN useradd -m stupid_user 
WORKDIR /app
USER stupid_user
CMD ["python", "-u", "task.py"]