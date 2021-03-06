from turtle import color
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import create_engine
from io import BytesIO
from matplotlib import pyplot as plt
import numpy as np

app = Flask(__name__)
app.secret_key = "Secret Key"

# SQLAlchemy Database Configurarion with MySql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/db2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Creating model table for out free throw data base


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    ft_made = db.Column(db.Integer)
    ft_attempted = db.Column(db.Integer)
    location = db.Column(db.String(100))

    def __init__(self, id, year, month, day, ft_made, ft_attempted, location):
        self.id = id
        self.year = year
        self.month = month
        self.day = day
        self.ft_made = ft_made
        self.ft_attempted = ft_attempted
        self.location = location


@app.route('/')
def Index():
    db_conn_str = 'mysql://root:''@localhost/db2'
    db_conn = create_engine(db_conn_str)
    df = pd.read_sql('SELECT * FROM data', con=db_conn)
    made = df["ft_made"].sum()
    total = df["ft_attempted"].sum()
    if total == 0 or None:
        output = "You have not had a Shooting Session!"
    else:
        proportion = float(made)/float(total)
        percent = round(proportion, 3)*100
        output = "Your Free Throw Percentage: " + str(percent) + "%"

    all_data = Data.query.all()
    return render_template('index.html', FTsessions=all_data, FTaverage=output)


@app.route('/stats')
def stats():
    db_conn_str = 'mysql://root:''@localhost/db2'
    db_conn = create_engine(db_conn_str)
    df = pd.read_sql('SELECT * FROM data', con=db_conn)

    alter_lst = []
    all_locations = df['location']
    for loc in all_locations:
        alter_lst.append(loc.lower())
    df['location'] = alter_lst

    new_lst = []
    for loc in df['location']:
        new_lst.append(loc.lower())

    percent_per_location = {}
    locations = list(set(new_lst))
    for location in locations:
        newdf = df[df['location'] == location]
        made = newdf['ft_made'].sum()
        total = newdf['ft_attempted'].sum()
        percent = round(made/total, 2) * 100
        percent_per_location[location] = percent

    lst_percentiles = sorted(percent_per_location.items(),
                             key=lambda x: x[1], reverse=True)
    percent_per_loc_sorted = dict(lst_percentiles)

    df_tail = df.tail()

    made = df_tail['ft_made'].sum()
    total = df_tail['ft_attempted'].sum()
    last5 = round(made/total, 2) * 100

    total_made = df['ft_made'].sum()
    total_total = df['ft_attempted'].sum()
    total_percent = round(total_made/total_total, 2) * 100

    return render_template('stats.html', sorted_dict=percent_per_loc_sorted, last5=last5, shootingPercentage=total_percent)


@app.route('/insert', methods=['POST'])
def insert():

    if request.method == 'POST':
        id = request.form['id']
        year = request.form['year']
        month = request.form['month']
        day = request.form['day']
        fmade = request.form['FT_made']
        fattempted = request.form['FT_attempted']
        location = request.form['location']

        my_data = Data(id, year, month, day, fmade, fattempted, location)
        db.session.add(my_data)
        db.session.commit()

        flash("Free Throw Session Inserted Successfully")

        return redirect(url_for('Index'))


@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Free Throw Session Deleted Successfully")

    return redirect(url_for('Index'))


@app.route('/dashboard.svg')
def dash():
    db_conn_str = 'mysql://root:''@localhost/db2'
    db_conn = create_engine(db_conn_str)
    df = pd.read_sql('SELECT * FROM data', con=db_conn)
    fig, ax = plt.subplots(figsize=(9, 6))

    y = np.array(df['ft_made'].to_list())
    x = np.array(df['ft_attempted'].to_list())
    m, b = np.polyfit(x, y, 1)
    line = m*x + b
    plt.plot(x, line, label='Line of Best Fit',
             color="red", linestyle='dashed')

    plt.scatter(df['ft_attempted'], df['ft_made'],
                s=60, alpha=0.7, edgecolor='k')
    plt.title("Free Throws Made vs Free Throws Attempted", fontdict={
        'fontname': 'Comic Sans MS', 'fontsize': 20})
    plt.xlabel("FT attempted", fontdict={'fontname': 'Comic Sans MS'})
    plt.ylabel("FT made", fontdict={'fontname': 'Comic Sans MS'})
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})


@app.route('/semiPieChart.svg')
def semichart():
    db_conn_str = 'mysql://root:''@localhost/db2'
    db_conn = create_engine(db_conn_str)
    df = pd.read_sql('SELECT * FROM data', con=db_conn)
    FT_Made = df['ft_made'].sum()
    FT_Missed = df['ft_attempted'].sum() - FT_Made
    labels = ['FT Made', 'FT Missed']
    vals = [FT_Made, FT_Missed]
    colors = ['green', 'red']
    explode = (0.2, 0.1)
    fig = plt.figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    patches, texts, pcts = ax.pie(vals, labels=labels, colors=colors, explode=explode, autopct='%.01f%%',
                                  wedgeprops={'linewidth': 3.0,
                                              'edgecolor': 'white'},
                                  textprops={'size': 'x-large'})
    plt.setp(pcts, color='white', fontweight='bold')
    #ax.set_title('Free Throw Shooting Distribution', fontsize=18)
    plt.tight_layout()
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})


if __name__ == "__main__":
    app.run(debug=True)
