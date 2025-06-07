# Stage 1: Build environment
FROM docker.io/ursamajorlab/jammy-python:3.10.5

RUN python -m ensurepip --upgrade && \
    python -m pip install --upgrade pip setuptools wheel
# Verify Python and pip are available
RUN python --version && pip --version

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies with clearer error reporting
RUN pip install --no-cache-dir -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn \
    || { echo "pip install failed"; pip --version; python -m pip --version; exit 1; }

#字体  fc-list :lang=zh | grep -i "wqy"
RUN mkdir -p /usr/share/fonts/wqy && \
    curl -o /usr/share/fonts/wqy/wqy-microhei.ttc \
    https://github.com/oh-my-fish/plugin-foreign-env/raw/master/fonts/wqy-microhei.ttc && \
    fc-cache -fv

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Entrypoint
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]