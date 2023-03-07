FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY extract_grid_load.py ${LAMBDA_TASK_ROOT}

CMD [ "extract_grid_load.lambda_handler" ]