from flask import Flask, render_template, send_file, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)

LINKS = {'Home': '/',
         'Download': '/download',
         'Rooms': '/rooms',
         'Prices': '/prices',
         'Date sold': '/date',
         'Year built': '/built',
         'Distance vs year': '/distvsyear',
         'Raw data': '/raw',
         'Conclusions': '/conclusions'}

DATA_PATH = 'data/Melbourne_housing_FULL.csv'


def render_page(html_string=None, additional_info=None, errors=None, cur_filter=None, image=None):
    return render_template('index.html', links=LINKS.items(), html_string=html_string, additional_info=additional_info, errors=errors, cur_filter=cur_filter, image=image)


@app.route(LINKS['Home'], methods=['GET'])
def index():
    info = '<p style="font-size: 40px">Melbourne Housing Market</p>' \
           '<a href="https://www.kaggle.com/anthonypino/melbourne-housing-market" style="color: #0088a9; text-decoration: none;">Link to the page with dataset</a>'
    return render_page(additional_info=info)


@app.route(LINKS['Rooms'], methods=['GET'])
def rooms():
    data = pd.read_csv(DATA_PATH).dropna()
    rooms_data = data['Rooms'].apply(lambda x: '6+' if x >= 6 else str(x)).value_counts().sort_index()
    fig = px.bar(rooms_data, labels={'index': 'Number of rooms', 'value': 'Number of houses'}, width=1300, height=700, template='plotly_dark', title='Distribution of the number of rooms')
    fig.update_layout(font={'size': 20})
    rooms_description = '<br>' + 'Descriptive statistics:' + '<br>' + data['Rooms'].describe().to_frame().transpose().to_html()
    return render_page(html_string=fig.to_html(full_html=False, include_plotlyjs='cdn'), additional_info=rooms_description)


@app.route(LINKS['Prices'], methods=['GET'])
def prices():
    data = pd.read_csv(DATA_PATH).dropna()
    prices_data = data['Price'].apply(lambda x: max(200000, min(x, 2000000)))
    fig = px.histogram(prices_data, nbins=10, width=1300, height=700, template='plotly_dark', title='Histogram of prices')
    fig.update_traces(marker={'color': 'red'})
    fig.update_layout(bargap=0.1, font={'size': 20}, xaxis_title_text='Price in Australian dollars', yaxis_title_text='Number of houses')
    prices_description = '<br>' + 'Descriptive statistics:' + '<br>' + data['Price'].describe().to_frame().transpose().to_html()
    return render_page(html_string=fig.to_html(full_html=False, include_plotlyjs='cdn'), additional_info=prices_description)


@app.route(LINKS['Date sold'], methods=['GET'])
def date():
    data = pd.read_csv(DATA_PATH).dropna()
    designation = {'br': 'bedroom', 'h': 'house', 'u': 'unit', 't': 'townhouse'}
    date_data = pd.DataFrame(list(zip(data['Date'].apply(lambda s: '-'.join(s.replace('/', ' ').split()[::-1])), data['Type'].apply(lambda x: designation[x]))), columns=['Date', 'Type'])
    fig = px.histogram(date_data, x='Date', color='Type', nbins=12, width=1300, height=800, template='plotly_dark', title='Sold houses')
    # fig.update_traces(marker={'color': 'yellow'})
    fig.update_layout(bargap=0.1, font={'size': 20}, xaxis_title_text='Date', yaxis_title_text='Number of houses sold')
    date_description = None  # '<br>' + 'Descriptive statistics:' + '<br>' + data.describe().to_html()  # data['Date'].describe().to_frame().transpose().to_html()
    return render_page(html_string=fig.to_html(full_html=False, include_plotlyjs='cdn'), additional_info=date_description)


