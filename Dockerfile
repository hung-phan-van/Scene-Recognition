FROM nvidia/cuda:11.2.0-cudnn8-devel-ubuntu18.04 as build

RUN apt-get update && apt-get -y install python3-pip libgl1-mesa-glx &&\
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY requirements_ai_lib.txt .

RUN python3 -m pip install --upgrade pip && \ 
    mkdir /install && \ 
    python3 -m pip install --ignore-installed --prefix /install -f https://download.pytorch.org/whl/torch_stable.html -r requirements_ai_lib.txt

RUN python3 -m pip install --ignore-installed --prefix /install -r requirements.txt 

RUN python3 -m pip install gdown


RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get -y install libgtk2.0-dev git unzip cmake make gcc build-essential yasm nasm libtool libc6 libc6-dev wget libnuma1 libnuma-dev openssl libssl-dev && \
    apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

WORKDIR /usr/local/app

COPY build_vpf.sh /usr/local/app

RUN ./build_vpf.sh

FROM python:3.6-slim as app

RUN apt-get update && apt-get -y install libgl1-mesa-glx libgtk2.0-dev

ENV PATH /usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES video,compute,utility

# copy lib from stage 0
COPY --from=build /install/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

# copy vpf from stage 0
COPY --from=build /install_vpf/vpf /usr/local/lib/python3.6/site-packages/vpf


# RUN cp /usr/local/lib/python3.6/site-packages/vpf/*.so /usr/lib/x86_64-linux-gnu && \
#     ln -s /usr/lib/x86_64-linux-gnu/libnvcuvid.so /usr/lib/x86_64-linux-gnu/libnvcuvid.so.1 && \
#     mv /usr/local/lib/python3.6/site-packages/vpf/*.h /usr/local/include 

RUN cp /usr/local/lib/python3.6/site-packages/vpf/*.so /usr/lib/x86_64-linux-gnu && \
    mv /usr/local/lib/python3.6/site-packages/vpf/*.h /usr/local/include 

WORKDIR /usr/local/app
COPY . /usr/local/app

ENTRYPOINT python3 app.py
# ENTRYPOINT python3 app.py --hls_url https://trailer.vieon.vn/Teaser_RMVN_ChoiLaChay.mp4 --season_id bc45168d-1bec-4023-bbf1-bb005b2bf984 --content_id 30b0a3d9-0379-4717-a630-35dcad6f6302  --video_url test_video 