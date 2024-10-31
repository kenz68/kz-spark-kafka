import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark.sql.types import StructType, StructField, DoubleType, TimestampType

if __name__ == "__main__":
    # Define the schema
    schema = StructType([
        StructField("ts_min_bigint", TimestampType(), True),
        StructField("measurement", DoubleType(), True)
    ])

    dfs = []
    spark = SparkSession.builder.getOrCreate()
    # Process each room directory
    for room_dir in os.listdir(".\\dataset\\KETI"):
        if not room_dir.endswith('.txt'):
            room_id = room_dir.strip()  # Assumes the directory name is the room ID

            # Initialize a dictionary to store the data for this room
            room_data = {}

            # Process each CSV file in the room directory
            for sensor_file in os.listdir(f".\\dataset\\KETI\\{room_dir}"):
                sensor_name = sensor_file.strip().split('.')[0]  # Assumes the file name is the sensor name

                # Load the CSV file into a dataframe and add it to the room data dictionary
                df = spark.read.format("csv") \
                    .option("header", False) \
                    .option("inferSchema", False) \
                    .schema(schema) \
                    .load(f".\\dataset\\KETI\\{room_dir}\\{sensor_file}") \
                    .withColumnRenamed("measurement", sensor_name)

                room_data[sensor_name] = df

            # Combine the dataframes for all sensors into a single dataframe for this room
            df = room_data['co2']
            for sensor_name in ['light', 'temperature', 'humidity', 'pir']:
                df = df.join(room_data[sensor_name], on="ts_min_bigint", how="inner")

            # Add the room ID as a column
            df = df.withColumn("room", lit(room_id))
            dfs.append(df)
            # Add the combined dataframe to the list of dataframes
            # df.show(truncate=False)

    for df_item in dfs:
        print("writing...", df_item["ts_min_bigint"])
        kafka_df = df_item.selectExpr("CAST(ts_min_bigint AS STRING) as key", "to_json(struct(*)) as value")
        # Write the DataFrame to Kafka
        kafka_df.write\
            .format("kafka")\
            .option("kafka.bootstrap.servers", "127.0.0.1:9092")\
            .option("topic", "office_index")\
            .save()

    # Stop spark session
    spark.stop()
