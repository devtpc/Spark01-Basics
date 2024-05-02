# Spark Basics Homework

## Introduction

This project is a Homework material from the EPAM Date Engineering Mentor program. The main idea behind this task is to create a Spark ETL job using Azure Kubernetes Service (AKS). Infrastructure should be set up using Terraform. The original copyright belongs to [EPAM](https://www.epam.com/). 

Some tasks from the original README:

* Setup needed requirements into your env: `pip install -r requirements.txt`
* Add your code in `src/main/`
* Test your code with `src/tests/`
* Package your artifacts
* Modify dockerfile if needed
* Build and push docker image
* Deploy infrastructure with terraform
* Launch Spark app in cluster mode on AKS

Some original instructions about the task itself:

* Download/fork the backbone project
* Download the [data files](https://static.cdn.epam.com/uploads/583f9e4a37492715074c531dbd5abad2/dse/m06sparkbasics.zip). Unzip it and upload into provisioned via Terraform storage account.
* Create Spark ETL job to read data from storage container.
* Check hotels data on incorrect (null) values (Latitude & Longitude). For incorrect values map (Latitude & Longitude) from OpenCage Geocoding API in job on fly (Via REST API).
* Generate geohash by Latitude & Longitude using one of geohash libraries (like geohash-java) with 4-characters length in extra column.
* Left join weather and hotels data by generated 4-characters geohash (avoid data multiplication and make you job idempotent)
* Deploy Spark job on Kubernetes Service, to setup infrastructure use terraform scripts from module
* Development and testing are recommended to do locally in your IDE environment.
* Store enriched data (joined data with all the fields from both datasets) in provisioned with terraform Storage Account preserving data partitioning and parquet format in “data” container 
* Expected results
  - Repository with Docker, configuration scripts, application sources etc.
  - Upload in task Readme MD file with link on repo, fully documented homework with screenshots and comments.

## About the repo

This repo is hosted [Here](https://github.com/devtpc/Spark01-Basics)

> [!NOTE]
> The original data files are not included in this repo, only the link.
> Some configuration files, API keys, tfvars are not included in this repo.


## Prerequisites

* The necessiary software environment should be installed on the computer (python, spark, azure cli, docker, terraform, etc.)
* For Windows use Gitbash to run make and shell commands. (It was deployed and tested on a Windows machine)
* Have an Azure account (free tier is enough)
* Have an Azure storage account ready for hosting the terraform backend
* Register at [Opencage](https://opencagedata.com/) and get a key for their API


## Preparatory steps

### Setup the local environment

Run  `pip install -r requirements.txt` or `make install-requirements`

### Download the data files

Download the data files from [here](https://static.cdn.epam.com/uploads/583f9e4a37492715074c531dbd5abad2/dse/m06sparkbasics.zip).
Exctract the zip file, and copy its content to this repo. Rename the 'm06sparkbasics' folder to 'data'.
The file structure should look like this:

![File structure image](/screenshots/img_data_file_structure.png)

### Setup your configuration

Go to the [configcripts folder](/configscripts/) and copy/rename the `config.conf.template` file to `config.conf`. Change the AZURE_BASE, OPENCAGE_API_KEY, DOCKER_IMAGE_NAME values as instructed within the file.

In the [configcripts folder](/configscripts/) copy/rename the `terraform_backend.conf.template` file to `terraform_backend.conf`. Fill the parameters with the terraform data

Propagate your config data to other folders with the [refreshconfs.sh](/configscripts/refresh_confs.sh) script, or with `make refresh-confs` from the main folder

The details are in comments in the config files

### Optional: Inspect the python files

The main file, which performs the required task is the [sparktask01.py](src/main/python/sparktask01.py) in the [/src/main/python](src/main/python) folder. The file gets its configuration data form the spark-submit configuration. The source code id documentet with comments.

The task processing is very time-consuming, so for testing purposes other python files were also added, like [sparktask01_small.py](src/main/python/sparktask01_small.py), [sparktask01_verify.py](src/main/python/sparktask01_verify.py) and [pi2.py](src/main/python/pi2.py). These are not required for the task, they are solely for testing purposes.

### Optional: Run some unit tests locally

There are unit tests in [src/test/test_sparktask01.py](src/test/test_sparktask01.py). To run the test, go to the src folder and type:
```
python -m unittest discover -s test
```

This is the result of the unit test:

![Unittest result image](/screenshots/img_unittest_result.png)

## Deploying the app in the Azure cloud

Before starting, make sure, that config files were correctly set up in the first step. There should be a terraform.auto.tvars file with your azure config settings, and a backend.conf file with the backend settings in the terraform folder.

Log in to Azure CLI with `az login`

> [!NOTE]
> The following steps can be executed together by calling `make all` from the main folder. However, it is advisible to perform the steps individually. The makefile and some shell scripts behind are decumented with comments

### Create and push the Docker image

Before creating the image make sure your docker daemon / docker desktop is running, and you are logged in your dockerhub account.

Enter the main folder in bash. Copy the files to docker folder, build the image, and push to DockerHub by the command `make docker-upload` This command copies the python files to the docker/pyscript folder, builds the image, and pushes it to DockerHub
Alternatively, after manually copying the files to docker/pyspripts folder (which you don't need if you use the `make` command) these command can be run:
```
# substitute $DOCKER_IMAGE_NAME with the image name in username/imagename:tag format
# Build the image
docker build ./docker -t $DOCKER_IMAGE_NAME

# push the image
docker push $DOCKER_IMAGE_NAME
```
The image is pushed to dockerhub:

![Docker pushed image](/screenshots/img_docker_pushed.png)

### Setup the azure infrastructure with terraform

Use `make createinfra` command to your azure infrastructure. Alternatively, to do it step-by-step:

In your terraform folder:
```
#initialize your terraform
terraform init --backend-config=backend.conf

#plan the deployment
terraform plan -out terraform.plan

#deploy. If asked, answer yes
terraform apply terraform.plan
```
After running the script, you get a message, that 'Apply complete'. The following picture shows a modification, if you run it for the first time, All resources would be in the 'added' category.

![Terraform created](/screenshots/img_terraform_created.png)

The original template suggested a vm_size of "Standard_D2_v2", but it was modified to "Standard_D3_v2"

### Optional: Verify the infrastructure
To verify infrastructure visually, login to the Azure portal, and enter resource groups. There are  2 new resource groups:
* the one, which was parameterized, rg-youruniquename-yourregion

![AKS created 1](/screenshots/img_aks_created_1.png)

* the managed cluster resource group, starting with MC_

![AKS created 2](/screenshots/img_aks_created_2.png)

After entering the AKS, it can be observed, that events are occuring, it confirms that the cluster is up and running:

![AKS created 3](/screenshots/img_aks_created_3.png)

The data container was created:

![AKS created 4](/screenshots/img_aks_created_4.png)

### Save needed keys from Azure
Storage access key will be needed in the spark-submit, so save the storage account key from Azure by typing `make retrieve-keys`. This saves the storage key to `configscripts/az_secret.conf` file. For retrieving, the command uses internally the following structure:
```
keys=$(az storage account keys list --resource-group $AKS_RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query "[0].value" --output tsv)
```

### Upload data input files to the storage account

Now, that you have your storage account and key ready, the data files can be uploaded to the storage. Type `make uploaddata` to upload the data files. This command uses internally the following structure:

```
az storage blob upload-batch --source ./../data --destination data  --account-name $STORAGE_ACCOUNT --account-key $STORAGE_ACCOUNT_KEY
```

The data is uploaded to the server:

![Data upload 1](/screenshots/img_dataupload_1.png)

![Data upload 2](/screenshots/img_dataupload_2.png)

### Prepare the AKS cluster for spark-submit

If you destroyed your previous AKS cluster, and set it up with the same name, you might need to edit your .kube/.config file to remove your previous credentials.

The cluster can be set up by typing `make prepare-spark`
The individual steps behind this command:

```
#Retrieve the AKS credentials
az aks get-credentials --resource-group $AKS_RESOURCE_GROUP --name $AKS_CLUSTER

#Prepare service account and clusterrolebinding
kubectl create serviceaccount spark
kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default

#Start proxy, so that you can communicate with your clustar as localhost. Start this in a different terminal/command prompt, as this will block the terminal!
kubectl proxy
```

![Prepare spark image](/screenshots/img_prepare_spark_1.png)

#### Optional: Check the cluster nodes by typing `kubectl get nodes`

The AKS node is Ready:

![Prepare spark image2](/screenshots/img_prepare_spark_2.png)

### Optional: Verify the setup by deploying a small task

It's better to verify, that the AKS cluster can run a spark job on a smaller task, before running the big task.

#### Optional: Verify the setup by deploying pi2

Try to run the pi2 task by typing `make submit-pi2`

This script is a classic spark testscript (modified a bit to run quicker) to test that park is running. It calculates the rough value of pi. If everything goes well, the code will run, stop at the end, with the termination reason: "completed", as in this picture:

![Pi result 1](/screenshots/img_pi_result_1.png)

Type `kubectl get pods` to see the name of the pod, and after that `kubectl logs <pod name>` to see the logs. You can find the output of '---  Pi is roughy' within the logs, confirming, that the spark job was really executed and completed.

![Pi result 2](/screenshots/img_pi_result_2.png)


#### Optional: Verify the setup by deploying small

The pi task was very basic: it didn't use our data, and it didn't need to connect to the storage. Let's try something more serious, but still a small task! Try to run the small task by typing `make submit-small` This task connects to the hotel data, creates a subset where the Latitude and Longitude data are null or 'NA' and writes the result to the storage.

The code runs, stops at the end with the termination reason: "completed". We can verify the logs as previously, or go to the storage to verify, that the results have been written out.

The result appeared in the storage:

![Small result 1](/screenshots/img_small_result_1.png)

After downloading and opening the csv file, the 34 null and 'NA' hotels can be observed.

![Small result 2](/screenshots/img_small_result_2.png)


### Deploying the final application

Deploy the final task by running `make submit-task`. The code behind this command:
```
spark-submit \
    --master k8s://http://127.0.0.1:8001 \
    --deploy-mode cluster  \
    --name spark-app \
    --conf spark.driver.memory=4G \
    --conf spark.kubernetes.container.image=$DOCKER_IMAGE_PATH \
    --conf spark.hadoop.fs.azure.account.key.$STORAGE_ACCOUNT.dfs.core.windows.net=$STORAGE_ACCESS_KEY \
    --conf spark.tp_sparkbasics01.datapath="abfss://data@$STORAGE_ACCOUNT.dfs.core.windows.net" \
    --conf spark.tp_sparkbasics01.opencagekey="$OPENCAGE_KEY" \
    --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
    local:///opt/pyscripts/$PYTHON_FILE
```
As we are using `kubectl proxy`, there's no need to know the cluster's real IP, localhost (127.0.0.1) can be used.

In this case, driver memory was set to 4G. It was enough to run this task successfully, however, further tweaking might increase the performance.

Our secret is passed to the python file with the arbitrarily choosen spark.YOUR_CHOICE configurations. The secrets are the Opencage API key, and the access key to the storage.

The final task successfuly completed.

![Task_completed 1](/screenshots/img_task_completed_1.png)

The task used 2 executor pods besides the driver.

![Task_completed 2](/screenshots/img_task_completed_2.png)

On the Azure portal, it can be checked, that the parquet files really were created.

![Task_completed 3](/screenshots/img_task_completed_3.png)


### Verifying the results

As the parquet files are not in a human-readable format, run `make submit-verify` to read the parquet files. As written earlier in the pi2 and small task, examine the pod logs! Within the logs 20 rows can be seen:

![Verify task](/screenshots/img_verify_task.png)

This way it could be verified, that the result is in the required format.

### Destroy the AKS cluster

Run `make destroy-cluster` to destroy the AKS cluster. This prevents the cluster from running, reducing the costs.

![Destroy](/screenshots/img_destroy.png)

The above command destroys only the cluster, but preserve the storage with the data and the results.