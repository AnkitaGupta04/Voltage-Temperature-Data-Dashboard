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
    
    # Handle empty voltage_below_20 with a message
    voltage_below_20_html = analysis_results['voltage_below_20'].to_html(classes='table table-striped') if not analysis_results['voltage_below_20'].empty else '<p class="text-gray-600">No values below 20</p>'
    
    return render_template('index.html', plot1_div=plot1_div, plot2_div=plot2_div,
                          peaks_lows=analysis_results['peaks_lows'].to_html(classes='table table-striped'),
                          voltage_below_20=voltage_below_20_html,
                          downward_slopes=analysis_results['downward_slopes'].to_html(classes='table table-striped'))

if __name__ == '__main__':
    app.run(debug=True)