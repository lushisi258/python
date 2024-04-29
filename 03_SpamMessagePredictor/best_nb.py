from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from joblib import dump
import pandas as pd


# 读取数据
df = pd.read_csv("C:/Code/data/sms_pub_preprocessed2.csv")

# 提取特征数据和目标数据
X = df['msg_new']
y = df['label']

# 使用空字符串填充缺失值
X = X.fillna('')

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 定义Pipeline
pipe = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('nb', MultinomialNB(alpha=0.3, fit_prior=True))
])

# 使用pipeline进行训练
pipe.fit(X_train, y_train)

# 保存模型
dump(pipe, "C:/Code/python/03_SpamMessagePredictor/best_nb.joblib")

# 输出模型的准确率
print('Accuracy: ', pipe.score(X_test, y_test))