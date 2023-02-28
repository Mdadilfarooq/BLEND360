import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import datetime
import time

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(className='container', children=[
    html.H2('Store Management System', className='text-center', style={'marginTop': 20}),
    html.Div(className='form-group', children=[html.Label('Name', style={'marginTop': 20}),
        dcc.Input(id='input-name', type='text', value='', className='form-control'),
        html.Label('Amount', style={'marginTop': 20}),
        dcc.Input(id='input-amount', type='number', value=0, className='form-control'),
        html.Label('Payment Option', style={'marginTop': 20}),
        dcc.Dropdown(
            id='dropdown-payment-option',
            options=[
                {'label': 'Cash', 'value': 'cash'},
                {'label': 'Credit Card', 'value': 'credit_card'},
                {'label': 'Debit Card', 'value': 'debit_card'},
            ],
            value='cash',
            className='form-control'
        ),
        html.Button(id='submit-button', n_clicks=0, children='Submit', className='btn btn-primary', style={'marginTop': 20})
    ]),
    html.Div(id='output-message', children='', className='text-center', style={'marginTop': 20})
])

last_submit_time = time.time()
min_delay = 1

@app.callback(
    dash.dependencies.Output('output-message', 'children'),
    [dash.dependencies.Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('input-name', 'value'),
     dash.dependencies.State('input-amount', 'value'),
     dash.dependencies.State('dropdown-payment-option', 'value')]
)
def update_output(n_clicks, name, amount, payment_option):
    global last_submit_time
    current_time = time.time()
    if n_clicks == 0:
        return
    if current_time - last_submit_time < min_delay:
        return "Please wait for at least {} seconds before submitting again.".format(min_delay)
    last_submit_time = current_time
    if not name or amount <= 0:
        return "Name and Amount fields is required."
    try:
        df = pd.read_csv('dags/store_data.csv')
        new_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_entry = pd.DataFrame({
            'timestamp': [new_timestamp],
            'name': [name],
            'payment_option': [payment_option],
            'amount': [amount]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv('dags/store_data.csv', index=False)
        return 'New entry added with timestamp {}: {} - {}/{}'.format(
            new_timestamp, name, payment_option, amount
        )
    except FileNotFoundError:
        new_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df = pd.DataFrame({
            'timestamp': [new_timestamp],
            'name': [name],
            'payment_option': [payment_option],
            'amount': [amount]
        })
        df.to_csv('dags/store_data.csv', index=False)
        return 'New file created with entry added with timestamp {}: {} - {}/{}'.format(
            new_timestamp, name, payment_option, amount
        )

if __name__ == '__main__':
    app.run_server(debug=True)

