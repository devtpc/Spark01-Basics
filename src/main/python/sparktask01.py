from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import pygeohash as pgh
import requests
from pyspark.sql.functions import avg,max

# constants
OPENCAGE_API_PATH = "https://api.opencagedata.com/geocode/v1/json"


# Geocodeing & geohash functions
def get_api_geometry(country, city, address):
    """
    Get the latitude and longitude as a double tuple from the parameters using OpenCage API.
    If no result, returns (0,0) (non-existent hotel position in the Atlantic Ocean)
    """
    query = f"{address},+{city}"
    params =  {
        "key": OPENCAGE_API_KEY,
        "q": query,
        "countrycode":country
    }
    response = requests.get(OPENCAGE_API_PATH, params = params)
    result = response.json()
    if result['results']:
        geometry = (result['results'][0]['geometry']['lat'],result['results'][0]['geometry']['lng'])
        return geometry
    return (0.0,0.0)

def get_latitude(latitude, country, city, address) -> StringType:
    """  Get the original latitude as String, or if not given (null, 'NA'), gets Latitude using OpenCage API.  """
    try:
        floatvalue = float(latitude)
        return latitude
    except:
        return str(get_api_geometry(country, city, address)[0])


def get_longitude(longitude, country, city, address) -> StringType:
    """   Get the original latitude as String, or if not given (null, 'NA'), gets Latitude using OpenCage API.  """
    try:
        floatvalue = float(longitude)
        return longitude
    except:
        return str(get_api_geometry(country, city, address)[1])

def geohash_encode(lat,lng):
    """   Get 4-digit geohash for a latitude/longitude  """
    return pgh.encode(float(lat), float(lng), precision=4)

# UDF functions for the Dataframe Operations
udf_lat = udf(get_latitude, StringType())
udf_lng = udf(get_longitude, StringType())
udf_hash_encode = udf(geohash_encode, StringType())


if __name__ == '__main__':

    # Start pyspark session
    spark = SparkSession.builder.appName("Sparkbasics01").getOrCreate()

    # Read configs and secrets from context
    DATA_PATH = spark.sparkContext.getConf().get("spark.tp_sparkbasics01.datapath")
    OPENCAGE_API_KEY = spark.sparkContext.getConf().get("spark.tp_sparkbasics01.opencagekey")

    # Remark: DATA_PATH access keys should be set in the spark-submit command

    # Load hotels data
    df_hotels = spark.read.option("header", "true").csv(f'{DATA_PATH}/hotels')

    # geocode address to lat/lng, if it's null or 'NA'
    df_corr_hotels = df_hotels \
        .withColumn("Latitude", udf_lat(df_hotels['Latitude'],df_hotels['Country'], df_hotels['City'], df_hotels['Address'])) \
        .withColumn("Longitude", udf_lng(df_hotels['Longitude'],df_hotels['Country'], df_hotels['City'], df_hotels['Address']))

    # Calculate geohash for hotels
    df_corr_hotels = df_corr_hotels.withColumn("geohash", udf_hash_encode(df_corr_hotels['Latitude'], df_corr_hotels['Longitude']))

    # Read Weather data, and calculate its geohash
    df_weather = spark.read.parquet(f'{DATA_PATH}/weather')
    df_weather= df_weather.withColumn("geohash_wthr", udf_hash_encode(df_weather['lat'], df_weather['lng']))

    # Aggregate weather data by geohash and date. For temperature, calculate the average
    df_weather_corr = df_weather.groupBy(["geohash_wthr","wthr_date"]) \
        .agg(avg("avg_tmpr_f").alias("avg_tmpr_f"), \
            avg("avg_tmpr_c").alias("avg_tmpr_c"), \
            max("year").alias("year"), \
            max("month").alias("month"), \
            max("day").alias("day")
            )

    # Create left join on data. Every hotel will remain, with their respective weather data, if there are no weather data, than null for the weather
    df_result = df_corr_hotels.join(df_weather_corr, df_corr_hotels.geohash == df_weather_corr.geohash_wthr, 'left')

    # Write results as parquet
    df_result.write.mode('overwrite').partitionBy('year', 'month','day').parquet(f'{DATA_PATH}/result')
    spark.stop()
