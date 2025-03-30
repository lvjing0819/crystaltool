
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
df = pd.read_csv("/Volumes/Elements/跨境电商/TIKTOK/账务/2024/全部 订单-2025-03-26-19_32.csv")
save_path = r"/Volumes/Elements/跨境电商/TIKTOK/账务/2024/订单饼图"
# df2 = pd.read_excel("/Volumes/Elements/跨境电商/TIKTOK/账务/2503/income_20250324070818.xlsx",sheet_name="Order details")
# df1['Order ID'] = df1['Order ID'].astype(str)
# df1['SKU ID'] = df1['SKU ID'].astype(str)

# df2['Order/adjustment ID  '] = df2['Order/adjustment ID  '].astype(str)
# df2['SKU ID'] = df2['SKU ID'].astype(str)
# print(df1.shape)
# print(df2.shape)
# df = pd.merge(
#     df1, df2,
#     left_on=['Order ID', 'SKU ID'],  # df1的列
#     right_on=['Order/adjustment ID  ', 'SKU ID'],  # df2的列
#     how='left'  # 使用 inner join 只保留匹配的行
# )
print(f"** 一共有{df["Order ID"].nunique()}单")
print(f"** 一共有{df["Order ID"].shape[0]}行")
#df['Total settlement amount'] = pd.to_numeric(df['Total settlement amount'], errors='coerce')
df["Created Time"] = pd.to_datetime(df["Created Time"], errors="coerce")  # 转换为日期格式
df["Year"] = df["Created Time"].dt.year   # 提取年份
df["Month"] = df["Created Time"].dt.month # 提取月份
df["Year-Month"] = df["Created Time"].dt.strftime("%Y-%m")
df_month_group = df.groupby("Year-Month")
def billdetail(df):
    print("$以下为Seller SKU总揽")
    df_group = df.groupby("Seller SKU")["Quantity"].sum()
    for i,count in df_group.items():
        print(f"***Seller SKU : {i} ；数量 {count}" )
        # 2.有多少个订单是多产品的（不同SKU/单独SKU多个）
    df_overseas = df[df["Delivery Option"]!="全球标准运输服务"]

    print(f"**海外仓运输 一共有{df_overseas["Order ID"].nunique()}单")
    df_global = df[df["Delivery Option"]=="全球标准运输服务"]
    print(f"**国内仓库运输 一共有{df_global["Order ID"].nunique()}单")
def canceldtail(df):
    print("$以下为取消总览")
    df_group = df.groupby("Cancel Reason")["Order ID"].count()
    for i,count in df_group.items():
        print(f"***cancel reason : {i} ；数量 {count}" )




# === 定义通用的订单状态分类函数 ===

def classify_order(row):
    """ 根据订单状态、取消原因等信息，给订单打标签 """
    if row["Order Status"] == "Canceled" and row["Cancel By"] == "System" and row["Cancel Reason"] == "Customer overdue to pay":
        return "未付款取消"
    elif row["Order Status"] == "Canceled" and row["Cancel By"] in ["User", "Seller"]:
        return "已付款后取消"
    elif row["Order Status"] == "Canceled" and row["Cancel Reason"] in ["Package damaged","Package lost"]:
        return "物流丢失/损坏"
    elif row["Order Status"] == "Canceled" and row["Cancel Reason"] in ["Package delivery failed", "Package rejected"]:
        return "拒收订单"
    elif row["Order Status"] == "To ship":
        return "刚出单"
    elif row["Order Status"] == "Shipped" and row["Order Substatus"] == "In transit":
        return "运输中"
    elif row["Order Status"] == "Shipped" and row["Order Substatus"] == "Delivered":
        return "已收到未满7天"
    elif row["Order Status"] == "Completed" and row["Order Substatus"] == "Completed" and pd.isna(row["Cancelation/Return Type"]):
        return "已收到满7天"
    elif row["Order Status"] == "Completed" and row["Order Substatus"] == "Completed" and row["Cancelation/Return Type"] == "Return/Refund":
        return "退款退货"
    else:
        return "其他"
