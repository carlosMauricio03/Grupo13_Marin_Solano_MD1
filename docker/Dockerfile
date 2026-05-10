FROM python:3.11-slim

WORKDIR /app

COPY requirements-notebook.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements-notebook.txt

COPY . .

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.allow_origin='*'"]