@app.route(LINKS['Year built'], methods=['GET'])
def built():
    data = pd.read_csv(DATA_PATH).dropna()
    cnt_data = [0] * 13
    cur_val = 1900
    cur_ind = 0
    labels = ['Before 1900'] + [str(1900 + i * 10) + '-' + str(1909 + i * 10) for i in range(12)]
    for x in data['YearBuilt'].sort_values():
        if x >= cur_val:
            cur_val += 10
            cur_ind += 1
        cnt_data[cur_ind] += 1
    built_data = pd.DataFrame(list(zip(cnt_data, labels)), columns=['Number', 'Period'])
    fig = px.pie(built_data, values='Number', names='Period', width=1300, height=700, template='plotly_dark', title='Year built')
    fig.update_layout(font={'size': 20})
    date_description = '<br>' + 'Descriptive statistics:' + '<br>' + data['YearBuilt'].describe().to_frame().transpose().to_html()  # data['Date'].describe().to_frame().transpose().to_html()
    return render_page(html_string=fig.to_html(full_html=False, include_plotlyjs='cdn'), additional_info=date_description)


@app.route(LINKS['Distance vs year'], methods=['GET'])
def distvsyear():
    data = pd.read_csv(DATA_PATH).dropna()
    designation = {'br': 'bedroom', 'h': 'house', 'u': 'unit', 't': 'townhouse'}
    data['Type'] = data['Type'].apply(lambda x: designation[x])
    data['Distance in km'] = data['Distance']
    dvy_data = data[['Type', 'Distance in km', 'YearBuilt']]
    fig = px.scatter(dvy_data, y='Distance in km', x='YearBuilt', color='Type', width=1300, height=700, template='plotly_dark', title='Distance from central district vs year built')
    fig.update_layout(font={'size': 20})
    dvy_description = '<br><br><br> '
    # dvy_description = '<br>' + 'Descriptive statistics:' + '<br>' + data['YearBuilt'].describe().to_frame().transpose().to_html()  # data['Date'].describe().to_frame().transpose().to_html()
    return render_page(html_string=fig.to_html(full_html=False, include_plotlyjs='cdn'), additional_info=dvy_description)


@app.route(LINKS['Raw data'], methods=['GET', 'POST'])
def rawdata():
    data = pd.read_csv(DATA_PATH)
    errors = []
    cur_filter = ""
    if request.method == "POST":
        cur_filter = request.form.get('filters')
        if cur_filter:
            try:
                print(cur_filter)
                data = data.query(cur_filter)
            except Exception as e:
                print(e)
                errors.append('Incorrect filter')

    # With more than 1000 rows the page takes too long to load
    return render_page(html_string=data.head(1000).to_html(), errors=errors, cur_filter=cur_filter)


@app.route(LINKS['Download'], methods=['GET'])
def download():
    return send_file(DATA_PATH, as_attachment=True)


@app.route(LINKS['Conclusions'], methods=['GET'])
def concl():
    conclusions = "Let's consider what one can understood from the results. Most of the houses sold in Melbourne had 3 rooms, then houses with 4  and 2 rooms respictively." \
                  " The share of apartments with 1, 5 and more than 6 room is small compared to the rest." \
                  " Although the median price is 1.1M dollars, the most popular category of houses with a price between 600k$ and 800k$." \
                  " It can be seen that the overwhelming majority of the sold real estate are houses, in second place are units and in the last are townhouses.<br>" \
                  " Despite consistent sales growth in 2016, sales declined sharply in the first quarter of 2017." \
                  ' As the author of the dataset himself said: "Melbourne is currently experiencing a housing bubble (some experts say it may burst soon".' \
                  " On the other hand, after such a sharp drop, the sales levels returned to their previous level and even surpassed the results of the last year" \
                  " and falling only in the last two quarters. But only due to a decrease in the proportion of units and townhouses, the number of houses was stable.<br>" \
                  " Half of all buildings sold were built in roughly equal proportions in 2000-2009, 1970-1979, 1960-1969 and 2010-2019" \
                  " and the oldest building sold was built in 1830." \
                  " The scatter plot clearly shows that over the past 30 years, most of the townhouses have been built," \
                  " they and units are the ones that are closest to central business district of Melbourne and actually form part of it." \
                  " Ordinary houses, however, are located at some distance and their highest density of clusters is about 15 km from the center." \
                  " One can see that over time, the area for selling real estate is expanding, which means that the business district itself is expanding over time."
    return render_page(additional_info=conclusions)


if __name__ == '__main__':
    app.run()