def affiliate_orders(row):
    if row["Order Amount"] == "MYR 0.00":
        return "达人样品"
    else:
        return "其他"
    
def order_plt(df,name,year_month):
    # 指定字体路径
    # font_path = "C:/Windows/Fonts/simhei.ttf"  # Windows 用户
    #font_path = "/System/Library/Fonts/Supplemental/Songti.ttc"  # macOS 用户
    # font_path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"  # Linux 用户

    #ont_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = 'Arial Unicode MS' 

    # 统计各类别订单数量
    order_counts = df[name].value_counts()
    # 画饼图
    plt.figure(figsize=(10, 6))
    wedges, texts, autotexts = plt.pie(
        order_counts, 
        labels=None,  # 不在饼图上显示标签
        autopct="%1.1f%%", 
        startangle=140
    )

    # 添加图例
    plt.legend(wedges, order_counts.index, title="订单类型", loc="lower left")
    title = f"{year_month}_不同订单类型的占比.png"
    plt.title(title)
    # 生成文件名（确保是字符串）
   

    # 组合完整路径
    file_path = os.path.join(save_path, title)
        # **正确方式：保存图像**
    plt.savefig(file_path, dpi=300, bbox_inches='tight')  # 确保传递的是字符串路径
    plt.show()
    

# === 定义一个通用的订单统计和展示函数 ===
def process_order_category(df, category_name):
    # === 在 DataFrame 中应用该分类函数 ===
    
    """ 统计某个类别订单，并打印相关信息 """
    df_filtered = df[df["Order Category"] == category_name]
    
    # 统计订单数量
    order_count = df_filtered["Order ID"].nunique()
    row_count = df_filtered.shape[0]
    
    print(f"#####################################     {category_name}   #############################")
    print(f"{category_name} 订单数量 ： {order_count} 单")
    print(f"** 一共有 {row_count} 行数据")
    
    # 账单明细
    billdetail(df_filtered)
    if category_name == "已付款后取消":
        canceldtail(df_filtered)

    return df_filtered  # 返回筛选后的数据
for year_month, df_month_group_data in df_month_group:
    df_month_group_data["Order Category"] = df_month_group_data.apply(classify_order, axis=1)
# === 在 DataFrame 中应用该分类函数 ===
    df_month_group_data["Affiliate Order"] = df_month_group_data.apply(affiliate_orders, axis=1)
    order_plt(df_month_group_data,"Order Category",year_month)
    
    df_blank =df_month_group_data[(df_month_group_data["Order Category"] =="其他")| pd.isna(df_month_group_data["Order Category"]) ]
    print("------------------------------",df_blank)
    print(df_blank["Order Substatus"].to_list())
# === 遍历不同的订单类别，自动处理 ===
    categories = ["未付款取消", "已付款后取消", "物流物流丢失/损坏", "拒收订单", "刚出单", "运输中", "已收到未满7天", "已收到满7天", "退款退货"]
    df_filtered_dict = {cat: process_order_category(df_month_group_data, cat) for cat in categories}

# === 处理达人样品子类别 ===
    df_affliate = df_month_group_data[df_month_group_data["Affiliate Order"]=="达人样品"]

    df_affliate_cancelbyseller = df_affliate[df_affliate["Cancel By"] == "Seller"]
    df_affliate_cancelbysys = df_affliate[df_affliate["Cancel By"] == "System"]
    print(f"#####################################     达人样品   #############################")
    print(f"达人样品订单 ： {df_affliate['Order ID'].nunique()} 单")
    print(f"达人样品被商家取消订单 ： {df_affliate_cancelbyseller['Order ID'].nunique()} 单")
    print(f"达人样品被系统取消订单 ： {df_affliate_cancelbysys['Order ID'].nunique()} 单")

    billdetail(df_affliate) 