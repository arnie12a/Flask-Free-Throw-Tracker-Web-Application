from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import create_engine
from io import BytesIO
from matplotlib import pyplot as plt

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
    #all_data = Data.query.all()
    db_conn_str = 'mysql://root:''@localhost/db2'
    db_conn = create_engine(db_conn_str)
    df = pd.read_sql('SELECT * FROM data', con=db_conn)
    fig, ax = plt.subplots()
    plt.scatter(df['ft_attempted'], df['ft_made'])
    plt.title("Free Throws Made vs Free Throws Attempted", fontdict={
        'fontname': 'Comic Sans MS', 'fontsize': 20})
    plt.xlabel("FT attempted", fontdict={'fontname': 'Comic Sans MS'})
    plt.ylabel("FT made", fontdict={'fontname': 'Comic Sans MS'})
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})


if __name__ == "__main__":
    app.run(debug=True)
