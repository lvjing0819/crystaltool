import pandas as pd
import os
import re
file=r'/Volumes/Elements/跨境电商/TIKTOK/面单/250330'
file_list=os.listdir(file)
country_dict = {"THB":"泰国","MYR":"马来西亚"}
filter_files=[os.path.join(file, f) for f in file_list if not f.startswith("._") and f.endswith(".csv")]
for f in filter_files:
    print(f)
    df= pd.read_csv(f,header=0)
    #df = df.drop(0)
    df["Quantity"] =  df["Quantity"].astype("int")
    print("=========================以下为基本信息======================")
    
    # 需要知道
    # 正则表达式：匹配 YYYY-MM-DD 格式的日期
    pattern = r"\d{4}-\d{2}-\d{2}"
    # 查找匹配的日期
    match = re.search(pattern, f)
    # 如果找到匹配的日期，提取并打印
    if match:
        date = match.group()  # 获取匹配的日期
        print("提取的日期:", date)
    else:
        print("未找到日期")
    print("=========================以下为订单信息======================")
    # 1.今天每个站点有多少订单
    ## 统计order列的非重复计数
    print("$该站点为：",f)
    unique_count=df["Order ID"].nunique()
    print("$一共产生订单：",unique_count)
    
    # 2.有多少个订单是多产品的（不同SKU/单独SKU多个）
    df_overseas = df[df["Delivery Option"]!="全球标准运输服务"]

    print(f"**海外仓运输 一共有{df_overseas["Order ID"].nunique()}单")
    df_global = df[df["Delivery Option"]=="全球标准运输服务"]
    print(f"**国内仓库运输 一共有{df_global["Order ID"].nunique()}单")
    ## 2.1统计不同sku组成的ID
    print(f"以下为国内仓库订单明细")
    dupicate_counts=df_global["Order ID"].value_counts()
    dupicate_count_filter=dupicate_counts[dupicate_counts > 1]
    dupicate_count_filter_index = dupicate_count_filter.index
    print("$订单中含多个不同商品组合的订单有:",len(dupicate_count_filter_index),"单")

    for Order_Id in dupicate_count_filter_index:
        print(f"***订单编号 '{Order_Id}' 对应的 'Seller_sku' 列的值:",df_global[df_global['Order ID'] == Order_Id]['Seller SKU'].tolist())
    ## 2.2统计相同sku下多单的ID
    
    morethanone_count = df_global[df_global["Quantity"]>=2].reset_index(drop=True)
    print("$订单中含单个商品数量>2的有：",len(morethanone_count),"单")
    for i in range(len(morethanone_count)):
        print(f"***订单编号 : 【 {morethanone_count.iloc[i,0]}】   SKU : 【{morethanone_count.iloc[i,6]} 】  数量 ：【{morethanone_count.iloc[i,9]}】")
    
    # 2.3 同时包含上述2种情况
    result = df_global[(df_global["Order ID"].isin(dupicate_count_filter_index))& (df_global["Quantity"]>=2)]
    print("$订单中包含多个商品组合同时出现单个商品数量>2的有：",len(result),"单")
    if len(result) != 0:
        for i in  result.index:
            print(f"***订单编号为 : 【{df_global.iloc[i,0]}】 , 包含的Seller SKU为：【{df_global.iloc[i,6]}】 ，数量为 ： 【{df_global.iloc[i,9]}】" )
    # 4.每个sku出了多少数量
    # groupby seller sku
    print("$以下为Seller SKU总揽")
    df_group = df_global.groupby("Seller SKU")["Quantity"].sum()
    for i,count in df_group.items():
        print(f"***Seller SKU : {i} ；数量 {count}" )


    

    # 4.多个站点归总
    # 统一显示
            

