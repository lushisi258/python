'''
predict的实现：
预测短信短信的类别和每个类别的概率
    参数: message: 经过jieba分词的短信
    返回值: 
        label: 整数类型，短信的类别，0 代表正常，1 代表恶意
        prob: 一个列表，包含两个元素，分别代表短信是正常和恶意的概率
'''
import re
import string
import joblib
from sklearn.pipeline import Pipeline

# 加载模型
pipeline = joblib.load('C:/Code/python/03_SpamMessagePredictor/best_nb.joblib')
# 停用词表路径
stopwords_path = 'C:/Code/python/03_SpamMessagePredictor/stopwords.txt'
# 定义一个包含中文标点符号的字符串
chinese_punctuation = '！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。'


# 读取停用词库
def read_stopwords(stopwords_path):
    """
    读取停用词库
    :param stopwords_path: 停用词库的路径
    :return: 停用词列表
    """
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = f.read()
    stopwords = stopwords.splitlines()
    return stopwords

# 删除停用词
def remove_stopwords(words, stopwords_set):
    return [word for word in words if word not in stopwords_set]

# 数据预处理
def preprocess_message(message):
    # 清洗数据
    message = re.sub('[{}{}]'.format(string.punctuation, chinese_punctuation), ' ', message)
    # 读取停用词库
    stopwords_set = read_stopwords(stopwords_path)
    # 删除停用词
    message = ' '.join([word for word in message.split() if word not in stopwords_set])
    return message

# 预测实现函数
def predict(message):
    # 清洗数据
    message = preprocess_message(message)
    # 判断是否是垃圾短信
    label = pipeline.predict([message])[0]
    # 判断概率
    proba = list(pipeline.predict_proba([message])[0])
    
    return label, proba

label, proba = predict('医生 拿 着 我 的 报告单 说 ： 幸亏 你 来 的 早 啊')
print(label, proba)