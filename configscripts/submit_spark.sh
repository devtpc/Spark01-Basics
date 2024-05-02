#run this only after you retreived ahe azure secret keys (you have the az_secret.conf) and your spark environment is prepared. For more details see README.md
source ./config.conf
source ./az_secret.conf

echo Submitting $PYTHON_FILE
#echo spark.hadoop.fs.azure.account.key.$STORAGE_ACCOUNT.dfs.core.windows.net=$STORAGE_ACCOUNT_KEY
#echo spark.tp_sparkbasics01.datapath="abfss://data@$STORAGE_ACCOUNT.dfs.core.windows.net"

echo "---- startin azure -----"
spark-submit \
    --master k8s://http://127.0.0.1:8001 \
    --deploy-mode cluster  \
    --name spark-app \
    --conf spark.driver.memory=4G \
    --conf spark.kubernetes.container.image=$DOCKER_IMAGE_PATH \
    --conf spark.hadoop.fs.azure.account.key.$STORAGE_ACCOUNT.dfs.core.windows.net=$STORAGE_ACCOUNT_KEY \
    --conf spark.tp_sparkbasics01.datapath="abfss://data@$STORAGE_ACCOUNT.dfs.core.windows.net" \
    --conf spark.tp_sparkbasics01.opencagekey="$OPENCAGE_KEY" \
    --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
    local:///opt/pyscripts/$PYTHON_FILE
echo "---- Ending azure -----"

#    --conf spark.hadoop.fs.azure.account.key.$STORAGE_ACCOUNT.blob.core.windows.net=$STORAGE_ACCESS_KEY \
#    --conf spark.kubernetes.file.upload.path='local:///opt' \

