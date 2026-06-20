"""Plotly Dash interactive BI dashboard over the SQLite warehouse."""
import sqlite3

import dash
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
import pandas as pd

DB_PATH = 'data/warehouse.db'
app     = dash.Dash(__name__, title='BI Dashboard')

C = {
    'primary': '#1565C0', 'accent':  '#2196F3',
    'success': '#43A047', 'warning': '#FB8C00',
    'danger':  '#E53935', 'purple':  '#8E24AA',
    'bg':      '#F5F7FA', 'card':    '#FFFFFF',
}


def _q(sql):
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql(sql, conn)
    conn.close()
    return df


def _card(**extra):
    base = {'background': C['card'], 'borderRadius': '10px',
            'padding': '14px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}
    return {**base, **extra}


def kpi(title, value, color):
    return html.Div([
        html.P(title, style={'color': '#666', 'fontSize': '13px', 'margin': '0 0 6px'}),
        html.H3(value, style={'color': color, 'margin': '0', 'fontSize': '26px'}),
    ], style={**_card(), 'flex': '1', 'minWidth': '160px'})


app.layout = html.Div([
    html.Div([
        html.H1('Business Intelligence Dashboard',
                style={'color': 'white', 'margin': '0', 'fontSize': '22px'}),
        html.P('SQLite  ·  Python ETL  ·  Plotly Dash',
               style={'color': '#BBDEFB', 'margin': '4px 0 0', 'fontSize': '12px'}),
    ], style={'background': C['primary'], 'padding': '18px 30px'}),

    html.Div([
        html.Div([
            html.Label('Year', style={'fontWeight': '600', 'fontSize': '13px'}),
            dcc.Dropdown(id='yr', clearable=False,
                options=[{'label': 'All', 'value': 'all'}] +
                        [{'label': str(y), 'value': y} for y in [2021, 2022, 2023]],
                value='all', style={'width': '160px'}),
        ]),
        html.Div([
            html.Label('Region', style={'fontWeight': '600', 'fontSize': '13px'}),
            dcc.Dropdown(id='rgn', clearable=False,
                options=[{'label': 'All', 'value': 'all'}] +
                        [{'label': r, 'value': r} for r in ['North','South','East','West','Central']],
                value='all', style={'width': '160px'}),
        ]),
    ], style={'background': 'white', 'padding': '14px 30px', 'display': 'flex',
              'gap': '30px', 'boxShadow': '0 1px 4px rgba(0,0,0,0.06)'}),

    html.Div([
        html.Div(id='kpis', style={'display': 'flex', 'gap': '14px',
                                    'flexWrap': 'wrap', 'marginBottom': '18px'}),
        html.Div([
            html.Div([dcc.Graph(id='trend')],    style={**_card(), 'flex': '2'}),
            html.Div([dcc.Graph(id='cat-pie')],  style={**_card(), 'flex': '1'}),
        ], style={'display': 'flex', 'gap': '14px', 'marginBottom': '14px'}),
        html.Div([
            html.Div([dcc.Graph(id='reg-bar')],  style={**_card(), 'flex': '1'}),
            html.Div([dcc.Graph(id='seg-bar')],  style={**_card(), 'flex': '1'}),
        ], style={'display': 'flex', 'gap': '14px', 'marginBottom': '14px'}),
        html.Div([dcc.Graph(id='cohort')], style=_card()),
    ], style={'padding': '20px 30px', 'background': C['bg']}),
], style={'fontFamily': 'Segoe UI, Arial, sans-serif'})


@app.callback(
    [Output('kpis','children'), Output('trend','figure'),
     Output('cat-pie','figure'), Output('reg-bar','figure'),
     Output('seg-bar','figure'), Output('cohort','figure')],
    [Input('yr','value'), Input('rgn','value')],
)
def update(yr, rgn):
    clauses = []
    if yr  != 'all': clauses.append(f'order_year = {int(yr)}')
    if rgn != 'all': clauses.append(f"region = '{rgn}'")
    where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''

    df   = _q(f'SELECT * FROM fact_transactions {where}')
    prod = _q('SELECT product_id, category FROM dim_products')
    df   = df.merge(prod, on='product_id', how='left')

    kpis = [
        kpi('Total Revenue',    f"${df['revenue'].sum():,.0f}",       C['accent']),
        kpi('Total Profit',     f"${df['profit'].sum():,.0f}",        C['success']),
        kpi('Orders',           f"{df['order_id'].nunique():,}",       C['warning']),
        kpi('Unique Customers', f"{df['customer_id'].nunique():,}",    C['purple']),
        kpi('Avg Order Value',  f"${df['revenue'].mean():,.0f}",       C['danger']),
    ]

    monthly = (df.groupby('year_month')
                 .agg(revenue=('revenue','sum'))
                 .reset_index().sort_values('year_month'))
    trend = go.Figure([
        go.Bar(x=monthly['year_month'], y=monthly['revenue'],
               marker_color=C['accent'], opacity=0.6),
        go.Scatter(x=monthly['year_month'], y=monthly['revenue'],
                   mode='lines+markers', line={'color': C['primary'], 'width': 2}),
    ])
    trend.update_layout(title='Monthly Revenue', showlegend=False,
                        plot_bgcolor='white', paper_bgcolor='white',
                        height=300, margin={'t':40,'b':40})

    cat   = df.groupby('category')['revenue'].sum().reset_index()
    cpie  = px.pie(cat, values='revenue', names='category', title='By Category',
                   color_discrete_sequence=px.colors.qualitative.Set2, height=300)
    cpie.update_layout(paper_bgcolor='white', margin={'t':40,'b':0})

    reg   = df.groupby('region')['revenue'].sum().reset_index().sort_values('revenue')
    rbar  = px.bar(reg, x='revenue', y='region', orientation='h', title='By Region',
                   color='revenue', color_continuous_scale='Blues', height=280)
    rbar.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       showlegend=False, margin={'t':40,'b':30})

    seg   = df.groupby('segment').agg(revenue=('revenue','sum'), profit=('profit','sum')).reset_index()
    sbar  = go.Figure([
        go.Bar(name='Revenue', x=seg['segment'], y=seg['revenue'], marker_color=C['accent']),
        go.Bar(name='Profit',  x=seg['segment'], y=seg['profit'],  marker_color=C['success']),
    ])
    sbar.update_layout(title='Revenue vs Profit by Segment', barmode='group',
                       plot_bgcolor='white', paper_bgcolor='white',
                       height=280, margin={'t':40,'b':30})

    first_p = df.groupby('customer_id')['year_month'].min().reset_index()
    first_p.columns = ['customer_id', 'cohort_month']
    ca    = df.merge(first_p, on='customer_id')
    sizes = first_p.groupby('cohort_month').size().reset_index(name='cohort_size')
    acts  = ca.groupby(['cohort_month','year_month'])['customer_id'].nunique().reset_index(name='actives')
    acts  = acts.merge(sizes, on='cohort_month')
    acts['retention'] = (acts['actives'] / acts['cohort_size'] * 100).round(1)
    piv   = acts.pivot(index='cohort_month', columns='year_month', values='retention').iloc[:12,:12]
    cohort = go.Figure(go.Heatmap(
        z=piv.values, x=piv.columns.tolist(), y=piv.index.tolist(),
        colorscale='Blues', text=piv.values,
        texttemplate='%{text:.1f}%', showscale=True,
    ))
    cohort.update_layout(title='Cohort Retention (%)', height=380,
                         paper_bgcolor='white', margin={'t':50,'b':50},
                         xaxis_title='Activity Month', yaxis_title='Cohort')

    return kpis, trend, cpie, rbar, sbar, cohort


if __name__ == '__main__':
    app.run(debug=True, port=8050)
