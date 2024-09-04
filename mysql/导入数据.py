import pandas as pd
from sqlalchemy import create_engine

# 读取Excel文件
df = pd.read_excel(r"C:\Users\17662\Desktop\软件实践2\数据\customer.xlsx")

# 创建数据库引擎
# 替换username, password, host, port, database_name为你的数据库信息
engine = create_engine('mysql+pymysql://root:5457hzcx@localhost:3306/软件实践')

# 将数据导入数据库
df.to_sql('customer', con=engine, index=False, if_exists='append')