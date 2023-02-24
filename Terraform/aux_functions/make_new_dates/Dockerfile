FROM public.ecr.aws/lambda/python:3.9

COPY make_new_dates.py ${LAMBDA_TASK_ROOT}

CMD [ "make_new_dates.lambda_handler" ]