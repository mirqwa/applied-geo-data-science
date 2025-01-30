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
