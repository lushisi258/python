import pandas as pd
import re
import string

# 加载数据
df = pd.read_csv("C:/Code/data/sms_pub.csv")

# 定义一个包含中文标点符号的字符串
chinese_punctuation = '！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。'

# 清洗数据
df['msg_new'] = df['msg_new'].apply(lambda x: re.sub('[{}{}]'.format(string.punctuation, chinese_punctuation), ' ', x))

# 加载停用词表
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    stop_words = f.read().split('\n')

# 删除停用词
df['msg_new'] = df['msg_new'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

# 保存预处理后的数据
df.to_csv('sms_pub_preprocessed2.csv', index=False)