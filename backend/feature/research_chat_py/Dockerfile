FROM public.ecr.aws/docker/library/python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir --target /deps -r requirements.txt

FROM public.ecr.aws/docker/library/python:3.12-slim
RUN pip install --no-cache-dir awslambdaric
COPY --from=builder /deps /opt/python
ENV PYTHONPATH=/opt/python:/app
COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "-m", "awslambdaric"]
CMD ["presentation.lambda_handlers.ws_send_message.handler.handler"]
