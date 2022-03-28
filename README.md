# Scene recognition

1. [Setting up environment](#set-up-environment)
2. [Installing basic packages and AI packages](#install-basic-packages-and-ai-packages)
3. [Download pre-trained AI models for recognition process](#download-trained-ai-models-for-recognition-process)
4. [Runing code](#Running-code)
5. [Docker set up](#docker-set-up)

## Set up environment
Installing miniconda for environment variable control:
```
wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
Creating conda envirenment
```
conda create -n scene python=3.8
conda activate scene 
pip install --upgrade pip
```
**Please make sure that the python version >= 3.6**
## Installing basic packages and AI packages
Clone the repository and enter to root folder of it:
```
git clone <gitlab_link>
cd <project_directory>
```
Installing basic packages:
```
pip install -r requirements.txt
```
Installing AI packages:
```
pip install torch==1.7.0+cu110 torchvision==0.8.1+cu110 torchaudio===0.7.0 -f https://download.pytorch.org/whl/torch_stable.html
```
Please note that these AI packages are **only compatible with CUDA 11.1**

## Download trained AI models for recognition process
In root directory of project (using when testing not using for deploy docker):
```
mkdir weights
gdown https://drive.google.com/uc?id=1f1oHRT5t-tItQtlXknq4Dd9kH3ubhEV0 -O ./weights/checkpoint.pth
```

## Docker set up

Export environment variables:
```
export IMAGE_NAME=scene-recognition
export GPU_ID=0
export NAME=scene-recognition
export WORKDIR=/usr/local/app
export CURRENT_DIR=`pwd`
export HOST=27017
export MONGODB_HOST=mongo_server
export APP_PORT=<port>
export APP_HOST=0.0.0.0
export MONGO_USER=<user_db>
export MONGO_PASS=<password>
export MONGO_DB=admin
```

Build docker:  
```
docker build -t $IMAGE_NAME .
``` 
Run docker:
```
docker run -d -it --network rtx0  -e MONGO_PORT=$HOST -e MONGODB_HOST=$MONGODB_HOST -e MONGO_USER=$MONGO_USER  -e MONGO_PASS=$MONGO_PASS  -e MONGO_DB=$MONGO_DB  -h ai_worker -p $APP_PORT:$APP_PORT -e APP_HOST=$APP_HOST -e APP_PORT=$APP_PORT  --name $NAME --gpus device=$GPU_ID  -v {current_dir}/.env:/usr/local/app/.env -v  {current_dir}/weights/checkpoint.pth:/usr/local/app/weights/checkpoint.pth  $IMAGE_NAME
```
