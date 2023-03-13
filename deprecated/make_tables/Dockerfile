FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

COPY make_tables.json .

COPY points_of_interest.json .

COPY table_structure.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY make_tables.py ${LAMBDA_TASK_ROOT}

CMD [ "make_tables.lambda_handler" ]