FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY extract_pirate_historic.py ${LAMBDA_TASK_ROOT}

CMD [ "extract_pirate_historic.lambda_handler" ]