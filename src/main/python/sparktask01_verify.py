from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import pygeohash as pgh
import requests
from pyspark.sql.functions import avg,max

if __name__ == '__main__':

    # Start pyspark session
    spark = SparkSession.builder.appName("Sparkbasics01").getOrCreate()

    # Read configs and secrets from context
    DATA_PATH = spark.sparkContext.getConf().get("spark.tp_sparkbasics01.datapath")

    # Read result data
    df_result = spark.read.parquet(f'{DATA_PATH}/result')
    df_result.show()
    spark.stop()
