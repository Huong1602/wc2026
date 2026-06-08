FROM node:20-bookworm-slim

WORKDIR /app/backend

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 python3-pip python3-venv \
  && rm -rf /var/lib/apt/lists/*

COPY backend/package*.json ./
RUN npm install

COPY backend/ ./
COPY ml/ ../ml/

RUN python3 -m pip install --break-system-packages -r ../ml/requirements.txt

EXPOSE 3000

CMD ["npm", "start"]
