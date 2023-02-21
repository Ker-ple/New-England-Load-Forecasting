FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY extract_uscrn_data.py ${LAMBDA_TASK_ROOT}

COPY uscrn_utils.py ${LAMBDA_TASK_ROOT}

CMD [ "extract_uscrn_data.lambda_handler" ]