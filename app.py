import dash
import dash_daq as daq
import sqlite3
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output


staticDischarge = 52
NPSHRlimit = 7
sealevel = 10.3


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

con = sqlite3.connect("db.sqlite3", check_same_thread=False)

body = dbc.Container(
	[
		dbc.Row(
			[
				dbc.Col(
					[
						html.Div("Energy Performance Indicators (EPIs)",  style={'fontSize': 20, 'text-align':'center', 'font-weight':'bold'}),
						html.Div(id='live-update-text'),
						html.Div("Status",  style={'fontSize': 20, 'text-align':'center', 'font-weight':'bold'}),
						html.Div(id='live-update-status'),
					],
				),
				dbc.Col(
					[
						html.Div("Live Monitoring",  style={'fontSize': 20, 'text-align':'center', 'font-weight':'bold'}),
						daq.LEDDisplay(
						id='my-LED-power',
						label="Actual Pump Power Consumption (kW) ",
						color="#FF5E5E",
						size=15,
						),
					daq.LEDDisplay(
						id='my-LED-flow',
						label="Discharge Flow Rate (Cubic metre per Hour) ",
						color="#FF5E5E",
						size=15,
						),
					daq.LEDDisplay(
						id='my-LED-flow2',
						label="Suction Flow Rate (Cubic metre per Hour) ",
						color="#FF5E5E",
						size=15,
						),
					daq.LEDDisplay(
						id='my-LED-pressure',
						label="Measured Discharge Head (m of Head) ",
						color="#FF5E5E",
						size=15,
						),
					daq.LEDDisplay(
						id='my-LED-pressure2',
						label="Measured Suction Head (m of Head) ",
						color="#FF5E5E",
						size=15,
						),

					],		
				),	
			],
			className="mt-4",		
		),
		dbc.Row(
			[
				dbc.Col(
					[
						html.Div("Consumption, Cost, and CO2 Emissions",  style={'fontSize': 20, 'text-align':'center', 'font-weight':'bold'}),
						html.Div(id='live-update-text2')
					]
				),
				dbc.Col(
					[
						html.Div("Performance Classification",  style={'fontSize': 20, 'text-align':'center', 'font-weight':'bold'}),
						html.Div(id='live-update-text3')
					]
				)
			]
		),

		dbc.Row(
			[
				dbc.Col(
					[dcc.Graph(id='live-graph-efficiency', animate=False)]
					),
				dbc.Col(
					[dcc.Graph(id='live-energy-breakdown', animate=False)]
					),
			])
	],
	className = "mt-4",
)



def serve_layout():
	return(html.Div([
    	html.Div('Pump Energy Efficiency Dashboard', style={'fontSize': 35, 'text-align':'center', 'font-weight':'bold'}),
    	html.Div([body]),
		html.Div('This site is updated for every 10 seconds', style={'text-align':'center'}),
    	dcc.Interval(
         	id='updater',
         	interval=10*1000,
         	n_intervals=0
			)
	]))

app.layout = serve_layout

@app.callback(Output('live-update-text', 'children'),
              [Input('updater', 'n_intervals')])
