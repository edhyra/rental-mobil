FROM mcr.microsoft.com/devcontainers/python:0-3.11

# Install project dependencies
WORKDIR /workspace
COPY .. /workspace
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]
