FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git \
    cmake \
    make \
    g++ \
    pkg-config \
    libglib2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libexpat1 \
    libgl1 \
    libegl1 \
    libgles2 \
    mesa-utils \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-util1 \
    libxcb-cursor0 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render0 \
    libxcb-render-util0 \
    libxcb-randr0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libsm6 \
    libice6 \
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/zrax/pycdc.git && \
    cd pycdc && \
    cmake . && \
    make && \
    make install && \
    cd .. && rm -rf pycdc

COPY . .

RUN useradd -m sandbox
USER sandbox

CMD ["python", "main.py"]
