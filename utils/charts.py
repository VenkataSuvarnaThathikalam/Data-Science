import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def line_chart(df: pd.DataFrame, date_col: str, value_col: str, title: str, freq: str = "M"):
    if date_col not in df.columns or value_col not in df.columns:
        return None
    data = df.groupby(pd.Grouper(key=date_col, freq=freq))[value_col].sum().reset_index()
    fig = px.line(data, x=date_col, y=value_col, title=title, markers=True)
    return fig


def multi_line_chart(df: pd.DataFrame, date_col: str, value_cols: list, title: str, freq: str = "M"):
    """Plot multiple lines on same chart"""
    data = df.groupby(pd.Grouper(key=date_col, freq=freq))[value_cols].sum().reset_index()
    fig = px.line(data, x=date_col, y=value_cols, title=title, markers=True)
    return fig


def bar_chart(df: pd.DataFrame, group_col: str, value_col: str | None, title: str, top_n: int = None, aggfunc: str = "sum"):
    if value_col is None:
        data = df.groupby(group_col).size().reset_index(name="count")
        sort_col = "count"
    elif aggfunc == "sum":
        data = df.groupby(group_col)[value_col].sum().reset_index(name=value_col)
        sort_col = value_col
    elif aggfunc == "count":
        data = df.groupby(group_col)[value_col].count().reset_index(name=value_col)
        sort_col = value_col
    elif aggfunc == "mean":
        data = df.groupby(group_col)[value_col].mean().reset_index(name=value_col)
        sort_col = value_col
    elif aggfunc == "nunique":
        data = df.groupby(group_col)[value_col].nunique().reset_index(name=value_col)
        sort_col = value_col
    else:
        data = df.groupby(group_col)[value_col].sum().reset_index(name=value_col)
        sort_col = value_col

    data = data.sort_values(sort_col, ascending=False)
    if top_n:
        data = data.head(top_n)
    fig = px.bar(data, x=group_col, y=sort_col, title=title, text=sort_col)
    return fig


def horizontal_bar_chart(df: pd.DataFrame, group_col: str, value_col: str, title: str, top_n: int = None):
    """Horizontal bar chart for better readability with many categories"""
    data = df.groupby(group_col)[value_col].sum().reset_index(name=value_col)
    data = data.sort_values(value_col, ascending=True)
    if top_n:
        data = data.tail(top_n)
    fig = px.bar(data, y=group_col, x=value_col, title=title, orientation="h")
    return fig


def scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None, title: str):
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title, hover_data=[x_col, y_col])
    return fig


def histogram(df: pd.DataFrame, column: str, title: str, nbins: int = 30):
    df_clean = df[[column]].dropna()
    fig = px.histogram(df_clean, x=column, nbins=nbins, title=title)
    return fig


def pie_chart(df: pd.DataFrame, values_col: str, names_col: str, title: str):
    """Create a pie chart"""
    data = df.groupby(names_col)[values_col].sum().reset_index()
    fig = px.pie(data, values=values_col, names=names_col, title=title)
    return fig


def box_plot(df: pd.DataFrame, y_col: str, x_col: str | None, title: str):
    """Create a box plot to show distribution"""
    fig = px.box(df, y=y_col, x=x_col, title=title)
    return fig


def heatmap(data: pd.DataFrame, title: str):
    """Create a heatmap from pivot data"""
    fig = go.Figure(data=go.Heatmap(z=data.values, x=data.columns, y=data.index))
    fig.update_layout(title=title)
    return fig


def waterfall_chart(df: pd.DataFrame, category_col: str, value_col: str, title: str):
    """Create a waterfall chart"""
    data = df.groupby(category_col)[value_col].sum().reset_index()
    fig = go.Figure(go.Waterfall(
        x=data[category_col],
        y=data[value_col],
        textposition="outside",
        text=data[value_col],
    ))
    fig.update_layout(title=title)
    return fig


def default_rate_chart(df: pd.DataFrame, segment_col: str, title: str):
    """Create chart showing default rate by segment"""
    data = df.groupby(segment_col)["TARGET"].agg(["sum", "count"]).reset_index()
    data.columns = [segment_col, "Defaults", "Total"]
    data["Default_Rate"] = (data["Defaults"] / data["Total"] * 100).round(2)
    data = data.sort_values("Default_Rate", ascending=False)
    fig = px.bar(data, x=segment_col, y="Default_Rate", title=title, text="Default_Rate")
    return fig