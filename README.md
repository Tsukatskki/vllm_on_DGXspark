# vllm_on_DGXspark
This is a fast deployment of vLLM on DgxSparks by Docker, or any other kind of server using ARM64 and CUDA13 at the same time.
vLLM uses DeepSeek-OCR as the first model.
# Setup
## Step 1: Preperation
- Although the docker is used for deployment, local environment will be used for building wheels.
'''
sh preparation.sh
'''
## Step 2: Validate GPU penetration (this is a MUST)
'''
docker run --rm --gpus all nvidia/cuda:12.4.1-runtime-ubuntu22.04 nvidia-smi
'''
## Step 3: Get a Token from HuggingFace
- a HuggingFace token is needed for downloading models.
- fill in '.env' with the HuggingFace token.
'''
HUGGING_FACE_HUB_TOKEN=fill_in_your_hf_token_here
'''
## Step 4: Build with docker
'''
docker compose up
'''
- the default vLLM will be running on port 8000 and a webui will be running on port 3000.
## Step 5: Use the service with Devtunnel
'''
# install Devtunnel
curl -sL https://aka.ms/DevTunnelCliInstall | bash

# initilize Webui
devtunnel create vllm-webui --allow-anonymous
devtunnel port create vllm-webui --port-number 3000 --protocol http
devtunnel host vllm-webui 

# initilize main service
devtunnel create vllm --allow-anonymous
devtunnel port create vllm --port-number 8000 --protocol http
devtunnel host vllm-webui 
'''

# Use DeepSeek-OCR in vLLM
- fill in api, port, input, output in 'pdf_processing.py'
'''
python pdf_processing.py
'''
- for a test using DeepSeek-OCR