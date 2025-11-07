curl -sL https://aka.ms/DevTunnelCliInstall | bash

devtunnel create vllm-webui --allow-anonymous
devtunnel port create vllm-webui --port-number 3000 --protocol http
devtunnel host vllm-webui 

devtunnel create vllm --allow-anonymous
devtunnel port create vllm --port-number 8000 --protocol http
devtunnel host vllm-webui 
