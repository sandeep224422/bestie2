FROM python:3.10-slim

# Install dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ffmpeg gnupg ca-certificates \
 && curl -fsSL https://deb.nodesource.com/setup_19.x | bash - \
 && apt-get install -y nodejs \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . /app/
WORKDIR /app/

# Install Python deps
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Start command
CMD ["bash", "start"]
