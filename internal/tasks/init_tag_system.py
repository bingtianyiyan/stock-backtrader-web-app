# -*- coding: utf-8 -*-
from core.domain import Block, BlockStock, Stock
from core.tag.tag_service import build_default_main_tag, build_default_sub_tags
from core.tag.tag_utils import (
    build_initial_stock_pool_info,
    build_initial_main_tag_info,
    build_initial_sub_tag_info,
    build_initial_industry_info,
)
from core.trading.trading_service import build_default_query_stock_quote_setting

def init_tag_system_info():
    # init industry info
    build_initial_industry_info()#zvt库 industry_info 行业信息

    # init tag info
    build_initial_main_tag_info()#zvt库 main_tag_info  行业标签
    build_initial_sub_tag_info()#zvt库 sub_tag_info 概念标签
    build_initial_stock_pool_info()#zvt库 stock_pool_info
    build_default_query_stock_quote_setting()#zvt库 query_stock_quote_setting

    Stock.record_data(provider="em")
    Block.record_data(provider="em", sleeping_time=0)
    BlockStock.record_data(provider="em", sleeping_time=0)
    # init default main tag
    build_default_main_tag()#zvt库 stock_tags 股票标签

    # init default sub tags
    build_default_sub_tags()#zvt库 根据em的stock表数据获取股票id 然后查询表zvt库sub_tag_info数据，把subTag标签数据概念数据更新


if __name__ == "__main__":
    # init industry info
    build_initial_industry_info()#zvt库 industry_info 行业信息

    # init tag info
    build_initial_main_tag_info()#zvt库 main_tag_info  行业标签
    build_initial_sub_tag_info()#zvt库 sub_tag_info 概念标签
    build_initial_stock_pool_info()#zvt库 stock_pool_info
    build_default_query_stock_quote_setting()#zvt库 query_stock_quote_setting

    Stock.record_data(provider="em")
    Block.record_data(provider="em", sleeping_time=0)
    BlockStock.record_data(provider="em", sleeping_time=0)
    # init default main tag
    build_default_main_tag()#zvt库 stock_tags 股票标签

    # init default sub tags
    build_default_sub_tags()#zvt库 根据em的stock表数据获取股票id 然后查询表zvt库sub_tag_info数据，把subTag标签数据概念数据更新
