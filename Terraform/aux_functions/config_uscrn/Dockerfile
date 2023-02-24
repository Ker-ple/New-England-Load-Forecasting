FROM public.ecr.aws/lambda/python:3.9

COPY config_uscrn.py ${LAMBDA_TASK_ROOT}

CMD [ "config_uscrn.lambda_handler" ]