def update_metrics(n):
	df = pd.read_sql_query("SELECT consumptionElectric, costElectric, emittedCO2, displacedFluids  FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	style = {'padding': '5px', 'fontSize': '20', 'text-align':'center'}
	return [
        html.P('kWh/m3:   {0:.3f} '.format(df.iat[0,0]/df.iat[0,3]), style=style),
        html.P('€/m3:   {0:.3f}'.format(df.iat[0,1]/df.iat[0,3]), style=style),
        html.P('kg CO2/m3:   {0:0.3f}'.format(df.iat[0,2]/df.iat[0,3]), style=style)
    ]

@app.callback(Output('live-update-status', 'children'),
              [Input('updater', 'n_intervals')])
def update_metrics(n):
	df = pd.read_sql_query("SELECT flow, flow2, pressure2, pressure  FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	style = {'padding': '5px', 'fontSize': '20', 'text-align':'center'}
	if df.iat[0,1]-df.iat[0,0]>1.5:
		stylestatus = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color':'#f5c515'}
		status = 'Possible Serious Pump Recirculation or Leakage Detected'
	else:
		stylestatus = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color':'#3cbf0c'}
		status = 'Negligible Recirculation and Leakage'

	if sealevel-df.iat[0,2]<NPSHRlimit:
		stylestatus2 = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color':'#f5c515'}
		status2 = 'Cavitation Warning'
	else:
		stylestatus2 = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color':'#3cbf0c'}
		status2 = 'Suction Pressure at Safe Range'

	if df.iat[0,3]<staticDischarge:
		stylestatus3 = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color':'#f5c515'}
		status3 = 'Possible Pumping Failure Detected'
	else:
		stylestatus3 = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color':'#3cbf0c'}
		status3 = 'Pumping System OK'

	return [
        html.Div(status, style=stylestatus),
		html.Div(status2, style=stylestatus2),
		html.Div(status3, style=stylestatus3),
    ]

@app.callback(Output('my-LED-pressure', 'value'),
              [Input('updater', 'n_intervals')])

def update_gauge(n):
	df = pd.read_sql_query("SELECT pressure FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	value =  "{0:.3f}".format(df.iat[0,0])
	return value

@app.callback(Output('my-LED-pressure2', 'value'),
              [Input('updater', 'n_intervals')])

def update_gauge(n):
	df = pd.read_sql_query("SELECT pressure2 FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	value =  "{0:.3f}".format(-1*df.iat[0,0])
	return value


@app.callback(Output('my-LED-power', 'value'),
              [Input('updater', 'n_intervals')])

def update_gauge(n):
	df = pd.read_sql_query("SELECT power FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	value = "{0:.3f}".format(df.iat[0,0])
	return value

@app.callback(Output('my-LED-flow', 'value'),
              [Input('updater', 'n_intervals')])

def update_gauge(n):
	df = pd.read_sql_query("SELECT flow FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	value = "{0:.3f}".format(df.iat[0,0])
	return value

@app.callback(Output('my-LED-flow2', 'value'),
              [Input('updater', 'n_intervals')])

def update_gauge(n):
	df = pd.read_sql_query("SELECT flow2 FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	value = "{0:.3f}".format(df.iat[0,0])
	return value




@app.callback(Output('live-update-text2', 'children'),
              [Input('updater', 'n_intervals')])
def update_metrics(n):
	df = pd.read_sql_query("SELECT consumptionElectric, costElectric, emittedCO2  FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	style = {'padding': '5px', 'fontSize': '20', 'text-align':'center'}
	return [
        html.P('Daily Electricity Consumption: {0:.3f} kWh'.format(df.iat[0,0]), style=style),
        html.P('Daily Electricity Cost: € {0:.3f}'.format(df.iat[0,1]), style=style),
        html.P('Daily CO2 Emissions: {0:0.3f} kg CO2'.format(df.iat[0,2]), style=style)
    ]

@app.callback(Output('live-update-text3', 'children'),
              [Input('updater', 'n_intervals')])
def update_metrics(n):
	df = pd.read_sql_query("SELECT efficiencyOverall, efficiencyHydraulic  FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	style = {'padding': '5px', 'fontSize': '20', 'text-align':'center'}
	if df.iat[0,0]>=70:
		stylegrade = {'padding': '1px', 'fontSize': '20px', 'text-align':'center', 'background-color':'#026e14'}
		grade = 'Grade A : Excellent'
	elif df.iat[0,0] < 70 and df.iat[0,0] >= 65:
		stylegrade = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color': '#54a621'}
		grade = 'Grade B : Good'
	elif df.iat[0,0] < 65 and df.iat[0,0] >= 50:
		stylegrade = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color': '#50d900'}
		grade = 'Grade C : OK' 
	elif df.iat[0,0] < 50 and df.iat[0,0] >= 40:
		stylegrade = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color': '#d9d500'}
		grade = 'Grade D : Bad'
	else:
		stylegrade = {'padding': '1px', 'fontSize': '15px', 'text-align':'center', 'background-color': '#d94100'}
		grade = 'Grade E : Poor'
	return [
        html.P('Overall Efficiency: {0:.3f} %'.format(df.iat[0,0]), style=style),
        html.P('Pump Efficiency: {0:.3f} %'.format(df.iat[0,1]), style=style),
		html.Div( grade, style=stylegrade)
    ]



@app.callback(Output('live-graph-efficiency', 'figure'),
              [Input('updater', 'n_intervals')])
def update_graph(n):
	df = pd.read_sql_query("SELECT pump_time, efficiencyOverall FROM myapp_pump", con)

	data = go.Scatter(
            x=df['pump_time'],
            y=df['efficiencyOverall'],
            name='Pump efficiency',
            mode= 'markers',
			marker= dict(
            color='Red',
            line= dict(
                color='Red',
                width=1
            )
            ))
	return {'data': [data],
                'layout': {
                'yaxis': {'title' : '% Efficiency', 'showticklabels' : True, 'range':[50,100]},
				'xaxis': {'showticklabels' : True},
                'title': 'Pump Overall Efficiency Over Time',
				'showlegend' : False,
                'margin': go.layout.Margin(l=100, r=100, b=100, t=100,pad=5),
				'uirevision': 'Pump efficiency',
            }}

@app.callback(Output('live-energy-breakdown', 'figure'),
              [Input('updater', 'n_intervals')])
def update_graph(n):
	df = pd.read_sql_query("SELECT efficiencyHydraulic, efficiencyPiping, efficiencyOverall, consumptionElectric FROM myapp_pump ORDER BY id DESC LIMIT 1", con)
	pumpingLoss = (df.iat[0,3]*0.96)*(1-df.iat[0,0]/100)
	frictionLoss = (df.iat[0,3]*0.96*df.iat[0,0]/100)*(1-df.iat[0,1]/100)
	motorLoss = (0.04)*df.iat[0,3]
	usefulWork = df.iat[0,2]*df.iat[0,3]/100
	labels=['Pumping Loss', 'Friction Loss','Motor Loss', 'Useful Work']    
	data = go.Pie(labels=labels,values= [pumpingLoss, frictionLoss, motorLoss, usefulWork])
	return {'data': [data],
                'layout': {
                'title': 'Electrical Energy Breakdown',
				'showlegend' : True,
                'margin': go.layout.Margin(l=100, r=100, b=100, t=100,pad=5)				
            }}

if __name__ == '__main__':
    app.run_server(debug=True)

