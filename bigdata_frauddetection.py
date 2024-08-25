# -*- coding: utf-8 -*-
"""BigData_FraudDetection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GBwBNLveiBjI7UpLMKwG2P5Eq2DxuNf9
"""

!pip install pyspark

!pip install sparkxgb

from google.colab import drive
drive.mount('/content/drive')

from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.functions import col,sum,count,isnull
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from xgboost.spark import SparkXGBClassifier
from pyspark.ml.classification import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# Create a Spark session
spark = SparkSession.builder.appName("FraudDetection").getOrCreate()
# Check if a SparkContext already exists
try:
    sc = SparkContext.getOrCreate()
    print("Using existing SparkContext")
except ValueError:
    # If not, create a new SparkContext
    sc = SparkContext("local", "FraudDetection")
    print("Created new SparkContext")

# Print information about the SparkContext
print("SparkContext version:", sc.version)
print("SparkContext master:", sc.master)
print("SparkContext appName:", sc.appName)

# Specify the file paths
train_trans_path = '/content/drive/MyDrive/Colab-Notebooks/CloudComputing/Project/ieee-fraud-detection/train_transaction.csv'
train_identity_path = '/content/drive/MyDrive/Colab-Notebooks/CloudComputing/Project/ieee-fraud-detection/train_identity.csv'
test_trans_path = '/content/drive/MyDrive/Colab-Notebooks/CloudComputing/Project/ieee-fraud-detection/test_transaction.csv'
test_identity_path = '/content/drive/MyDrive/Colab-Notebooks/CloudComputing/Project/ieee-fraud-detection/test_identity.csv'

# Parallelize the loading of data using text file method
rdd_train_trans = spark.sparkContext.textFile(train_trans_path)
rdd_train_identity = spark.sparkContext.textFile(train_identity_path)
rdd_test_trans = spark.sparkContext.textFile(test_trans_path)
rdd_test_identity = spark.sparkContext.textFile(test_identity_path)

# Convert RDDs to DataFrames
train_trans = spark.read.csv(rdd_train_trans, header=True, inferSchema=True)
train_identity = spark.read.csv(rdd_train_identity, header=True, inferSchema=True)
test_trans = spark.read.csv(rdd_test_trans, header=True, inferSchema=True)
test_identity = spark.read.csv(rdd_test_identity, header=True, inferSchema=True)

# Join Train_Trans and Train_Identity
train_data = train_trans.join(train_identity, on='TransactionID', how='left')
# Join test_trans and test_identity
test_data = test_trans.join(test_identity, on='TransactionID', how='left')

# Show the loaded DataFrames
train_data.show()
#test_data.show()

train_data.printSchema

# Get the number of partitions in the DataFrame
num_partitions_train = train_data.rdd.getNumPartitions()
num_partitions_test = test_data.rdd.getNumPartitions()
# Show the partition distribution information
print(f"Number of partitions in train: {num_partitions_train}")
print(f"Number of partitions in test: {num_partitions_test}")

# Collect data in each partition and print partition sizes(no of rows or element in each partitions)
partition_sizes_train = train_data.rdd.glom().map(len).collect()
partition_sizes_test = test_data.rdd.glom().map(len).collect()
print("Partition Sizes of train:", partition_sizes_train)
print("Partition Sizes of test:", partition_sizes_test)

print((train_data.count()))
print((test_data.count()))

