#AkShare 数据
import akshare as ak

# 获取股票名称
def get_stock_name(stock_code):
    stock_individual_info_em_df = ak.stock_individual_info_em(symbol=stock_code)
    print(stock_individual_info_em_df)
    stock_name = stock_code
    try:
        stock_name = stock_individual_info_em_df[stock_individual_info_em_df['item'] == '股票简称']['value'].values[0]
        print(f"股票简称: {stock_name}")
        return stock_name
    except IndexError:
        print("未能找到股票简称信息")
    if len(stock_name) == 0:
        return
    return stock_name