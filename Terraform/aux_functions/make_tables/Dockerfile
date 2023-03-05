FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY make_tables.py ${LAMBDA_TASK_ROOT}

CMD [ "make_tables.lambda_handler" ]