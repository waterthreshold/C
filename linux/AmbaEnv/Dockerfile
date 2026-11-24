# Use Ubuntu 22.04 as base image
FROM ubuntu:22.04

# Set environment to noninteractive to avoid tzdata and other prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install basic packages (optional, adjust as needed)
RUN ln -fs /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" > /etc/timezone && \
    apt-get update && apt-get install -y \
    bash \
    curl \
    sudo \
    gcc-arm-none-eabi \
    unzip \
    git \
    git-lfs \
    jq \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /app
COPY toolchain.zip ./toolchain.zip
COPY ubuntuToolChain-linux5.15-202304 ./ubuntuToolChain-linux5.15-202304
# Make it executable
RUN unzip toolchain.zip
RUN chmod +x ./ubuntuToolChain-linux5.15-202304

# Run your setup script
RUN ./ubuntuToolChain-linux5.15-202304 
COPY git-build /usr/bin/git-cec
COPY cec.json /etc/cec.json 
RUN chmod 755 /usr/bin/git-cec 

# Set entrypoint or command if needed
CMD ["/bin/bash"]

