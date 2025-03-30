import pandas as pd
df1 = pd.read_csv("/Volumes/Elements/跨境电商/TIKTOK/账务/2503/全部 订单-2025-03-24-13_57.csv")
df2 = pd.read_excel("/Volumes/Elements/跨境电商/TIKTOK/账务/2503/income_20250324070818.xlsx",sheet_name="Order details")
df1['Order ID'] = df1['Order ID'].astype(str)
df1['SKU ID'] = df1['SKU ID'].astype(str)

df2['Order/adjustment ID  '] = df2['Order/adjustment ID  '].astype(str)
df2['SKU ID'] = df2['SKU ID'].astype(str)
print(df1.shape)
print(df2.shape)
df = pd.merge(
    df1, df2,
    left_on=['Order ID', 'SKU ID'],  # df1的列
    right_on=['Order/adjustment ID  ', 'SKU ID'],  # df2的列
    how='left'  # 使用 inner join 只保留匹配的行
)
print(f"** 一共有{df["Order ID"].nunique()}单")
print(f"** 一共有{df["Order ID"].shape[0]}行")
df['Total settlement amount'] = pd.to_numeric(df['Total settlement amount'], errors='coerce')
df["Created Time"] = pd.to_datetime(df["Created Time"], errors="coerce")  # 转换为日期格式
df["Year"] = df["Created Time"].dt.year   # 提取年份
df["Month"] = df["Created Time"].dt.month # 提取月份
df["Year-Month"] = df["Created Time"].dt.strftime("%Y-%m")
df_month_group = df.groupby("Year-Month")
def billdetail(df):
    print("$以下为Seller SKU总揽")
    df_group = df.groupby("Seller SKU")["Quantity_x"].sum()
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


for year_month, df_month_group_data in df_month_group:
    print(f"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     月份:{year_month}   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ")
    print("#####################################     未付款取消订单   #############################")
    df_canceled_payoverdue = df_month_group_data[
   ((df_month_group_data["Order Status"] == "Canceled") & (df_month_group_data["Cancel By"] == "System") & (df_month_group_data["Cancel Reason"] == "Customer overdue to pay"))# 用户超时未付款
]
    print(f"因超时未付款而取消的订单 ： {df_canceled_payoverdue["Order ID"].nunique()} 单")
    print(f"** 一共有{df_canceled_payoverdue["Order ID"].shape[0]}行")
    print(df_canceled_payoverdue.columns)
    billdetail(df_canceled_payoverdue)
    

    print("#####################################     已付款后取消订单   #############################")
# 在国内就被取消的订单==》过滤订单状态为 "Canceled" 且结算金额为 0（internet bank）或 NaN（COD 订单）
    df_canceled = df_month_group_data[
   ((df_month_group_data["Order Status"] == "Canceled") & ((df_month_group_data["Cancel By"] == "User") | (df_month_group_data["Cancel By"] == "Seller")) ) # 用户或者是我们自己取消的## internetbank 结算账单为0，COD结算账单为 NAN
]
    print(f"被买家或者卖家取消的订单 ： {df_canceled["Order ID"].nunique()} 单----可能包含海外被取消但是未达结算日期的订单")
    print(f"** 一共有{df_canceled["Order ID"].shape[0]}行")
    billdetail(df_canceled)
    canceldtail(df_canceled)

#& ((df["Cancel By"] == "User") | (df["Cancel By"] == "Seller")) ) 
    df_canceled_by_sellers = df_canceled[df_canceled["Cancel By"] == "Seller"]
    print(f"被买家取消的订单 ： {df_canceled_by_sellers["Order ID"].nunique()} 单----可能包含海外被取消但是未达结算日期的订单")
    df_canceled_by_users = df_canceled[df_canceled["Cancel By"] == "User"]
    print(f"被卖家取消的订单 ： {df_canceled_by_users["Order ID"].nunique()} 单----可能包含海外被取消但是未达结算日期的订单")

    df_canceled_from_overseas = df_month_group_data[
   ( (df_month_group_data["Order Status"] == "Canceled") &   ((df_month_group_data["Cancel By"] == "User") | (df_month_group_data["Cancel By"] == "Seller")) ) &# 用户或者是我们自己取消的
    ((df_month_group_data["Total settlement amount"] != 0) & (~pd.isna(df_month_group_data["Total settlement amount"]))) ## 订单结算账单🈶数值且不为0 （>0有赔付，<0无赔付） 也不是NAN
]
    print(f"其中从国外取消的订单（已达结算日期） ： {df_canceled_from_overseas["Order ID"].nunique()} 单")
    billdetail(df_canceled_from_overseas)
## 有赔付
    df_canceled_from_overseas_with_pay = df_canceled_from_overseas[df_canceled_from_overseas["Total settlement amount"]>0]
    print(f"*****其中有赔付 ： {df_canceled_from_overseas_with_pay["Order ID"].nunique()} 单")
