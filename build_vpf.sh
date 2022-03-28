#!/bin/bash

export ROOT_VPF=/install_vpf
echo $ROOT_VPF

mkdir $ROOT_VPF

cd $ROOT_VPF
if [ ! -d "$ROOT_VPF/FFmpeg" ]
then
    git clone https://github.com/FFmpeg/FFmpeg.git
    cd FFmpeg
    git fetch
    git pull origin master
    git checkout 258a88dfe48e0eea1dd62ff196db36180d02a16e
    cd ..
fi
cd FFmpeg

mkdir -p $(pwd)/build_x64_release_shared 
./configure \
--prefix=$(pwd)/build_x64_release_shared \
--disable-static \
--disable-stripping \
--disable-doc \
--enable-shared \
--enable-openssl

make -j 12 && make install

cd $ROOT_VPF
if [ ! -d "$ROOT_VPF/Video_Codec_SDK_11.0.10" ]
then
    gdown https://drive.google.com/uc?id=1sSRzUsAyrCSirhDsM_qgueGJK6TMB9M1
    unzip Video_Codec_SDK_11.0.10.zip
fi

# Export paths to Video Codec SDK and FFMpeg
export PATH_TO_SDK=$ROOT_VPF/Video_Codec_SDK_11.0.10
export PATH_TO_FFMPEG=$ROOT_VPF/FFmpeg/build_x64_release_shared

# Clone repo and start building process
cd $ROOT_VPF
if [ ! -d "$ROOT_VPF/VideoProcessingFramework" ]
then
    git clone https://github.com/NVIDIA/VideoProcessingFramework
    cd VideoProcessingFramework
    git fetch
    git pull origin master
    git checkout 0e7413ec07f965aac0b13683813c085d435105b1
    cd ..
fi

if [ ! $(cat "$ROOT_VPF/VideoProcessingFramework/CMakeLists.txt" | grep "/usr/local/cuda/lib64/stubs") ]
then
    sed -i '/\link_directories(\/usr\/local\/cuda\/lib64)/a\\t\link_directories(\/usr\/local\/cuda\/lib64\/stubs)' VideoProcessingFramework/CMakeLists.txt
fi

# Export path to CUDA compiler (you may need this sometimes if you install drivers from Nvidia site):
export CUDACXX=/usr/local/cuda/bin/nvcc

# Now the build itself
cd VideoProcessingFramework
export INSTALL_PREFIX=$(pwd)/install
mkdir -p install
mkdir -p build
cd build

# If you want to generate Pytorch extension, set up corresponding CMake value GENERATE_PYTORCH_EXTENSION
cmake .. \
  -DFFMPEG_DIR:PATH="$PATH_TO_FFMPEG" \
  -DVIDEO_CODEC_SDK_DIR:PATH="$PATH_TO_SDK" \
  -DGENERATE_PYTHON_BINDINGS:BOOL="1" \
  -DGENERATE_PYTORCH_EXTENSION:BOOL="0" \
  -DCMAKE_INSTALL_PREFIX:PATH="$INSTALL_PREFIX"
make && make install

cd $ROOT_VPF
if [ ! -d "$ROOT_VPF/vpf" ]
then
    mkdir vpf
fi

cp VideoProcessingFramework/install/bin/* vpf/
cp -r $PATH_TO_FFMPEG/lib/* vpf
cp $ROOT_VPF/Video_Codec_SDK_11.0.10/Lib/linux/stubs/x86_64/* vpf
cp $ROOT_VPF/Video_Codec_SDK_11.0.10/Interface/* vpf