#we have got these v feature which not needed after during the eda and corelation analysis
not_chosen_v_fetaures = ['V2', 'V5', 'V7', 'V9', 'V10', 'V12', 'V15', 'V16', 'V17', 'V19', 'V21', 'V22', 'V24', 'V25', 'V28', 'V29', 'V31', 'V32', 'V33', 'V34', 'V35', 'V38', 'V39', 'V42', 'V43', 'V45', 'V46', 'V49', 'V50', 'V51', 'V53', 'V57', 'V58', 'V60', 'V61', 'V63', 'V64', 'V66', 'V69', 'V71', 'V72', 'V73', 'V74', 'V75', 'V77', 'V79', 'V83', 'V84', 'V85', 'V87', 'V90', 'V92', 'V93', 'V94', 'V95', 'V96', 'V97', 'V100', 'V101', 'V102', 'V103', 'V105', 'V106', 'V110', 'V112', 'V113', 'V116', 'V119', 'V122', 'V125', 'V126', 'V128', 'V132', 'V133', 'V134', 'V135', 'V137', 'V140', 'V141', 'V143', 'V144', 'V145', 'V146', 'V148', 'V149', 'V150', 'V151', 'V152', 'V153', 'V154', 'V155', 'V156', 'V158', 'V159', 'V161', 'V163', 'V164', 'V167', 'V168', 'V170', 'V172', 'V177', 'V178', 'V179', 'V181', 'V182', 'V184', 'V186', 'V189', 'V190', 'V191', 'V192', 'V193', 'V194', 'V196', 'V197', 'V199', 'V200', 'V201', 'V202', 'V204', 'V206', 'V208', 'V211', 'V212', 'V213', 'V214', 'V217', 'V218', 'V219', 'V222', 'V224', 'V225', 'V226', 'V227', 'V228', 'V229', 'V231', 'V232', 'V233', 'V236', 'V237', 'V239', 'V242', 'V243', 'V244', 'V245', 'V246', 'V247', 'V248', 'V249', 'V251', 'V253', 'V254', 'V255', 'V259', 'V261', 'V266', 'V267', 'V269', 'V270', 'V272', 'V273', 'V275', 'V276', 'V278', 'V279', 'V280', 'V287', 'V288', 'V290', 'V293', 'V294', 'V295', 'V298', 'V299', 'V300', 'V302', 'V304', 'V306', 'V308', 'V311', 'V313', 'V316', 'V317', 'V318', 'V319', 'V321', 'V322', 'V323', 'V324', 'V327', 'V329', 'V330', 'V331', 'V333', 'V334', 'V337']

# Drop columns from 'train_data'
train_data = train_data.drop(*not_chosen_v_fetaures)

# Drop columns from 'test_data'
test_data = test_data.drop(*not_chosen_v_fetaures)

num_columns_train = len(train_data.columns)
num_columns_test = len(test_data.columns)
print(num_columns_train)#236
print(num_columns_test)#236

# Get all column names except the label column
#all_columns = train_data.columns
#label_column = "isFraud"
#feature_cols = [col for col in all_columns if col != label_column]

# Create a StringIndexer for the categorical column
# Label Encoding of categorical variables  without any .fit or .transform
input_col= ['ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', \
            'card6', 'P_emaildomain', 'R_emaildomain', 'M1', 'M2', \
            'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', \
            'DeviceType', 'DeviceInfo']
output_col=['cat_ProductCD', 'cat_card1', 'cat_card2', 'cat_card3', 'cat_card4', 'cat_card5', \
            'cat_card6',  'cat_P_emaildomain', 'cat_R_emaildomain', 'cat_M1', 'cat_M2', \
            'cat_M3', 'cat_M4', 'cat_M5', 'cat_M6', 'cat_M7', 'cat_M8', 'cat_M9', \
            'cat_DeviceType', 'cat_DeviceInfo']
#String_cat_Indexer = StringIndexer(inputCols=input_col,outputCols=output_col, handleInvalid='keep')
train_data = StringIndexer(inputCols=input_col,outputCols=output_col, handleInvalid='keep').fit(train_data).transform(train_data)
test_data = StringIndexer(inputCols=input_col,outputCols=output_col, handleInvalid='keep').fit(test_data).transform(test_data)

train_data.show(2)

train_data = train_data.drop('ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', \
            'card6', 'P_emaildomain', 'R_emaildomain', 'M1', 'M2', \
            'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', \
            'DeviceType', 'DeviceInfo')
test_data = test_data.drop('ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', \
            'card6', 'P_emaildomain', 'R_emaildomain', 'M1', 'M2', \
            'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', \
            'DeviceType', 'DeviceInfo')

train_data = train_data.drop('TransactionID')
test_data = test_data.drop('TransactionID')

#handle the missing value
train_df = train_data.fillna(-999)
test_df = test_data.fillna(-999)

