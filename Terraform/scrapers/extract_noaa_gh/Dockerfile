FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY extract_noaa_gh.py ${LAMBDA_TASK_ROOT}

CMD [ "extract_noaa_gh.lambda_handler" ]