# import pandas as pd
# import plotly.graph_objects as go
# from scipy.signal import find_peaks
# from flask import Flask, render_template_string
# from io import StringIO  # Changed from BytesIO for text handling

# app = Flask(__name__)

# def plot_to_html(fig):
#     buf = StringIO()  # Use StringIO for text
#     fig.write_html(buf)
#     buf.seek(0)
#     return buf.getvalue()  # Return the string directly

# # Load data (ensure Sample_Data.csv is present)
# df = pd.read_csv('Sample_Data.csv')
# df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M')
# df = df.sort_values('Timestamp')

# # 1a. Create Plotly figure for FIGURE 1
# fig1 = go.Figure()

# # Original data
# fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Original Values', 
#                           line=dict(color='blue', width=1), opacity=0.5))

# # Moving averages (1000 and 5000 points)
# window_1000 = min(1000, len(df))
# window_5000 = min(5000, len(df))
# df['MA_1000'] = df['Values'].rolling(window_1000, min_periods=1).mean()
# df['MA_5000'] = df['Values'].rolling(window_5000, min_periods=1).mean()

# fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_1000'], mode='lines', name='1000 Value MA', 
#                           line=dict(color='red', width=2)))
# fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_5000'], mode='lines', name='5000 Value MA', 
#                           line=dict(color='green', width=2)))

# fig1.update_layout(title='Values with 1000 and 5000 Value Moving Averages',
#                    xaxis_title='Timestamp',
#                    yaxis_title='Values',
#                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#                    grid=dict(rows=1, columns=1),
#                    template='plotly_white')
# html_plot1 = plot_to_html(fig1)

# # 1b. 5-day moving average
# df.set_index('Timestamp', inplace=True)
# df['MA_5day'] = df['Values'].rolling('5D').mean()
# df.reset_index(inplace=True)

# fig2 = go.Figure()
# fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Voltage', 
#                           line=dict(color='blue', width=1), opacity=0.5))
# fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_5day'], mode='lines', name='5-Day Moving Average', 
#                           line=dict(color='orange', width=2)))

# fig2.update_layout(title='Voltage vs. Timestamp with 5-Day Moving Average',
#                    xaxis_title='Timestamp',
#                    yaxis_title='Voltage',
#                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#                    grid=dict(rows=1, columns=1),
#                    template='plotly_white')
# html_plot2 = plot_to_html(fig2)

# # 1c. Local peaks and lows
# peaks, _ = find_peaks(df['Values'], distance=10)
# peaks_df = df.iloc[peaks][['Timestamp', 'Values']].copy()
# peaks_df['Type'] = 'Peak'
# lows, _ = find_peaks(-df['Values'], distance=10)
# lows_df = df.iloc[lows][['Timestamp', 'Values']].copy()
# lows_df['Type'] = 'Low'
# extrema_df = pd.concat([peaks_df, lows_df]).sort_values('Timestamp')
# extrema_df.to_csv('extrema.csv', index=False)

# # 1d. Instances where Voltage < 20
# below_20 = df[df['Values'] < 20][['Timestamp', 'Values']]
# below_20.to_csv('below_20.csv', index=False)

# # 2. Downward slope acceleration
# df['diff'] = df['Values'].diff()
# df['second_diff'] = df['diff'].diff()
# recharge_points = df[df['diff'] > 10].index.tolist()
# cycles = []
# start = 0
# for end in recharge_points + [len(df)]:
#     cycles.append((start, end))
#     start = end
# accel_points = []
# for start, end in cycles:
#     cycle_df = df.iloc[start:end].dropna()
#     if len(cycle_df) > 2:
#         accel = cycle_df[(cycle_df['diff'] < 0) & (cycle_df['second_diff'] < 0)]
#         if not accel.empty:
#             accel_points.append(accel[['Timestamp']])
# if accel_points:
#     accel_df = pd.concat(accel_points).drop_duplicates()
#     accel_df.to_csv('accel_down.csv', index=False)

# # Load tables
# extrema = pd.read_csv('extrema.csv')
# below_20 = pd.read_csv('below_20.csv')
# accel_down = pd.read_csv('accel_down.csv')

# html_template = """
# <!doctype html>
# <html>
# <head><title>Voltage Data Dashboard</title></head>
# <body>
# <h1>Values with 1000 and 5000 Value Moving Averages</h1>
# {{ plot1 | safe }}
# <h1>Voltage with 5-Day Moving Average</h1>
# {{ plot2 | safe }}
# <h1>Local Peaks and Lows</h1>
# {{ extrema_table | safe }}
# <h1>Voltage Below 20</h1>
# {{ below_20_table | safe }}
# <h1>Acceleration in Downward Slopes</h1>
# {{ accel_table | safe }}
# </body>
# </html>
# """

# @app.route('/')
# def index():
#     return render_template_string(html_template, plot1=html_plot1, plot2=html_plot2,
#                                  extrema_table=extrema.to_html(index=False),
#                                  below_20_table=below_20.to_html(index=False),
#                                  accel_table=accel_down.to_html(index=False))

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)









from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
from assignment1 import analyze_voltage_data

app = Flask(__name__)

@app.route('/')
def index():
    # Load and analyze data
    df = pd.read_csv('Sample_Data.csv')
    analysis_results = analyze_voltage_data(df)
    
    # Generate plots
    fig1 = go.Figure(data=[
        go.Scatter(x=df['Timestamp'], y=df['Values'], name='Values', line=dict(color='blue')),
        go.Scatter(x=df['Timestamp'], y=analysis_results['ma_1000'], name='1000 MA', line=dict(color='red')),
        go.Scatter(x=df['Timestamp'], y=analysis_results['ma_5000'], name='5000 MA', line=dict(color='green'))
    ])
    fig1.update_layout(title='Values with 1000 and 5000 Value Moving Averages')
    
    fig2 = go.Figure(data=[
        go.Scatter(x=df['Timestamp'], y=df['Values'], name='Voltage', line=dict(color='blue')),
        go.Scatter(x=df['Timestamp'], y=analysis_results['ma_5day'], name='5-Day MA', line=dict(color='orange'))
    ])
    fig2.update_layout(title='Voltage vs. Timestamp with 5-Day Moving Average')
    
    # Convert Plotly figures to HTML
    plot1_div = fig1.to_html(full_html=False)
    plot2_div = fig2.to_html(full_html=False)
    
    return render_template('index.html', plot1_div=plot1_div, plot2_div=plot2_div,
                          peaks_lows=analysis_results['peaks_lows'].to_html(classes='table table-striped'),
                          voltage_below_20=analysis_results['voltage_below_20'].to_html(classes='table table-striped'),
                          downward_slopes=analysis_results['downward_slopes'].to_html(classes='table table-striped'))

if __name__ == '__main__':
    app.run(debug=True)