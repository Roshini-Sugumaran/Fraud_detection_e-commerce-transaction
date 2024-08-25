# -*- coding: utf-8 -*-
"""bigdata_eda.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1tY302gdNanx80oXOYgfsFO7FqVtWxi71
"""

!pip install pyspark

from google.colab import drive
drive.mount('/content/drive')

from pyspark.sql import SparkSession
from pyspark.sql.functions import col,sum,count,isnull

spark = SparkSession.builder.appName("Fraud Detection").getOrCreate()

Train_Trans = spark.read.csv('/content/drive/MyDrive/Colab Notebooks/train_transaction.csv', header=True, inferSchema=True)
Train_Identity = spark.read.csv('/content/drive/MyDrive/Colab Notebooks/train_identity.csv', header=True, inferSchema=True)
Test_Trans= spark.read.csv('/content/drive/MyDrive/Colab Notebooks/test_transaction.csv', header=True, inferSchema=True)
Test_Identity = spark.read.csv('/content/drive/MyDrive/Colab Notebooks/test_identity.csv', header=True, inferSchema=True)

train_data = Train_Trans.join(Train_Identity, on='TransactionID', how='left')

test_data = Test_Trans.join(Test_Identity, on='TransactionID', how='left')

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import pandas as pd
import matplotlib.pyplot as plt

# Create a Spark session
spark = SparkSession.builder.appName("FraudAnalysis").getOrCreate()

# Assuming `train_data` is a PySpark DataFrame
# Replace 'ProductCD' and 'isFraud' with the actual column names in your DataFrame

# Define a window specification
window_spec = Window.partitionBy('ProductCD')

# Calculate the count and percentage
ax_data = (
    train_data
    .groupBy('ProductCD', 'isFraud')
    .count()
    .withColumn('total_count', F.sum('count').over(window_spec))
    .withColumn('percentage', F.col('count') / F.col('total_count'))
    .withColumn('percentage_str', F.format_number(F.col('percentage') * 100, 1))
    .select('ProductCD', 'isFraud', 'count', 'percentage_str')
    .toPandas()
)

# Plotting using Matplotlib
fig, ax = plt.subplots()

# Set width of bar
bar_width = 0.35

# Set position of bar on X axis
r1 = range(len(ax_data['ProductCD'].unique()))
r2 = [x + bar_width for x in r1]

# Plot bars
ax.bar(r1, ax_data[ax_data['isFraud'] == 0]['count'], color='b', width=bar_width, edgecolor='grey', label='Not Fraud')
ax.bar(r2, ax_data[ax_data['isFraud'] == 1]['count'], color='r', width=bar_width, edgecolor='grey', label='Fraud')

# Annotate with percentage values
for r in r1:
    product_cd = ax_data['ProductCD'].unique()[r]
    subset = ax_data[ax_data['ProductCD'] == product_cd]
    total_count = subset['count'].sum()
    for i, is_fraud in enumerate([0, 1]):
        count = subset[subset['isFraud'] == is_fraud]['count'].values[0]
        percentage = count / total_count * 100
        ax.annotate('{:.1f}%'.format(percentage), (r + i * bar_width, count), ha='center', va='bottom')

# Add labels, title, and legend
ax.set_xlabel('ProductCD')
ax.set_ylabel('Count')
ax.set_title('ProductCD Count Plot')
ax.set_xticks([r + bar_width/2 for r in r1])
ax.set_xticklabels(ax_data['ProductCD'].unique())
ax.legend()

plt.show()

import matplotlib.pyplot as plt
from pyspark.sql import functions as F

# Group the data by the 'isFraud' column and count the occurrences of each value
fraud_distribution = train_data.groupBy('isFraud').count().orderBy('isFraud')

fraud_distribution.show()

# Calculate the total count
total_count = fraud_distribution.select(F.sum('count')).collect()[0][0]

print(total_count)

# Convert the result to a Pandas DataFrame for easy plotting
fraud_distribution_df = fraud_distribution.toPandas()


# Define colors for the two classes
colors = ['blue', 'red']

plt.figure(figsize=(8, 6))
bars = plt.bar(fraud_distribution_df['isFraud'], fraud_distribution_df['count'], color=colors)
plt.title('Distribution of isFraud Variable')
plt.xlabel('isFraud')
plt.ylabel('Count')

# Set x-ticks to correspond to the categories 0 and 1
plt.xticks([0, 1])

