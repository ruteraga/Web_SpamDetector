FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip

# Force typing-extensions version first
RUN pip install typing-extensions==4.5.0

# Install TensorFlow and core deps with compatible numpy version
RUN pip install --no-cache-dir \
    tensorflow-cpu==2.15.0 \
    numpy==1.24.3 \
    pandas==2.1.3

# Install API deps
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    paho-mqtt==1.6.1 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    requests==2.31.0

# Install dashboard deps
RUN pip install --no-cache-dir \
    streamlit==1.28.1 \
    plotly==5.18.0

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]