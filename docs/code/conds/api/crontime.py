from rocketry.conds import crontime

@app.task(crontime('* * * * *'))
def do_minutely():
    ...

@app.task(crontime('*/2 12-18 * Oct Fri'))
def do_complex():
    "Run at every 2nd minute past every hour from 12 through 18 on Friday in October."
    ...