# Add percentage labels to the bars
for bar in bars:
    height = bar.get_height()
    percent = (height / total_count) * 100
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{percent:.2f}%', ha='center', va='bottom')



plt.show()

# Convert the 'TransactionDT' column to a list for each dataset
train_TransactionDT = train_data.select('TransactionDT').rdd.flatMap(lambda x: x).collect()
test_TransactionDT = test_data.select('TransactionDT').rdd.flatMap(lambda x: x).collect()

# Plot the histograms using matplotlib
plt.figure(figsize=(12, 5))
plt.hist(train_TransactionDT, bins=50, alpha=0.5, label='Train', color='blue')
plt.hist(test_TransactionDT, bins=50, alpha=0.5, label='Test', color='green')
plt.title('Train - Test Transaction date - distribution')
plt.legend()
plt.show()

import pandas as pd
import seaborn as sns

from pyspark.sql.functions import count,col

import matplotlib.pyplot as plt

# Group the data by 'ProductCD' and 'isFraud' and calculate counts
grouped_data = train_data.groupBy('ProductCD', 'isFraud').agg(count('*').alias('count'))

# Calculate the total count for each 'ProductCD' category
total_count = train_data.groupBy('ProductCD').agg(count('*').alias('total_count'))

# Join the grouped_data with total_count to get the percentage
grouped_data_percentage = grouped_data.join(total_count, 'ProductCD') \
    .withColumn('percentage', (col('count') / col('total_count')) * 100)

# Show the results
grouped_data_percentage.show()

# Convert to Pandas DataFrame for visualization
grouped_data_percentage_pd = grouped_data_percentage.toPandas()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col



# Assuming you have a PySpark DataFrame df_train

# Calculate the day of the week for each transaction
df_train = train_data.withColumn("dayofweek", ((col("TransactionDT") / (60 * 60 * 24) - 1) % 7).cast("int"))

# Calculate the percentage of fraud transactions for each day of the week
tmp = df_train.groupBy("dayofweek").agg({"isFraud": "mean"}).withColumnRenamed("avg(isFraud)", "Percentage fraud transactions")

# Calculate the number of transactions for each day of the week
tmp_count = df_train.groupBy("dayofweek").count().withColumnRenamed("count", "Number of transactions")

# Join the two DataFrames on dayofweek
tmp = tmp.join(tmp_count, "dayofweek")

# Convert PySpark DataFrame to Pandas for plotting
tmp_pandas = tmp.toPandas()

# Import the necessary libraries for plotting
import matplotlib.pyplot as plt
import seaborn as sns

# Create a Matplotlib and Seaborn plot
fig, axes = plt.subplots(figsize=(12, 5))
axes = sns.lineplot(x=tmp_pandas['dayofweek'], y=tmp_pandas['Percentage fraud transactions'], color='r')
axes2 = axes.twinx()
axes2 = sns.barplot(x=tmp_pandas['dayofweek'], y=tmp_pandas['Number of transactions'], palette='summer')
axes.set_title('Fraud transaction vs dayofweek')

# Show the plot
plt.show()

from pyspark.sql.functions import hour, from_unixtime

#Convert the "TransactionDT" column to a timestamp
train_data = train_data.withColumn("TransactionDT", from_unixtime(train_data["TransactionDT"]).cast("timestamp"))

# Create a new column 'hour' based on the 'TransactionDT' column
df_train = train_data.withColumn("hour", hour(train_data["TransactionDT"]))

# Calculate the percentage of fraud transactions for each hour
tmp = df_train.groupBy("hour").agg({"isFraud": "mean"}).withColumnRenamed("avg(isFraud)", "Percentage fraud transactions")

# Calculate the number of transactions for each hour
tmp_count = df_train.groupBy("hour").count().withColumnRenamed("count", "Number of transactions")

# Merge the two DataFrames
tmp = tmp.join(tmp_count, ["hour"], "inner")

# Convert the PySpark DataFrame to a Pandas DataFrame for plotting
tmp_pd = tmp.toPandas()
# Sort the Pandas DataFrame by the 'hour' column in ascending order
tmp_pd = tmp_pd.sort_values(by="hour")

# Create the plot with sorted data
fig, axes = plt.subplots(figsize=(12, 5))
axes = tmp_pd.plot(x="hour", y="Percentage fraud transactions", kind="line", color="r", ax=axes)
axes2 = axes.twinx()
tmp_pd.plot(x="hour", y="Number of transactions", kind="bar", color="c", ax=axes2)

