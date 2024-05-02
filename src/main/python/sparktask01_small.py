from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import pygeohash as pgh
import requests
from pyspark.sql.functions import avg,max

# constants
OPENCAGE_API_PATH = "https://api.opencagedata.com/geocode/v1/json"

if __name__ == '__main__':

    # Start pyspark session
    spark = SparkSession.builder.appName("Sparkbasics01").getOrCreate()

    # Read configs and secrets from context
    DATA_PATH = spark.sparkContext.getConf().get("spark.tp_sparkbasics01.datapath")

    # Remark: DATA_PATH access keys should be set in the spark-submit command

    # Load hotels data
    df_hotels = spark.read.option("header", "true").csv(f'{DATA_PATH}/hotels')

    #filter the dataframe where goe coordinates are invalid
    df_result = df_hotels.filter("Latitude is NULL OR Longitude is NULL OR Latitude = 'NA' OR Longitude = 'NA'")

    print("---------------------result count------------",df_result.count())
    print("---------------------Writing to------------",f'{DATA_PATH}/smallresults')

    #write result to csv file on storage
    df_result.coalesce(1).write.mode('overwrite').csv(f'{DATA_PATH}/smallresults')
    
    spark.stop()
