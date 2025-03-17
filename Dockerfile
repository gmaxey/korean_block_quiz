FROM ubuntu:22.04

WORKDIR /app

# Install base dependencies and build tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    mecab \
    libmecab-dev \
    curl \
    build-essential \
    automake \
    autoconf \
    && rm -rf /var/lib/apt/lists/*

# Manually install mecab-ko and mecab-ko-dic
RUN curl -L -o mecab-ko.tar.gz "https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.2.tar.gz" \
    && tar xvf mecab-ko.tar.gz \
    && cd mecab-0.996-ko-0.9.2 \
    && ./configure && make && make install \
    && cd .. \
    && curl -L -o mecab-ko-dic.tar.gz "https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.1.1-20180720.tar.gz" \
    && tar xvf mecab-ko-dic.tar.gz \
    && cd mecab-ko-dic-2.1.1-20180720 \
    && ./autogen.sh && ./configure && make && make install \
    && ldconfig \
    && cd .. \
    && rm -rf mecab-ko.tar.gz mecab-ko-dic.tar.gz mecab-0.996-ko-0.9.2 mecab-ko-dic-2.1.1-20180720

# Verify system MeCab works
RUN mecab --version

# Update pip and setuptools, then install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools \
    && pip3 install --no-cache-dir flask==2.3.3 wordfreq[cjk]==3.1.1 \
    && pip3 install --no-cache-dir --force-reinstall --no-binary mecab-python3 mecab-python3==1.0.9

# Debug installation
RUN ls -la /usr/local/lib/python3.10/dist-packages/MeCab \
    && python3 -c "import sys; print('sys.path:', sys.path)" \
    && python3 -c "import MeCab; mecab = MeCab.Tagger(); print('MeCab test:', mecab.parse('테스트'))"

# Copy project files
COPY . /app

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
