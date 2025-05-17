FROM public.ecr.aws/lambda/python:3.9

# Copia tu código y modelo
COPY app/ ${LAMBDA_TASK_ROOT}

# Instala las dependencias
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Define el entrypoint de Lambda
CMD ["lambda_function.lambda_handler"]
