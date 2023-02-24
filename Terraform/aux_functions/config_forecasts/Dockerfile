FROM public.ecr.aws/lambda/python:3.9

COPY config_forecasts.py ${LAMBDA_TASK_ROOT}

CMD [ "config_forecasts.lambda_handler" ]