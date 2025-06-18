# 股票回测Web应用

## 项目概述

这是一个基于Python的股票回测Web应用，集成了多个强大的开源库，为量化交易研究提供了一站式解决方案。通过直观的界面，用户可以获取市场数据、执行策略回测并可视化分析结果。

### 核心特性

- **数据获取** - 通过AkShare实时获取A股市场数据
- **策略回测** - 利用Backtrader框架测试交易策略表现
- **结果可视化** - 使用Pyecharts生成专业图表展示
- **交互界面** - 基于Streamlit构建友好的Web操作环境

## 技术架构

| 组件             | 功能          | 链接 |
|----------------|-------------|------|
| **Streamlit**  | 构建交互式数据应用界面 | [官方仓库](https://github.com/streamlit/streamlit) |
| **AkShare**    | 获取金融市场数据    | [官方仓库](https://github.com/akfamily/akshare) |
| **Backtrader** | 执行量化交易策略回测  | [官方仓库](https://github.com/mementum/backtrader) |
| **Pyecharts**  | 生成专业金融数据图表  | [官方仓库](https://github.com/pyecharts/pyecharts) |
### 项目分层
web: streamlit相关页面
internal: 放置业务相关逻辑
          service:业务逻辑
          rep：仓储
          router:fastapi数据接口api和router
          domain：中间层模型
          pkg：中间层组件放置的地方
core: 相关协议和类库
          inialize:初始化配置文件逻辑
          contract:协议相关
          domain:协议落库的数据模型
          config:配置文件实体相关
          db:管理数据库相关
          factors:策略放置的地方
          pkg：组件封装放置的地方
          recorders:数据获取的接口实现
config: 配置文件

## 快速开始


### 环境准备

确保已安装所有依赖包：

```bash
pip install -r requirements.txt
```

### 启动应用

执行以下命令启动Web界面：

```bash
streamlit run main.py
```
###
本地调式直接启动 debug_streamlit.py
### 策略测试

## 支持的策略

本项目实现了以下量化交易策略：

- **MA策略** - 基于单一移动平均线的趋势跟踪策略
- **MACross策略** - 基于快慢双均线交叉的信号策略

## 参数配置指南

### AkShare数据参数

| 参数 | 说明 |
|------|------|
| **symbol** | 股票代码（如：600070） |
| **period** | 数据周期（日线、周线、月线） |
| **start date** | 数据起始日期 |
| **end date** | 数据结束日期 |
| **adjust** | 复权方式（qfq：前复权，hfq：后复权） |

### Backtrader回测参数

| 参数 | 说明 |
|------|------|
| **start date** | 回测开始日期 |
| **end date** | 回测结束日期 |
| **start cash** | 初始资金 |
| **commission fee** | 交易佣金比例 |
| **stake** | 每次交易股数 |

## 相关推荐
