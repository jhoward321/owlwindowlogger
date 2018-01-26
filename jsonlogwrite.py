from datetime import datetime

try:
    import simplejson as json
except ImportError:
    import json

def write(data, logfile):
    data = data
    data['log_timestamp'] = str(datetime.utcnow())
    if 'window_title' in data:
        data['window_title'] = data['window_title'].encode('string_escape')
    text = json.dumps(data, separators=(',',':')) #compact
    print(logfile, text)
    with open(logfile, 'a') as fp:
        fp.write(text + '\n')
