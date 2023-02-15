FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY split_date_range.py ${LAMBDA_TASK_ROOT}

CMD [ "split_date_range.lambda_handler" ]