axes.set_title("Fraud transaction (no of transactions) vs hour")
plt.show()

# Count the missing values in the 'TransactionAmt' column
missing_count = df_train.filter(col('TransactionAmt').isNull()).count()

# Display the result
print("Number of missing values in 'TransactionAmt':", missing_count)

# Register Spark DataFrames as temporary SQL tables
train_data.createOrReplaceTempView("train_data")
test_data.createOrReplaceTempView("test_data")

# Use SQL to sample data and retrieve it as PySpark DataFrames
sampled_train_data = spark.sql("SELECT TransactionDT, TransactionAmt, isFraud FROM train_data")
sampled_test_data = spark.sql("SELECT TransactionDT, TransactionAmt FROM test_data")

# Convert the sampled PySpark DataFrames to Pandas DataFrames for visualization
sampled_train_pandas = sampled_train_data.toPandas()
sampled_test_pandas = sampled_test_data.toPandas()

# Create a figure with two subplots
fig, axes = plt.subplots(1,2, figsize=(15, 5))

# Scatterplot for Training Data
axes[0].scatter(sampled_train_pandas['TransactionAmt'], sampled_train_pandas['TransactionDT'], c=sampled_train_pandas['isFraud'])
axes[0].set_title('Transaction Amount - Train')
axes[0].set_ylabel('TransactionDT')
axes[0].set_xlabel('Transaction Amount')

# Scatterplot for Test Data
axes[1].scatter(sampled_test_pandas['TransactionAmt'], sampled_test_pandas['TransactionDT'],)
axes[1].set_title('Transaction Amount - Test')
axes[1].set_ylabel('TransactionDT')
axes[1].set_xlabel('Transaction Amount')

# Show the plot

plt.show()

from pyspark.sql.functions import log
#Log transform the 'TransactionAmt' column in the test DataFrame
test_amt = test_data.withColumn("LogTransactionAmt", log(test_data["TransactionAmt"]))

# Filter fraudulent and non-fraudulent transactions in the training DataFrame
dff_fraud = train_data.filter(df_train["isFraud"] == 1)
dff_notfraud = train_data.filter(df_train["isFraud"] == 0)

# Log transform the 'TransactionAmt' column in both DataFrames
dff_fraud = dff_fraud.withColumn("LogTransactionAmt", log(dff_fraud["TransactionAmt"]))
dff_notfraud = dff_notfraud.withColumn("LogTransactionAmt", log(dff_notfraud["TransactionAmt"]))

# Convert PySpark DataFrames to Pandas DataFrames for plotting
pd_dff_fraud = dff_fraud.select("LogTransactionAmt").toPandas()
pd_dff_notfraud = dff_notfraud.select("LogTransactionAmt").toPandas()
pd_test_amt = test_amt.select("LogTransactionAmt").toPandas()

# Plot the data using Matplotlib
fig, axes = plt.subplots(1, 2, figsize=(15, 8))
pd_dff_notfraud["LogTransactionAmt"].plot(kind="hist", ax=axes[0], label="not fraud")
pd_dff_fraud["LogTransactionAmt"].plot(kind="hist", ax=axes[0], label="fraud")
axes[0].set_title('Log(Fraud transaction distribution) Train')
axes[0].legend()

pd_test_amt["LogTransactionAmt"].plot(kind="hist", ax=axes[1])
axes[1].set_title('Log(Fraud transaction distribution) Test')

plt.show()

# Check the version of PySpark
!pip show pyspark

from pyspark.sql.functions import col

# Get the list of column names that meet the criteria
selected_columns = [col_name for col_name in train_data.columns if col_name.startswith('D') and len(col_name) <= 3]

# Select the specified columns and display the first few rows
df_train_selected = train_data.select(*selected_columns)
df_train_selected.show()

for col in selected_columns:
    # Select the relevant columns from the Spark DataFrame
    data = train_data.select("TransactionDT", col).toPandas()

    # Create a local Pandas DataFrame containing the data
    # 'toPandas' is used to convert the Spark DataFrame to a Pandas DataFrame for local processing

    # PLOT ORIGINAL D
    plt.figure(figsize=(15, 5))
    plt.scatter(data['TransactionDT'], data[col])
    plt.title(f'Original {col}')
    plt.xlabel('Time')
    plt.ylabel(col)
    plt.show()

