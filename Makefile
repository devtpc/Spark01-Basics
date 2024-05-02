CONFIG = ./configscripts/config.conf
include ${CONFIG}

install-requirements:
	pip install -r requirements.txt

#propagateing config settings to the respective folders/files
refresh-confs:
	@cd configscripts && \
	sh refresh_confs.sh

#docker commands - Note: docker dameon should be running
docker-copy:
	@echo "Copying python scripts to the destination folder"
	@cp -r src/main/python/*.py docker/pyscripts
docker-build: docker-copy
	@echo "Building docker image" $(DOCKER_IMAGE_NAME)
	@cd docker && \
	docker build . -t $(DOCKER_IMAGE_NAME)
docker-push:
	@echo "Pushing docker image" $(DOCKER_IMAGE_NAME)
	@docker push $(DOCKER_IMAGE_NAME)
	@echo docker image $(DOCKER_IMAGE_NAME) pushed.
docker-upload: docker-build docker-push


#create infra with terraform - Note: you should be lgged in with 'az login'
planinfra:
	@cd terraform && \
	terraform init --backend-config=backend.conf && \
	terraform plan -out terraform.plan

createinfra: planinfra
	@cd terraform && \
	terraform apply -auto-approve terraform.plan

#retrieve azure storage key and save it to a config file
retrieve-storage-keys:
	@echo "Retrieving azure keys"
	@cd configscripts && \
	sh retrieve_storage_keys.sh

#upload data to the provisioned storage account
uploaddata:
	@echo "Uploading data"
	@cd configscripts && \
	sh upload_data.sh

# Set open new terminal command. "kubectl proxy" should run in a new open terminal, which opens differently in different OS-s. Tested in Windows with Git Bash
ifeq ($(OS),Windows_NT)
    # Windows with Git Bash
    NEW_TERMINAL := cmd //c start cmd //k
else ifeq ($(shell uname),Linux)
    # Linux
    NEW_TERMINAL := x-terminal-emulator -e
else ifeq ($(shell uname),Darwin)
    # macOS
    NEW_TERMINAL := open -a Terminal
else
    $(error Unsupported operating system: $(shell uname))
endif


# preparing environment for spark-submit to tha AKS clustrer
retrieve-aks-credentials:
	@cd configscripts && \
	sh retrieve_aks_credentials.sh

prepare-spark-service-acc:
	@kubectl create serviceaccount spark
	@kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default

run-proxy:
	@echo "Opening kubectl proxy in new terminal"
	@$(NEW_TERMINAL) "kubectl proxy"
	@sleep 1

prepare-spark: retrieve-aks-credentials prepare-spark-service-acc run-proxy


#submitting the tasks to the cluster

#test task
submit-pi2: export PYTHON_FILE = $(PYTHON_FILE_PI)
submit-pi2:
	@cd configscripts && \
	sh submit_spark.sh

#test task 2
submit-small: export PYTHON_FILE = $(PYTHON_FILE_SMALL)
submit-small:
	@cd configscripts && \
	sh submit_spark.sh

#THE REAL TASK
submit-task: export PYTHON_FILE = $(PYTHON_FILE_TASK)
submit-task:
	@cd configscripts && \
	sh submit_spark.sh

#Verifying task
submit-verify: export PYTHON_FILE = $(PYTHON_FILE_VERIFY)
submit-verify:
	@cd configscripts && \
	sh submit_spark.sh


#destroy cluster with terraform. Only the cluster, the data storage part remains	
destroy-cluster:
	@cd terraform && \
	terraform destroy -auto-approve --target azurerm_kubernetes_cluster.bdcc

#bigger blocks

# all functions after `az login`:
all: refresh-confs docker-upload createinfra retrieve-storage-keys uploaddata prepare-spark submit-task destroy-cluster

# all functions except upload after `az login` - used, when storage account remained, bud cluster is destroyed
all-but-upload: refresh-confs docker-upload createinfra retrieve-storage-keys prepare-spark submit-task destroy-cluster