FROM python:3.10-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./.env /code/.env
COPY ./utils /code/utils
COPY ./core /code/core
COPY ./guard_rails_as_service.py /code/guard_rails_as_service.py

CMD ["python", "guard_rails_as_service.py"]