# Sample 500 fraud and 500 non-fraud examples to plot
fraud_df = train_data.filter(col('isFraud') == 1).sample(False, 0.1)
non_fraud_df = train_data.filter(col('isFraud') == 0).sample(False, 0.1)

# Concatenate the DataFrames
sample_df = fraud_df.union(non_fraud_df)

# Specify the features to plot
d_cols = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15']


# Convert the sampled Spark DataFrame to Pandas DataFrame
sampled_data_pd = sample_df.toPandas()

# Set up Seaborn pair plot
sns.pairplot(vars=d_cols, hue='isFraud', data=sampled_data_pd, height=5)
plt.suptitle("\nPair Plots of D_features\n")
plt.show()

from pyspark.sql.functions import col

# Get the list of column names that meet the criteria
selected_columns = [col_name for col_name in train_data.columns if col_name.startswith('M') and len(col_name) <= 2]

# Select the specified columns and display the first few rows
df_train_selected = train_data.select(*selected_columns)
df_train_selected.show()

# Assuming `m_features` is a list of column names you want to analyze
m_features = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]

# Calculate missing values for each M column
missing_values = (
    train_data
    .select([sum(col(c).isNull().cast("int")).alias(c) for c in m_features])
)

# Show the results
missing_values.show()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import matplotlib.pyplot as plt
import seaborn as sns

# Assuming `m_features` is a list of column names you want to plot
m_features = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]

# Create a figure with subplots
fig, axes = plt.subplots(3, 3, figsize=(13, 15))
fig.tight_layout(pad=6.0)
fig.suptitle('Plotting for M features')
idx = 0

plt.margins(0.05, 0.1)

for i in range(3):
    for j in range(3):
        if idx == len(m_features):
            break

        f = m_features[idx]
        idx += 1

        # Use Spark SQL to calculate counts
        count_df = (
            train_data
            .groupBy(f, 'isFraud')
            .count()
            .withColumn('percentage', col('count') / train_data.count() * 100)
            .orderBy(f)
        )

        # Collect the results to the local machine
        local_counts = count_df.toPandas()

        # Plotting
        sns.barplot(x=f, y='percentage', hue='isFraud', data=local_counts, ax=axes[i, j])

        # Annotate the bars
        for p in axes[i, j].patches:
            x = p.get_bbox().get_points()[:, 0]
            y = p.get_bbox().get_points()[1, 1]
            axes[i, j].annotate('{:.1f}%'.format(y), (x.mean(), y), ha='center', va='bottom')

        axes[i, j].set_title(f + " Count Plot")

# Show the plots
plt.show()

# Sample 500 fraud and 500 non-fraud examples to plot
fraud_df = train_data.filter(col('isFraud') == 1).sample(False, 0.1)
non_fraud_df = train_data.filter(col('isFraud') == 0).sample(False, 0.1)

# Concatenate the DataFrames
sample_df = fraud_df.union(non_fraud_df)

# Specify the features to plot
c_cols = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14']


# Convert the sampled Spark DataFrame to Pandas DataFrame
sampled_data_pd = sample_df.toPandas()

# Set up Seaborn pair plot
sns.pairplot(vars=c_cols, hue='isFraud', data=sampled_data_pd, height=5)
plt.suptitle("\nPair Plots of C_features\n")
plt.show()

# Plot boxplots for each column in c_cols
for col_name in c_cols:
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

    # Boxplot for Fraud
    sns.boxplot(x='isFraud', y=col_name, data=sampled_data_pd, ax=axes[0])
    axes[0].set_title(f'Fraud {col_name}')

    # Boxplot for Non Fraud
    sns.boxplot(x='isFraud', y=col_name, data=sampled_data_pd, ax=axes[1])
    axes[1].set_title(f'Non Fraud {col_name}')

    plt.show()

# Select only the required columns
selected_cols = ['ProductCD', 'TransactionAmt', 'isFraud']
filtered_data = train_data.select(*selected_cols)

# Convert the selected data to Pandas for local plotting
pandas_df = filtered_data.toPandas()

# Plot the boxplot using Seaborn (assuming Seaborn is installed)
plt.figure(figsize=(10, 6))
sns.boxplot(x='ProductCD', y='TransactionAmt', data=pandas_df, hue='isFraud')
plt.title('\nProductCD vs TransactionAmt\n')
plt.show()

