# Azure Deploy

Deploy the OWASP LLM Security Demo to Azure Container Instances using Terraform.

## Prerequisites

### 1. Build binaries compatible with AMD EPYC

Azure uses AMD EPYC CPUs. Build with generic AVX2 flags (no VNNI):
```bash
cd /path/to/llama.cpp

cmake -B build-azure \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="-O3 -march=x86-64-v3 -mno-avxvnni" \
  -DCMAKE_CXX_FLAGS="-O3 -march=x86-64-v3 -mno-avxvnni" \
  -DGGML_AVX2=ON \
  -DGGML_FMA=ON \
  -DGGML_AVX_VNNI=OFF \
  -DGGML_OPENMP=ON \
  -DBUILD_SHARED_LIBS=ON

cmake --build build-azure -j$(nproc)
```

### 2. Strip and copy binaries
```bash
strip build-azure/bin/llama-server build-azure/bin/owasp-llm-tool
strip build-azure/bin/*.so

cp build-azure/bin/llama-server /path/to/llmSecurityDemo/llama.cpp/build/bin/
cp build-azure/bin/owasp-llm-tool /path/to/llmSecurityDemo/llama.cpp/build/bin/
cp build-azure/bin/*.so* /path/to/llmSecurityDemo/llama.cpp/build/lib/
```

### 3. Build and push Docker image
```bash
cd /path/to/llmSecurityDemo
sudo docker-compose -f docker/docker-compose.yml build --no-cache
sudo docker tag docker_owasp-llm-demo:latest <YOUR_DOCKERHUB_USER>/owasp-llm-demo:<TAG>
sudo docker push <YOUR_DOCKERHUB_USER>/owasp-llm-demo:<TAG>
```

## Deploy

1. Open [Azure Cloud Shell](https://portal.azure.com)

2. Edit `main.tf` and set your values:
   - `location`: your preferred Azure region
   - `image`: your Docker Hub image
   - `dns_name_label`: unique name for your deployment

3. Initialize and apply:
```bash
cd infra/azure
terraform init
terraform apply
```

4. Open browser at the URL shown in output

## Shutdown

Always destroy when not using to avoid costs:
```bash
terraform destroy
```

## Costs

- ~0.05€/hour with 4 CPU + 4GB RAM
- ~36€/month if always runningi


