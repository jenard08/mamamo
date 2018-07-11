
import subprocess
import re
import datetime
import time

from flask import Flask, render_template, request, url_for, redirect
app = Flask(__name__)


def ping(myUrl):
    ping = subprocess.Popen(
        ["ping", myUrl],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, error = ping.communicate()
    match = re.search('(\d+\.\d+\.\d+\.\d+)', out)
    ip = match.group(0)
    return out

def tracert(myUrl):
    tracert = subprocess.Popen(
        ["tracert", myUrl],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, error = tracert.communicate()
    match = re.search('(\d+\.\d+\.\d+\.\d+)', out)
    ip = match.group(0)
    return out



def nslookup(myUrl):
    nslookup = subprocess.Popen(
        ["nslookup", myUrl],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    out, error = nslookup.communicate()
    match = re.search('(\d+\.\d+\.\d+\.\d+)', out)
    ip = match.group(0)
    return out

def netstat():
    netstat = subprocess.Popen(
        "netstat -r".split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, error = netstat.communicate()

    return out

@app.route('/', methods=['GET', 'POST'] )
def index_page():
    error =None # para macheck if may error no filename inputted and destination inputted

    if request.method == 'POST':
        if request.form['filename'] == "" and request.form['destine'] == "":
            error = 'Check whether you provide a filename or destination URL'

        else:
            return redirect(url_for('main'), code=307)
    return render_template('trend.html', error=error)

@app.route('/success',methods=['POST'])
def main():

    fname = request.form['filename']
    myUrl = request.form['destine']

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print "Network status report as of " + st

    ping_res = ping(myUrl).replace('\r\n', '<br/>')
    print "Ping complete"

    trace_res = tracert(myUrl).replace('\r\n', '<br/>')
    print "Tracert Complete"

    nslookup_res = nslookup(myUrl).replace('\r\n', '<br/>')
    print "Nslookup complete"

    netstat_res = netstat().replace('\r\n', '<br/>')
    print "Netstat complete"

    data = st, ping_res, trace_res, nslookup_res, netstat_res

    return render_template('loader.html', data=data)

if __name__ == '__main__':
   app.run(debug = True)
