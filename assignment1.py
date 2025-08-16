# assignment1.py
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks

def analyze_voltage_data(df):
    # Ensure Timestamp is in datetime format
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M')
    df = df.sort_values('Timestamp')

    # 1a. Moving averages (1000 and 5000 points)
    window_1000 = min(1000, len(df))
    window_5000 = min(5000, len(df))
    df['MA_1000'] = df['Values'].rolling(window_1000, min_periods=1).mean()
    df['MA_5000'] = df['Values'].rolling(window_5000, min_periods=1).mean()

    # 1b. 5-day moving average
    df.set_index('Timestamp', inplace=True)
    df['MA_5day'] = df['Values'].rolling('5D').mean()
    df.reset_index(inplace=True)

    # 1c. Local peaks and lows
    peaks, _ = find_peaks(df['Values'], distance=10)
    peaks_df = df.iloc[peaks][['Timestamp', 'Values']].copy()
    peaks_df['Type'] = 'Peak'
    lows, _ = find_peaks(-df['Values'], distance=10)
    lows_df = df.iloc[lows][['Timestamp', 'Values']].copy()
    lows_df['Type'] = 'Low'
    extrema_df = pd.concat([peaks_df, lows_df]).sort_values('Timestamp')

    # 1d. Instances where Voltage < 20
    below_20 = df[df['Values'] < 20][['Timestamp', 'Values']]

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
    accel_df = pd.concat(accel_points).drop_duplicates() if accel_points else pd.DataFrame()

    # Save results to CSV (optional for local debugging)
    extrema_df.to_csv('extrema.csv', index=False)
    below_20.to_csv('below_20.csv', index=False)
    accel_df.to_csv('accel_down.csv', index=False)

    # Generate plots (for local HTML output, optional)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Original Values', line=dict(color='blue', width=1), opacity=0.5))
    fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_1000'], mode='lines', name='1000 Value MA', line=dict(color='red', width=2)))
    fig1.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_5000'], mode='lines', name='5000 Value MA', line=dict(color='green', width=2)))
    fig1.update_layout(title='Values with 1000 and 5000 Value Moving Averages', xaxis_title='Timestamp', yaxis_title='Values', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), grid=dict(rows=1, columns=1), template='plotly_white')
    fig1.write_html('ma_plot.html')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['Values'], mode='lines', name='Voltage', line=dict(color='blue', width=1), opacity=0.5))
    fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['MA_5day'], mode='lines', name='5-Day Moving Average', line=dict(color='orange', width=2)))
    fig2.update_layout(title='Voltage vs. Timestamp with 5-Day Moving Average', xaxis_title='Timestamp', yaxis_title='Voltage', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), grid=dict(rows=1, columns=1), template='plotly_white')
    fig2.write_html('5day_ma_plot.html')

    return {
        'ma_1000': df['MA_1000'],
        'ma_5000': df['MA_5000'],
        'ma_5day': df['MA_5day'],
        'peaks_lows': extrema_df,
        'voltage_below_20': below_20,
        'downward_slopes': accel_df
    }

if __name__ == '__main__':
    # For local testing
    df = pd.read_csv('Sample_Data.csv')
    results = analyze_voltage_data(df)
    print("Analysis completed. Data saved to CSV files.")