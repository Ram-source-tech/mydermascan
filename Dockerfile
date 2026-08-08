FROM tensorflow/tensorflow:2.21.0

WORKDIR /app

# Install Python dependencies (tensorflow is already provided by the base image)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (ensure the model file under models/ is included in build context)
COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["python", "app.py"]
