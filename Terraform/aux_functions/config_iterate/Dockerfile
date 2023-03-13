FROM public.ecr.aws/lambda/python:3.9

COPY config_iterate.py ${LAMBDA_TASK_ROOT}

CMD [ "config_iterate.lambda_handler" ]