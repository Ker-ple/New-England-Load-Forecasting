FROM public.ecr.aws/lambda/python:3.9

COPY config_pirate.py ${LAMBDA_TASK_ROOT}

CMD [ "config_pirate.lambda_handler" ]