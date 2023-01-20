FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY extract.py ${LAMBDA_TASK_ROOT}

CMD [ "extract.lambda_handler" ]