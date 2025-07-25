# -*- coding: utf-8 -*-
import logging
from enum import Enum
from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from core.contract.api import decode_entity_id
from core.contract.data_type import Bean
from core.contract.normal_data import NormalData
from core.utils.decorator import to_string
from core.utils.pd_utils import pd_is_not_null

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """
    Chart type enum
    """

    #: candlestick chart
    kline = "kline"
    #: line chart
    line = "line"
    #: area chart
    area = "area"
    #: scatter chart
    scatter = "scatter"
    #: histogram chart
    histogram = "histogram"
    #: pie chart
    pie = "pie"
    #: bar chart
    bar = "bar"


_zvt_chart_type_map_scatter_mode = {ChartType.line: "lines", ChartType.area: "none", ChartType.scatter: "markers"}


@to_string
class Rect(Bean):
    """
    rect struct with left-bottom(x0, y0), right-top(x1, y1)
    """

    def __init__(self, x0=None, y0=None, x1=None, y1=None) -> None:
        #: left-bottom x0
        self.x0 = x0
        #: left-bottom y0
        self.y0 = y0
        #: right-top x1
        self.x1 = x1
        #: right-top y1
        self.y1 = y1


class Draw(object):
    def draw_kline(
        self, width=None, height=None, title=None, keep_ui_state=True, show=False, scale_value=None, **kwargs
    ):
        return self.draw(
            main_chart=ChartType.kline,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def draw_line(
        self, width=None, height=None, title=None, keep_ui_state=True, show=False, scale_value=None, **kwargs
    ):
        return self.draw(
            main_chart=ChartType.line,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def draw_area(
        self, width=None, height=None, title=None, keep_ui_state=True, show=False, scale_value=None, **kwargs
    ):
        return self.draw(
            main_chart=ChartType.area,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def draw_scatter(
        self, width=None, height=None, title=None, keep_ui_state=True, show=False, scale_value=None, **kwargs
    ):
        return self.draw(
            main_chart=ChartType.scatter,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def draw_histogram(
        self, width=None, height=None, title=None, keep_ui_state=True, show=False, scale_value=None, **kwargs
    ):
        return self.draw(
            ChartType.histogram,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def draw_bar(self, width=None, height=None, title=None, keep_ui_state=True, show=False, scale_value=None, **kwargs):
        return self.draw(
            ChartType.bar,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def draw_pie(self, width=None, height=None, title=None, keep_ui_state=True, show=False, scale_value=None, **kwargs):
        return self.draw(
            ChartType.pie,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def draw(
        self,
        main_chart=ChartType.kline,
        sub_chart="bar",
        width=None,
        height=None,
        title=None,
        keep_ui_state=True,
        show=False,
        scale_value=None,
        **kwargs,
    ):

        raise NotImplementedError()

    def default_layout(self, main_chart=None, width=None, height=None, title=None, keep_ui_state=True, **layout_params):
        if keep_ui_state:
            uirevision = True
        else:
            uirevision = None

        if main_chart == ChartType.histogram:
            xaxis = None
        else:
            xaxis = dict(
                linecolor="#BCCCDC",
                showgrid=False,
                showspikes=True,  # Show spike line for X-axis
                # Format spike
                spikethickness=2,
                spikedash="dot",
                spikecolor="#999999",
                spikemode="across",
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=3, label="3m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all"),
                        ]
                    )
                ),
                rangeslider=dict(
                    visible=True,
                ),
                type="date",
            )

        return dict(
            showlegend=True,
            plot_bgcolor="#FFF",
            hovermode="x",
            hoverdistance=100,  # Distance to show hover label of data point
            spikedistance=1000,  # Distance to show spike
            uirevision=uirevision,
            height=height,
            width=width,
            title=title,
            yaxis=dict(
                autorange=True,
                fixedrange=False,
                zeroline=False,
                linecolor="#BCCCDC",
                showgrid=False,
            ),
            xaxis=xaxis,
            legend_orientation="h",
            hoverlabel={"namelength": -1},
            **layout_params,
        )


class Drawable(object):
    def drawer(self):
        drawer = Drawer(
            main_df=self.drawer_main_df(),
            main_data=self.drawer_main_data(),
            factor_df_list=self.drawer_factor_df_list(),
            factor_data_list=self.drawer_factor_data_list(),
            sub_df_list=self.drawer_sub_df_list(),
            sub_data_list=self.drawer_sub_data_list(),
            sub_col_chart=self.drawer_sub_col_chart(),
            annotation_df=self.drawer_annotation_df(),
            rects=self.drawer_rects(),
        )
        return drawer

    def draw(
        self,
        main_chart=ChartType.kline,
        width=None,
        height=None,
        title=None,
        keep_ui_state=True,
        show=False,
        scale_value=None,
        **kwargs,
    ):
        return self.drawer().draw(
            main_chart=main_chart,
            width=width,
            height=height,
            title=title,
            keep_ui_state=keep_ui_state,
            show=show,
            scale_value=scale_value,
            **kwargs,
        )

    def drawer_main_df(self) -> Optional[pd.DataFrame]:
        return None

    def drawer_main_data(self) -> Optional[NormalData]:
        return None

    def drawer_factor_df_list(self) -> Optional[List[pd.DataFrame]]:
        return None

    def drawer_factor_data_list(self) -> Optional[List[NormalData]]:
        return None

    def drawer_sub_df_list(self) -> Optional[List[pd.DataFrame]]:
        return None

    def drawer_sub_data_list(self) -> Optional[List[NormalData]]:
        return None

    def drawer_annotation_df(self) -> Optional[pd.DataFrame]:
        return None

    def drawer_rects(self) -> Optional[List[Rect]]:
        return None

    def drawer_sub_col_chart(self) -> Optional[dict]:
        return None


class StackedDrawer(Draw):
    def __init__(self, *drawers) -> None:
        super().__init__()
        assert len(drawers) > 1
        self.drawers: List[Drawer] = drawers

    def make_y_layout(self, index, total, start_index=1, domain_range=(0, 1)):
        part = (domain_range[1] - domain_range[0]) / total

        if index == 1:
            yaxis = "yaxis"
            y = "y"
        else:
            yaxis = f"yaxis{index}"
            y = f"y{index}"

        return (
            yaxis,
            y,
            dict(
                anchor="x",
                autorange=True,
                fixedrange=False,
                zeroline=False,
                linecolor="#BCCCDC",
                showgrid=False,
                domain=[
                    domain_range[0] + part * (index - start_index),
                    domain_range[0] + part * (index - start_index + 1),
                ],
            ),
        )

    def draw(
        self,
        main_chart=ChartType.kline,
        sub_chart="bar",
        width=None,
        height=None,
        title=None,
        keep_ui_state=True,
        show=False,
        scale_value=None,
        **kwargs,
    ):
        stacked_fig = go.Figure()

        total = len(self.drawers)
        start = 1
        domain_range = (0, 1)
        for drawer in self.drawers:
            if drawer.has_sub_plot():
                domain_range = (0.2, 1)
                start = 2
                break
        for index, drawer in enumerate(self.drawers, start=start):
            traces, sub_traces = drawer.make_traces(
                main_chart=main_chart, sub_chart=sub_chart, scale_value=scale_value, **kwargs
            )

            # fix sub traces as the bottom
            if sub_traces:
                yaxis, y, layout = self.make_y_layout(index=1, total=1, domain_range=(0, 0.2))
                # update sub_traces with yaxis
                for trace in sub_traces:
                    trace.yaxis = y
                stacked_fig.add_traces(sub_traces)
                stacked_fig.layout[yaxis] = layout

            # make y layouts
            yaxis, y, layout = self.make_y_layout(
                index=index, total=total, start_index=start, domain_range=domain_range
            )

            stacked_fig.layout[yaxis] = layout

            # update traces with yaxis
            for trace in traces:
                trace.yaxis = y
            stacked_fig.add_traces(traces)

            # update shapes with yaxis
            if drawer.rects:
                for rect in drawer.rects:
                    stacked_fig.add_shape(
                        type="rect",
                        x0=rect.x0,
                        y0=rect.y0,
                        x1=rect.x1,
                        y1=rect.y1,
                        line=dict(color="RoyalBlue", width=1),
                        # fillcolor="LightSkyBlue",
                        yref=y,
                    )

            # annotations
            if pd_is_not_null(drawer.annotation_df):
                stacked_fig.layout["annotations"] = annotations(drawer.annotation_df, yref=y)

        stacked_fig.update_layout(
            self.default_layout(
                main_chart=main_chart, width=width, height=height, title=title, keep_ui_state=keep_ui_state
            )
        )

        if show:
            stacked_fig.show()
        else:
            return stacked_fig


class Drawer(Draw):
    def __init__(
        self,
        main_df: pd.DataFrame = None,
        factor_df_list: List[pd.DataFrame] = None,
        sub_df_list: pd.DataFrame = None,
        main_data: NormalData = None,
        factor_data_list: List[NormalData] = None,
        sub_data_list: NormalData = None,
        sub_col_chart: Optional[dict] = None,
        rects: List[Rect] = None,
        annotation_df: pd.DataFrame = None,
        scale_value: int = None,
    ) -> None:
        """

        :param main_df: df for main chart
        :param factor_df_list: list of factor df on main chart
        :param sub_df_list: df for sub chart under main chart
        :param main_data: NormalData wrap main_df,use either
        :param factor_data_list: list of NormalData wrap factor_df,use either
        :param sub_data_list: NormalData wrap sub_df,use either
        :param annotation_df:
        """

        #: 主图数据
        if main_data is None:
            main_data = NormalData(main_df)
        self.main_data: NormalData = main_data

        #: 主图因子
        if not factor_data_list and factor_df_list:
            factor_data_list = []
            for df in factor_df_list:
                factor_data_list.append(NormalData(df))
        #: 每一个df可能有多个column, 代表多个指标，对于连续型的，可以放在一个df里面
        #: 对于离散型的，比如一些特定模式的连线，放在多个df里面较好，因为index不同
        self.factor_data_list: List[NormalData] = factor_data_list

        #: 副图数据
        if not sub_data_list and sub_df_list:
            sub_data_list = []
            for df in sub_df_list:
                sub_data_list.append(NormalData(df))
        #: 每一个df可能有多个column, 代表多个指标，对于连续型的，可以放在一个df里面
        #: 对于离散型的，比如一些特定模式的连线，放在多个df里面较好，因为index不同
        self.sub_data_list: List[NormalData] = sub_data_list

        #: 幅图col对应的图形，line or bar
        self.sub_col_chart = sub_col_chart

        #: 主图的标记数据
        self.annotation_df = annotation_df

        #: list of rect
        self.rects = rects

        self.scale_value = scale_value

    def add_factor_df(self, df: pd.DataFrame):
        self.add_factor_data(NormalData(df))

    def add_factor_data(self, data: NormalData):
        if not self.factor_data_list:
            self.factor_data_list = []
        self.factor_data_list.append(data)

    def add_sub_df(self, df: pd.DataFrame):
        self.add_sub_data(NormalData(df))

    def add_sub_data(self, data: NormalData):
        if not self.sub_data_list:
            self.sub_data_list = []
        self.sub_data_list.append(data)

    def has_sub_plot(self):
        return self.sub_data_list is not None and not self.sub_data_list[0].empty()

    def make_traces(self, main_chart=ChartType.kline, sub_chart="bar", yaxis="y", scale_value=None, **kwargs):
        traces = []
        sub_traces = []

        for entity_id, df in self.main_data.entity_map_df.items():
            df = df.select_dtypes(np.number)
            df = df.copy()
            if scale_value:
                for col in df.columns:
                    first = None
                    for i in range(0, len(df)):
                        first = df[col][i]
                        if first != 0:
                            break
                    if first == 0:
                        continue
                    scale = scale_value / first
                    df[col] = df[col] * scale
            code = entity_id
            try:
                _, _, code = decode_entity_id(entity_id)
            except Exception:
                pass

            # 构造主图
            if main_chart == ChartType.bar:
                for col in df.columns:
                    trace_name = "{}_{}".format(code, col)
                    ydata = df[col].values.tolist()
                    traces.append(go.Bar(x=df.index, y=ydata, name=trace_name, yaxis=yaxis, **kwargs))
            elif main_chart == ChartType.kline:
                trace_name = "{}_kdata".format(code)
                trace = go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    close=df["close"],
                    low=df["low"],
                    high=df["high"],
                    name=trace_name,
                    yaxis=yaxis,
                    **kwargs,
                )
                traces.append(trace)
            elif main_chart in [ChartType.scatter, ChartType.line, ChartType.area]:
                mode = _zvt_chart_type_map_scatter_mode.get(main_chart)
                for col in df.columns:
                    trace_name = "{}_{}".format(code, col)
                    ydata = df[col].values.tolist()
                    traces.append(go.Scatter(x=df.index, y=ydata, mode=mode, name=trace_name, yaxis=yaxis, **kwargs))
            elif main_chart == ChartType.histogram:
                for col in df.columns:
                    trace_name = "{}_{}".format(code, col)
                    x = df[col].tolist()
                    trace = go.Histogram(x=x, name=trace_name, **kwargs)
                    traces.append(trace)
                    annotation = [
                        dict(
                            entity_id=entity_id,
                            timestamp=x[-1],
                            value=0,
                            flag=f"{trace_name}:{x[-1]}",
                        )
                    ]
                    annotation_df = pd.DataFrame.from_records(annotation, index=["entity_id", "timestamp"])
                    if pd_is_not_null(self.annotation_df):
                        self.annotation_df = pd.concat([self.annotation_df, annotation_df])
                    else:
                        self.annotation_df = annotation_df
            elif main_chart == ChartType.pie:
                for _, row in df.iterrows():
                    traces.append(go.Pie(name=entity_id, labels=df.columns.tolist(), values=row.tolist(), **kwargs))
            else:
                assert False

            # 构造主图指标
            if self.factor_data_list:
                for factor_data in self.factor_data_list:
                    if not factor_data.empty():
                        factor_df = factor_data.entity_map_df.get(entity_id)
                        factor_df = factor_df.select_dtypes(np.number)
                        if pd_is_not_null(factor_df):
                            for col in factor_df.columns:
                                trace_name = "{}_{}".format(code, col)
                                ydata = factor_df[col].values.tolist()

                                line = go.Scatter(
                                    x=factor_df.index, y=ydata, mode="lines", name=trace_name, yaxis=yaxis, **kwargs
                                )
                                traces.append(line)

            # 构造幅图
            if self.has_sub_plot():
                for sub_data in self.sub_data_list:
                    sub_df = sub_data.entity_map_df.get(entity_id)
                    if pd_is_not_null(sub_df):
                        sub_df = sub_df.select_dtypes(np.number)
                        for col in sub_df.columns:
                            trace_name = "{}_{}".format(code, col)
                            ydata = sub_df[col].values.tolist()

                            def color(i):
                                if i > 0:
                                    return "red"
                                else:
                                    return "green"

                            colors = [color(i) for i in ydata]

                            the_sub_chart = None
                            if self.sub_col_chart is not None:
                                the_sub_chart = self.sub_col_chart.get(col)
                            if not the_sub_chart:
                                the_sub_chart = sub_chart

                            if the_sub_chart == ChartType.line:
                                sub_trace = go.Scatter(
                                    x=sub_df.index, y=ydata, name=trace_name, yaxis="y2", marker=dict(color=colors)
                                )
                            else:
                                sub_trace = go.Bar(
                                    x=sub_df.index, y=ydata, name=trace_name, yaxis="y2", marker=dict(color=colors)
                                )
                            sub_traces.append(sub_trace)

        return traces, sub_traces

    def add_rects(self, fig, yaxis="y"):
        if self.rects:
            for rect in self.rects:
                fig.add_shape(
                    type="rect",
                    x0=rect.x0,
                    y0=rect.y0,
                    x1=rect.x1,
                    y1=rect.y1,
                    line=dict(color="RoyalBlue", width=1),
                    # fillcolor="LightSkyBlue"
                )
            fig.update_shapes(dict(xref="x", yref=yaxis))

    def draw(
        self,
        main_chart=ChartType.kline,
        sub_chart="bar",
        width=None,
        height=None,
        title=None,
        keep_ui_state=True,
        show=False,
        scale_value=None,
        **kwargs,
    ):
        yaxis = "y"
        traces, sub_traces = self.make_traces(
            main_chart=main_chart, sub_chart=sub_chart, yaxis=yaxis, scale_value=scale_value, **kwargs
        )

        if sub_traces:
            fig = make_subplots(rows=2, cols=1, row_heights=[0.8, 0.2], vertical_spacing=0.08, shared_xaxes=True)
            fig.add_traces(traces, rows=[1] * len(traces), cols=[1] * len(traces))
            fig.add_traces(sub_traces, rows=[2] * len(sub_traces), cols=[1] * len(sub_traces))
        else:
            fig = go.Figure()
            fig.add_traces(traces)

        # 绘制矩形
        self.add_rects(fig, yaxis=yaxis)

        fig.update_layout(
            self.default_layout(
                main_chart=main_chart, width=width, height=height, title=title, keep_ui_state=keep_ui_state
            )
        )

        if sub_traces:
            fig.update_layout(xaxis_rangeslider_visible=False)
            fig.update_layout(xaxis2_rangeslider_visible=True, xaxis2_rangeslider_thickness=0.1)
        # 绘制标志
        if pd_is_not_null(self.annotation_df):
            fig.layout["annotations"] = annotations(self.annotation_df, yref=yaxis)

        if show:
            fig.show()
        else:
            return fig

    def draw_table(self, width=None, height=None, title=None, keep_ui_state=True, **kwargs):
        cols = self.main_data.data_df.index.names + self.main_data.data_df.columns.tolist()

        index1 = self.main_data.data_df.index.get_level_values(0).tolist()
        index2 = self.main_data.data_df.index.get_level_values(1).tolist()
        values = [index1] + [index2] + [self.main_data.data_df[col] for col in self.main_data.data_df.columns]

        data = go.Table(
            header=dict(
                values=cols,
                fill_color=["#000080", "#000080"] + ["#0066cc"] * len(self.main_data.data_df.columns),
                align="left",
                font=dict(color="white", size=13),
            ),
            cells=dict(values=values, fill=dict(color="#F5F8FF"), align="left"),
            **kwargs,
        )

        fig = go.Figure()
        fig.add_traces([data])
        fig.update_layout(self.default_layout(width=width, height=height, title=title, keep_ui_state=keep_ui_state))

        fig.show()


def annotations(annotation_df: pd.DataFrame, yref="y"):
    """
    annotation_df format::

                                        value    flag    color
        entity_id    timestamp

    :param annotation_df:
    :param yref: specific yaxis e.g, y,y2,y3
    :return:
    """

    if pd_is_not_null(annotation_df):
        annotations = []
        for trace_name, df in annotation_df.groupby(level=0):
            if pd_is_not_null(df):
                for (_, timestamp), item in df.iterrows():
                    if "color" in item:
                        color = item["color"]
                    else:
                        color = "#ec0000"

                    value = round(item["value"], 2)
                    annotations.append(
                        dict(
                            x=timestamp,
                            y=value,
                            xref="x",
                            yref=yref,
                            text=item["flag"],
                            showarrow=True,
                            align="center",
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            # arrowcolor='#030813',
                            ax=-10,
                            ay=-30,
                            bordercolor="#c7c7c7",
                            borderwidth=1,
                            bgcolor=color,
                            opacity=0.8,
                        )
                    )
        return annotations
    return None


# the __all__ is generated
__all__ = ["ChartType", "Rect", "Draw", "Drawable", "StackedDrawer", "Drawer", "annotations"]
