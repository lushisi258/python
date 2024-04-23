import pandas as pd
from joblib import dump
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

time_start = time.time()

# 读取数据
df = pd.read_csv('C:/Code/python/03_SpamMessagePredictor/sms_pub_preprocessed2.csv')

# 提取特征数据和目标数据
X = df['msg_new']
y = df['label']

# 使用空字符串填充缺失值
X = X.fillna('')

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 创建一个Pipeline对象
pipe = Pipeline([
    ('tfidf', TfidfVectorizer()),  # 第一步是计算TF-IDF值
    ('svc', SVC(kernel='linear', probability=True))  # 第二步是SVC模型
])

# 使用训练集的特征和目标来训练Pipeline
pipe.fit(X_train, y_train)

# 保存你的Pipeline
dump(pipe, 'pipeline.joblib')

time_fit = time.time()
cost_time_fit = time_fit - time_start
cost_hour_fit = (time_fit - time_start) // 3600
cost_minute_fit = (time_fit - time_start - cost_hour_fit * 3600) // 60
cost_second_fit = time_fit - time_start - cost_hour_fit * 3600 - cost_minute_fit * 60
print('cost time of fit: %d h %d m %d s' % (cost_hour_fit, cost_minute_fit, cost_second_fit))

# 计算Pipeline在测试集上的准确率
accuracy = pipe.score(X_test, y_test)
print('Accuracy:', accuracy)

time_end = time.time()
cost_time = time_end - time_start
cost_hour = (time_end - time_start) // 3600
cost_minute = (time_end - time_start - cost_hour * 3600) // 60
cost_second = time_end - time_start - cost_hour * 3600 - cost_minute * 60
print('cost time: %d h %d m %d s' % (cost_hour, cost_minute, cost_second))