# Assuming 'domain_features' is a list of column names in your PySpark DataFrame
domain_features = ["P_emaildomain", "R_emaildomain"]

# Set up subplots
fig, axes = plt.subplots(2, 1, figsize=(15, 13))
fig.tight_layout(pad=15.0)
fig.suptitle('Plotting for domain features', y=0.9)
idx = 0

for i in range(2):
    if idx == len(domain_features):
        break

    f = domain_features[idx]
    idx += 1

    # Use Matplotlib's hist method for counting and plotting
    fraud_counts = (
        train_data
        .groupBy(f, 'isFraud')
        .count()
        .filter('isFraud == 1')
        .withColumnRenamed('count', 'fraud_count')
        .drop('isFraud')
    )

    non_fraud_counts = (
        train_data
        .groupBy(f)
        .count()
        .withColumnRenamed('count', 'non_fraud_count')
    )

    # Join the two DataFrames on the feature column
    counts = non_fraud_counts.join(fraud_counts, f, 'left_outer').fillna(0)

    # Convert to Pandas for plotting
    counts_pd = counts.toPandas()

    # Plotting
    counts_pd.plot(kind='bar', x=f, y=['non_fraud_count', 'fraud_count'], stacked=True, ax=axes[i])
    axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=90, ha='center')
    axes[i].legend(loc=7)
    axes[i].set_title(f + " Count Plot")

# Show the plot
plt.show()

# Count occurrences of values in the 'P_emaildomain' column
count_df = train_data.groupBy("P_emaildomain").count().toPandas()

# Create subplots
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 8))

# Plot the count using seaborn
sns.barplot(x='P_emaildomain', y='count', data=count_df, ax=axes)
axes.set_title('P_emaildomain')
axes.set_xticklabels(axes.get_xticklabels(), rotation=90)

# Show the plot
plt.show()

# Select relevant columns and group by 'P_emaildomain'
result_df = train_data.select('P_emaildomain', 'isFraud') \
    .groupBy('P_emaildomain') \
    .mean('isFraud') \
    .sort(col('avg(isFraud)').asc())

# Convert PySpark DataFrame to Pandas DataFrame for plotting
result_pd = result_df.toPandas()

# Plotting
result_pd.plot(kind='barh', x='P_emaildomain', y='avg(isFraud)', figsize=(15, 15))
plt.title('Percentage of Fraud by Purchaser email domain')
plt.show()

# Count occurrences of values in the 'P_emaildomain' column
count_df = train_data.groupBy("R_emaildomain").count().toPandas()

# Create subplots
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 8))

# Plot the count using seaborn
sns.barplot(x='R_emaildomain', y='count', data=count_df, ax=axes)
axes.set_title('R_emaildomain')
axes.set_xticklabels(axes.get_xticklabels(), rotation=90)

# Show the plot
plt.show()

# Perform the aggregation and calculation
result_df = train_data.groupBy('R_emaildomain').agg({'isFraud': 'mean'}).orderBy('avg(isFraud)')

# Convert the PySpark DataFrame to Pandas for plotting
pandas_df = result_df.toPandas()

# Plot the bar chart using Matplotlib

pandas_df.plot(kind='barh', x='R_emaildomain', y='avg(isFraud)', figsize=(15, 15))
plt.title('Percentage of Fraud by Recipient email domain')
plt.show()

from pyspark.sql import functions as F
from pyspark.sql.window import Window
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Convert TransactionAmt to log scale
train_data = train_data.withColumn("TransactionAmt", F.log("TransactionAmt"))
test_data = test_data.withColumn("TransactionAmt", F.log("TransactionAmt"))

# Filter fraud and not fraud transactions
dff_fraud = train_data.filter(train_data["isFraud"] == 1)
dff_notfraud = train_data.filter(train_data["isFraud"] == 0)

# Convert TransactionAmt to log scale for fraud and not fraud transactions
dff_fraud = dff_fraud.withColumn("TransactionAmt", F.log("TransactionAmt"))
dff_notfraud = dff_notfraud.withColumn("TransactionAmt", F.log("TransactionAmt"))

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(15, 8))

# Plot for Train data
sns.distplot(dff_notfraud.select("TransactionAmt").toPandas(), ax=axes[0], label='not fraud')
sns.distplot(dff_fraud.select("TransactionAmt").toPandas(), ax=axes[0], label='fraud')
axes[0].set_title('Log(Fraud transaction distribution) Train')
axes[0].legend()