## 无赔付
    df_canceled_from_overseas_without_pay = df_canceled_from_overseas[df_canceled_from_overseas["Total settlement amount"]<0]

    print(f"*****其中无赔付 ： {df_canceled_from_overseas_without_pay["Order ID"].nunique()} 单")
    billdetail(df_canceled_payoverdue)
    print("#####################################      丢失订单     #############################")
    df_lost_orders = df_month_group_data[(df_month_group_data["Order Status"] == "Canceled") &(df_month_group_data["Cancel Reason"] == "Package lost") &(df_month_group_data["Cancel By"] == "System")]
    print(f"因物流丢失的订单有 ： {df_lost_orders["Order ID"].nunique()} 单")
    print(f"** 一共有{df_lost_orders["Order ID"].shape[0]}行")
    print(df_lost_orders["Order ID"])
    billdetail(df_lost_orders)
 ## 有赔付
    df_lost_orders_with_pay = df_lost_orders[df_lost_orders["Total settlement amount"]>0]
    print(f"*****其中有赔付 ： {df_lost_orders_with_pay["Order ID"].nunique()} 单")
## 无赔付
    df_lost_orders_without_pay = df_lost_orders[df_lost_orders["Total settlement amount"]<0]

    print(f"*****其中无赔付 ： {df_lost_orders_without_pay["Order ID"].nunique()} 单")
    print("#####################################      拒收订单      #############################")
    df["Total settlement amount"] = pd.to_numeric(df_month_group_data["Total settlement amount"], errors="coerce")

    df_reject_orders = df_month_group_data[(df_month_group_data["Order Status"] == "Canceled") &((df_month_group_data["Cancel Reason"] == "Package delivery failed")| (df_month_group_data["Cancel Reason"] == "Package rejected"))&(df_month_group_data["Cancel By"] == "System")]
    print(f"因拒收的订单有 ： {df_reject_orders["Order ID"].nunique()} 单")
    print(f"** 一共有{df_reject_orders["Order ID"].shape[0]}行")

#df_reject_orders["Total settlement amount"] = df_reject_orders["Total settlement amount"].fillna(0)
#print(df_reject_orders["Total settlement amount"])
    billdetail(df_reject_orders)

 ## 有赔付
    df_reject_orders_with_pay = df_reject_orders[df_reject_orders["Total settlement amount"] > 0]
    print(f"*****其中有赔付 ： {df_reject_orders_with_pay["Order ID"].nunique()} 单")
## 无赔付
    df_reject_orders_without_pay = df_reject_orders[df_reject_orders["Total settlement amount"] < 0]

    print(f"*****其中无赔付 ： {df_reject_orders_without_pay["Order ID"].nunique()} 单")
    print("#####################################     刚出单   + #############################")

    df_toship_orders = df_month_group_data[df_month_group_data["Order Status"] == "To ship"]
    print(f"刚出的订单有 ： {df_toship_orders["Order ID"].nunique()} 单")
    print(f"** 一共有{df_toship_orders["Order ID"].shape[0]}行")
    billdetail(df_toship_orders)
    print("#####################################     运输中   #############################")

    df_shipping_orders = df_month_group_data[(df_month_group_data["Order Status"] == "Shipped")&(df_month_group_data["Order Substatus"] == "In transit")]
    print(f"运输中的订单有 ： {df_shipping_orders["Order ID"].nunique()} 单")
    print(f"** 一共有{df_shipping_orders["Order ID"].shape[0]}行")
    billdetail(df_shipping_orders)
    print("#####################################     已收到，未达7天无理由   #############################")

    df_delivered_orders = df_month_group_data[(df_month_group_data["Order Status"] == "Shipped")&(df_month_group_data["Order Substatus"] == "Delivered")]
    print(f"运输中的订单有 ： {df_delivered_orders["Order ID"].nunique()} 单")
    print(f"** 一共有{df_delivered_orders["Order ID"].shape[0]}行")
    billdetail(df_delivered_orders)
    print("#####################################     已收到，到达7天无理由   #############################")

    df_completed_orders = df_month_group_data[(df_month_group_data["Order Status"] == "Completed")&(df_month_group_data["Order Substatus"] == "Completed")&(pd.isna(df_month_group_data["Cancelation/Return Type"]))]
    print(f"运输中的订单有 ： {df_completed_orders["Order ID"].nunique()} 单")
    print(f"** 一共有{df_completed_orders["Order ID"].shape[0]}行")
    billdetail(df_completed_orders)

    print("#####################################  退款退货  #############################")
    df_returnrefund_orders = df_month_group_data[(df_month_group_data["Order Status"] == "Completed")&(df_month_group_data["Order Substatus"] == "Completed")&(df_month_group_data["Cancelation/Return Type"] == "Return/Refund")]
    print(f"退货/退款订单有 ： {df_returnrefund_orders["Order ID"].nunique()} 单")
    billdetail(df_returnrefund_orders)
    print(f"** 一共有{df_returnrefund_orders["Order ID"].shape[0]}行")
    print("#####################################   达人样品  #############################")
## Order Amount == 0都是达人订单
    df_affliate = df_month_group_data[df_month_group_data["Order Amount"]== "MYR 0.00" ]
    print(f"达人样品订单 ： {df_affliate["Order ID"].nunique()} 单-----可能为卖家取消，并非全部发走")
## 被卖家取消的样品
    df_affliate_cancelbyseller = df_affliate[(df_affliate["Order Status"] =="Canceled")&(df_affliate["Cancel By"] =="Seller")]
    print(f"达人样品被商家取消订单 ： {df_affliate_cancelbyseller["Order ID"].nunique()} 单")
    df_affliate_cancelbysys = df_affliate[(df_affliate["Order Status"] =="Canceled")&(df_affliate["Cancel By"] =="System")]
    print(f"达人样品被系统取消订单 ： {df_affliate_cancelbysys["Order ID"].nunique()} 单")
    billdetail(df_affliate)