all_columns = train_df.columns
label_column = "isFraud"
feature_cols = [col for col in all_columns if col != label_column]

#Assemble all the feautures with VectorAssembler
vector_assembler_1 = VectorAssembler(inputCols=feature_cols, outputCol="features")

# Modeling using RandomForestClassifier
dt_model = RandomForestClassifier(labelCol="isFraud", featuresCol="features")
# Create a pipeline
pipeline = Pipeline(stages=[vector_assembler_1, dt_model])
# Fit the pipeline model
final_pipeline = pipeline.fit(train_df)
# Predict on test data
test_predictions_from_pipeline = final_pipeline.transform(test_df)

# Define the evaluator for random forest
evaluator1 = BinaryClassificationEvaluator(labelCol="isFraud", metricName="areaUnderROC")

# Evaluate the model
area_under_curve = evaluator1.evaluate(test_predictions_from_pipeline)
print(f"Area under ROC curve for Random forest: {area_under_curve}")

# Convert PySpark RDD to a list for roc_curve
labels_and_probs = test_predictions_from_pipeline.select("isFraud", "probability").rdd.map(lambda row: (float(row["isFraud"]), float(row["probability"][1]))).collect()

# Extract labels and probabilities as lists
labels, probs = zip(*labels_and_probs)

# Get the ROC curve
fpr, tpr, thresholds = roc_curve(labels, probs)

# Compute AUC (Area Under the Curve)
roc_auc = auc(fpr, tpr)

# Plot the ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve for RandomForestClassifier')
plt.legend(loc="lower right")
plt.show()

# Modeling using SparkXGBClassifier
sparkXgboostclassifier = SparkXGBClassifier(
  features_col='features',
  label_col='isFraud',
  num_workers=1,
  device="cuda",
  use_gpu=True,
)

# Create a pipeline
pipeline = Pipeline(stages=[vector_assembler_1, sparkXgboostclassifier])

# Define the evaluator
evaluator = BinaryClassificationEvaluator(labelCol="isFraud", metricName="areaUnderROC")


# Set up the parameter grid for hyperparameter tuning
param_grid = ParamGridBuilder() \
  .addGrid(sparkXgboostclassifier.learning_rate, [0.0, 0.01, 0.1]) \
  .addGrid(sparkXgboostclassifier.max_depth, [2, 3, 5]) \
  .build()



# Create a CrossValidator with the XGBoost pipeline, parameter grid, and evaluator
cross_validator = CrossValidator(
    estimator=pipeline,
    estimatorParamMaps=param_grid,
    evaluator=evaluator,
    numFolds=3  # Number of folds in cross-validation
)


# Train the model using estimator
cv_model = cross_validator.fit(train_df)

# Make predictions on the test set using transformer
predict_df = cv_model.transform(test_df)


# Evaluate the model
area_under_curve = evaluator.evaluate(predict_df)
print(f"Area under ROC curve: {area_under_curve}")

# Get the best model from the cross-validation
bestModel = cv_model.bestModel

# Use the best model for making predictions on the test set
predictions = bestModel.transform(test_df)

# Get the best set of parameters
bestParams = bestModel.stages[-1].extractParamMap()

# Print or analyze the best set of parameters
print("Best parameters:")
for param, value in bestParams.items():
    print(f"{param.name}: {value}")

# Evaluate the model Xgboot
area_under_curve = evaluator.evaluate(predictions)
print(f"Area under ROC curve: {area_under_curve}")

predict_df.show(3)

#predict_df.filter.select('isFraud','prediction').show()
predict_df.select("isFraud", "prediction", "probability").show(5)

# Convert PySpark RDD to a list for roc_curve
labels_and_probs = predict_df.select("isFraud", "probability").rdd.map(lambda row: (float(row["isFraud"]), float(row["probability"][1]))).collect()

# Extract labels and probabilities as lists
labels, probs = zip(*labels_and_probs)

# Get the ROC curve
fpr, tpr, thresholds = roc_curve(labels, probs)

# Compute AUC (Area Under the Curve)
roc_auc = auc(fpr, tpr)

# Plot the ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve for XgBoot')
plt.legend(loc="lower right")
plt.show()