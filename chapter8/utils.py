import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go


def plot_radial_plot(cluster_means: pd.DataFrame) -> None:
    cluster_means.round(2)
    categories = cluster_means.columns
    fig = go.Figure()
    for g in cluster_means.index:
        fig.add_trace(
            go.Scatterpolar(
                r=cluster_means.loc[g].values,
                theta=categories,
                fill="toself",
                name=f"cluster #{g}",
            )
        )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[-2, 6])  # here we can define the range
        ),
        showlegend=True,
        title="Cluster Radial Plot",
        title_x=0.5,
    )
    fig.show()


def plot_clusters_choropleth(
    ny_census: gpd.GeoDataFrame, column_to_plot: str, cmap: str
) -> None:
    _, ax = plt.subplots(1, figsize=(6, 6))
    ny_census.plot(
        column=column_to_plot,
        categorical=True,
        legend=True,
        linewidth=0,
        ax=ax,
        legend_kwds={"loc": "center left", "bbox_to_anchor": (1, 0.5), "fmt": "{:.0f}"},
        cmap=cmap,
    )
    ax.set_axis_off()
    plt.show()
