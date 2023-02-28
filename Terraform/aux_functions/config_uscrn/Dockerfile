FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY config_uscrn.py ${LAMBDA_TASK_ROOT}

CMD [ "config_uscrn.lambda_handler" ]