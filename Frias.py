
import subprocess
import re
import datetime
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, render_template, request, url_for, redirect
app = Flask(__name__)


g_data = ""

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

def main():
    #fname = request.form['filename']
    myUrl = request.form.get('destine')

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('Network status report as of %Y-%m-%d %H:%M:%S' '<br/>')
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

    return data

@app.route('/', methods=['GET', 'POST'])
def index_page():
    error =None # para macheck if may error no filename inputted and destination inputted

    if request.method == 'POST':
        if request.form.get("email") == "" or request.form.get("destine") == "":
            error = 'Please fill up all the text field.'
        else:
            return redirect(url_for('success'), code=307)
    return render_template('trend.html', error=error)

@app.route('/success',methods=['POST'])
def success():

    global g_data
    g_data = main()

    return render_template('loader.html', data=g_data)

@app.route('/email')
def email():

    try:
        #need to verify on this
        me = request.form.get("email")
        you = "Matthew_Flores@trendmicro.com"
        cc = request.form.get("email")

        msg = MIMEMultipart('related')
        msg['Subject'] = "Trend Micro: Network Diagnostic Tool result"
        msg['From'] = me
        msg['To'] = you

        html = "<html><body><p>" + str(g_data) + "</p><body></html>"

        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        s = smtplib.SMTP('sjc1-rly.sdi.trendmicro.com')
        s.sendmail(me, [you, cc], msg.as_string())
        s.quit()
        print 'email sent!'

        return render_template('email.html')

    except Exception as e:
        return str(e)

if __name__ == '__main__':
   app.run(debug = True)
