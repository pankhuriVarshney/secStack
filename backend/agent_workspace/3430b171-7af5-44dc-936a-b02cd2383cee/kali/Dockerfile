FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl iputils-ping nano netcat-traditional nmap sqlmap \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]
