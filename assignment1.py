import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks
from flask import Flask, render_template_string
import os
from io import BytesIO

print("Starting script execution...")

# Load data into DataFrame
try:
    df = pd.read_csv('Sample_Data.csv')  # Save the full data from <DOCUMENT> as Sample_Data.csv
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M')  # Corrected format for DD-MM-YYYY HH:MM
    df = df.sort_values('Timestamp')
    print("Data loaded and sorted successfully. First timestamp:", df['Timestamp'].iloc[0])
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# 1a. Create Plotly figure for FIGURE 1
fig1 = go.Figure()

# Original data
fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Original Values', 
                          line=dict(color='blue', width=1), opacity=0.5))

# Moving averages (1000 and 5000 points)
window_1000 = min(1000, len(df))
window_5000 = min(5000, len(df))
df['MA_1000'] = df['Values'].rolling(window_1000, min_periods=1).mean()
df['MA_5000'] = df['Values'].rolling(window_5000, min_periods=1).mean()

fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_1000'], mode='lines', name='1000 Value MA', 
                          line=dict(color='red', width=2)))
fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_5000'], mode='lines', name='5000 Value MA', 
                          line=dict(color='green', width=2)))

fig1.update_layout(title='Values with 1000 and 5000 Value Moving Averages',
                   xaxis_title='Timestamp',
                   yaxis_title='Values',
                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                   grid=dict(rows=1, columns=1),
                   template='plotly_white')
fig1.write_html('ma_plot.html')  # Save for webapp
print("FIGURE 1 generated and saved as ma_plot.html.")

# 1b. 5-day moving average
df.set_index('Timestamp', inplace=True)
df['MA_5day'] = df['Values'].rolling('5D').mean()
df.reset_index(inplace=True)

fig2 = go.Figure()
print("Generating FIGURE 2...")
fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Voltage', 
                          line=dict(color='blue', width=1), opacity=0.5))
fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_5day'], mode='lines', name='5-Day Moving Average', 
                          line=dict(color='orange', width=2)))

fig2.update_layout(title='Voltage vs. Timestamp with 5-Day Moving Average',
                   xaxis_title='Timestamp',
                   yaxis_title='Voltage',
                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                   grid=dict(rows=1, columns=1),
                   template='plotly_white')
fig2.write_html('5day_ma_plot.html')
print("FIGURE 2 generated and saved as 5day_ma_plot.html.")

# 1c. Local peaks and lows
peaks, _ = find_peaks(df['Values'], distance=10)
peaks_df = df.iloc[peaks][['Timestamp', 'Values']].copy()
peaks_df['Type'] = 'Peak'
print("Local Peaks:")
print(peaks_df.to_string(index=False))

lows, _ = find_peaks(-df['Values'], distance=10)
lows_df = df.iloc[lows][['Timestamp', 'Values']].copy()
lows_df['Type'] = 'Low'
print("\nLocal Lows:")
print(lows_df.to_string(index=False))

extrema_df = pd.concat([peaks_df, lows_df]).sort_values('Timestamp')
extrema_df.to_csv('extrema.csv', index=False)
print("Peaks and lows saved to extrema.csv.")

# 1d. Instances where Voltage < 20
below_20 = df[df['Values'] < 20][['Timestamp', 'Values']]
print("\nInstances where Voltage < 20:")
print(below_20.to_string(index=False))
below_20.to_csv('below_20.csv', index=False)
print("Voltage < 20 instances saved to below_20.csv.")

# 2. Downward slope acceleration
df['diff'] = df['Values'].diff()
df['second_diff'] = df['diff'].diff()
recharge_points = df[df['diff'] > 10].index.tolist()
cycles = []
start = 0
for end in recharge_points + [len(df)]:
    cycles.append((start, end))
    start = end

accel_points = []
for start, end in cycles:
    cycle_df = df.iloc[start:end].dropna()
    if len(cycle_df) > 2:
        accel = cycle_df[(cycle_df['diff'] < 0) & (cycle_df['second_diff'] < 0)]
        if not accel.empty:
            accel_points.append(accel[['Timestamp']])

if accel_points:
    accel_df = pd.concat(accel_points).drop_duplicates()
    print("\nTimestamps where downward slope accelerates in each cycle:")
    print(accel_df.to_string(index=False))
    accel_df.to_csv('accel_down.csv', index=False)
else:
    print("\nNo acceleration points found in downward cycles.")
print("Slope acceleration analysis completed.")

# 4. Flask webapp setup
app = Flask(__name__)
print("Initializing Flask app...")

def plot_to_html(fig):
    buf = BytesIO()
    fig.write_html(buf)
    buf.seek(0)
    return buf.read().decode('utf-8')

# Load tables with error handling
try:
    extrema = pd.read_csv('extrema.csv')
    below_20 = pd.read_csv('below_20.csv')
    accel_down = pd.read_csv('accel_down.csv')
    print("CSV files loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading CSV files: {e}. Ensure script runs fully.")
    extrema, below_20, accel_down = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Generate HTML for plots with encoding fix
html_plot1 = ''
html_plot2 = ''
try:
    with open('ma_plot.html', 'r', encoding='utf-8') as f:
        html_plot1 = f.read()
    with open('5day_ma_plot.html', 'r', encoding='utf-8') as f:
        html_plot2 = f.read()
    print("HTML plot files read successfully.")
except FileNotFoundError:
    print("Warning: Plot HTML files not found. Regenerating placeholders.")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Original Values'))
    fig1.update_layout(title='Placeholder MA Plot')
    html_plot1 = plot_to_html(fig1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Voltage'))
    fig2.update_layout(title='Placeholder 5-Day MA Plot')
    html_plot2 = plot_to_html(fig2)
except UnicodeDecodeError as e:
    print(f"Encoding error reading HTML files: {e}. Regenerating placeholders.")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Original Values'))
    fig1.update_layout(title='Placeholder MA Plot')
    html_plot1 = plot_to_html(fig1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Voltage'))
    fig2.update_layout(title='Placeholder 5-Day MA Plot')
    html_plot2 = plot_to_html(fig2)

html_template = """
<!doctype html>
<html>
<head><title>Voltage Data Dashboard</title></head>
<body>
<h1>Values with 1000 and 5000 Value Moving Averages</h1>
{{ plot1 | safe }}
<h1>Voltage with 5-Day Moving Average</h1>
{{ plot2 | safe }}
<h1>Local Peaks and Lows</h1>
{{ extrema_table | safe }}
<h1>Voltage Below 20</h1>
{{ below_20_table | safe }}
<h1>Acceleration in Downward Slopes</h1>
{{ accel_table | safe }}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template, plot1=html_plot1, plot2=html_plot2,
                                 extrema_table=extrema.to_html(index=False),
                                 below_20_table=below_20.to_html(index=False),
                                 accel_table=accel_down.to_html(index=False))

if __name__ == '__main__':
    print(f"Starting Flask server on http://127.0.0.1:5000 and http://10.141.54.217:5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)  # Default port