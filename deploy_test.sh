docker build -t scene-test-v1 .

docker run -it --name scene-test-v1 --gpus device=2 --log-opt max-size=10m --log-opt max-file=5 -v /data/scene/weights:/usr/local/app/weights -v /usr/local/cuda-11.1:/usr/local/cuda -v /data/scene/env:/usr/local/app/env  -e API_URL=dev-task-pipeline.vie-api.com scene-test-v1:latest bash