# Plot for Test data
test_amt = np.log(test_data.select("TransactionAmt").toPandas())
sns.distplot(test_amt, ax=axes[1])
axes[1].set_title('Log(Fraud transaction distribution) Test')

plt.show()

id_columns = ['id_01','id_02','id_03','id_04','id_05','id_06','id_07','id_08','id_09','id_10','id11','id12','id_13','id_14','id_15','id_16','id_17','id_18','id_19','id_20','id_21','id_22','id_23','id_24','id_25','id_26','id_27',
                    'id_28','id_29','id_30','id_31','id_32','id_33','id_34','id_35','id_36','id_37','id_38']

from pyspark.sql.functions import col, mean
import matplotlib.pyplot as plt

# Get the list of column names that meet the criteria
idd_columns = ['id12','id_13','id_14','id_15','id_16','id_17','id_18','id_19','id_20','id_21','id_22','id_23','id_24','id_25','id_26','id_27',
                    'id_28','id_29','id_30','id_31','id_32','id_33','id_34','id_35','id_36','id_37','id_38']
for id_col in id_columns:
    grouped_data = train_data.groupBy(id_col).agg(mean("isFraud").alias("mean_isFraud"))

    sorted_data = grouped_data.sort(col("mean_isFraud").desc())

    top_10_data = sorted_data.limit(10).toPandas()


    top_10_data.plot(kind='barh', x=id_col, y='mean_isFraud', figsize=(10, 10))
    plt.title(f'Mean Fraud Rate for {id_col}')
    plt.show()

device_type_isfraud_distribution = train_data.groupBy("DeviceType", "isfraud").count()

# Convert PySpark DataFrame to Pandas DataFrame
device_type_isfraud_pandas = device_type_isfraud_distribution.toPandas()

# Plotting the bar chart
fig, ax = plt.subplots(figsize=(10, 6))
device_type_isfraud_pandas.pivot(index='DeviceType', columns='isfraud', values='count').plot(kind='bar', stacked=True, ax=ax)
plt.title("DeviceType Distribution by IsFraud")
plt.xlabel("DeviceType")
plt.ylabel("Count")
plt.legend(title="IsFraud", labels=['Not Fraud (0)', 'Fraud (1)'])
plt.show()

import matplotlib.pyplot as plt
from pyspark.sql import SparkSession

from pyspark.sql.functions import col, when


# Replace 'DeviceType' and 'isfraud' with the actual column names in your DataFrame
device_type_isfraud_distribution = train_data.groupBy("DeviceType", "isfraud").count()

# Convert PySpark DataFrame to Pandas DataFrame
device_type_isfraud_pandas = device_type_isfraud_distribution.toPandas()

# Pivot the data for plotting
pivot_df = device_type_isfraud_pandas.pivot(index='DeviceType', columns='isfraud', values='count')

# Calculate percentage of fraud and not fraud
pivot_df['PercentageFraud'] = (pivot_df[1] / (pivot_df[0] + pivot_df[1])) * 100
pivot_df['PercentageNotFraud'] = (pivot_df[0] / (pivot_df[0] + pivot_df[1])) * 100

# Plotting the bar chart
fig, ax = plt.subplots(figsize=(10, 6))
pivot_df[['PercentageNotFraud', 'PercentageFraud']].plot(kind='bar', ax=ax)
plt.title("DeviceType Distribution by IsFraud")
plt.xlabel("DeviceType")
plt.ylabel("Percentage")
plt.legend(title="IsFraud", labels=['Not Fraud (0)', 'Fraud (1)'])

# Annotate with percentage values
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy()
    ax.annotate(f'{height:.2f}%', (x + width / 2, y + height), ha='center', va='center')

plt.show()

import matplotlib.pyplot as plt

# Convert PySpark DataFrame to Pandas DataFrame for local plotting
device_counts_pandas = train_data.groupBy("DeviceInfo").count().toPandas()

# Check if data is present
print(device_counts_pandas)

# Select the top 25 high count device types
top_25_devices = device_counts_pandas.nlargest(25, 'count')

# Plotting the bar chart using Matplotlib for the top 25 devices
plt.figure(figsize=(14, 8))
top_25_devices.plot(kind='bar', x='DeviceInfo', y='count', color='skyblue')
plt.title('Top 25 DeviceInfo Distribution')
plt.xlabel('DeviceInfo')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()