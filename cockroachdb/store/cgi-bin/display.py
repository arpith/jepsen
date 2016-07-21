#! /usr/bin/env python3
import cgi
import cgitb
import os
import sys
import glob
import re
import urllib
import edn_format
import datetime
import humanize
import fnmatch
cpath = os.getenv("SCRIPT_NAME")

cgitb.enable()

form = cgi.FieldStorage()

base = os.path.realpath(os.getenv("DOCUMENT_ROOT"))
os.chdir(base)
path = ''
if 'path' in form:
    path = form.getvalue('path')
repath = os.path.realpath(path)
    
if len(path) == 0 or not repath.startswith(base):
    path = '.'

offset = 0
if 'offset' in form:
    offset = int(form.getvalue('offset'))

pgsize = 10
if 'pgsize' in form:
    pgsize = int(form.getvalue('pgsize'))

filter = '*'
if 'filter' in form:
    filter = form.getvalue('filter')
    
entry = None
if 'entry' in form:
    entry = form.getvalue('entry')
    
def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))  

self_ext = ['edn', 'stderr']

def reltime(ts):
    # format is YYMMDDTHHMMSS
    y = int(ts[:4]   ) 
    m = int(ts[4:6]  )
    d = int(ts[6:8]  )
    H = int(ts[9:11] )
    M = int(ts[11:13])
    S = int(ts[13:15])
    return humanize.naturaltime(datetime.datetime(y,m,d,H,M,S))

if path.split('.')[-1] in self_ext:
    print("Content-Type: text/plain;charset=utf-8\n")

    with open(path) as f:
        contents = f.read().replace(r'\n','\n')
        print(contents)

elif 'merge-logs' in form:
    r = re.compile('.*/cockroachdb/cockroach/')
    logfiles = glob.glob(os.path.join(path, "*/cockroach.stderr"))
    sources = []
    for l in logfiles:
        nodename = l.split('/')[-2]
        dl = []
        with open(l) as f:
            for line in f:
                if line[0] in 'IWEF':
                    x = line.rstrip().split(' ', 3)
                    dl.append( (nodename, x[0][0], x[0][1:]+'-'+x[1],r.sub('',x[2]),x[3]))
        sources.append(dl)
    data = []
    pos = [0 for i in sources]
    while True:
        exhausted = True

        lowest = -1
        row = None
        minval = '999999-99:99:99.999999'
        for s,sd in enumerate(sources):
            if pos[s] < len(sd):
                exhausted = False
                v = sd[pos[s]]
                if v[2] < minval:
                    lowest = s
                    minval = v[2]
                    row = v
        if not exhausted:
            assert lowest >= 0
            assert row is not None
            data.append(row)
            pos[lowest] += 1
        if exhausted:
            break
        
    print("Content-Type: text/html;charset=utf-8\n")
    print("""<!DOCTYPE html>
    <html lang=en>
    <head>
    <title>CockroachDB Jepsen merged time log</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
    <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script></head>
    <body><div class="container-fluid">
    <style type=text/css>
    td { font-family: monospace !important; }
    .hr { height: 3px; color: solid black; }
    </style>""")

    print("<h1>Merged log for " + path + "</h1>")
    print("""<table class='table table-condensed table-hover table-responsive'>""")

    sd = {'I':'info','W':'warning','E':'danger','F':'danger'}

    prev = None
    for d in data:
        status = sd[d[1]]
        if prev != d[0]:
            if prev is not None:
                print("<tr><td colspan=4></td></tr>")
            prev = d[0]
        print("<tr class=%s>" % status)
        print(''.join( ("<td>%s</td>" %s for s in d) ))
        print("</tr>")
    print("</table></div></body></html")
              

                         

elif 'grep-err' in form:
    print("Content-Type: text/plain;charset=utf-8\n")

    with open(path) as f:
        for l in f:
            if 'ERROR' in l:
                print(l)


elif 'version-details' in form:
    import re
    urlver = re.compile(r'^\s*(\S+)\s+(\S+)\s*$')
    print("Content-Type: text/html;charset=utf-8\n")
    print("""<!DOCTYPE html><html lang=en><body><pre>""")
    with open(path) as f:
        for l in f:
            l = l.rstrip()
            m = urlver.match(l)
            if m is None or "/" not in l:
                print(l)
            else:
                print("<a target='_blank' href='http://" + m.group(1) + "/tree/" + m.group(2) + "'>" + l + "</a>", end='')
                if 'cockroachdb/cockroach' in l: print("<strong>&lt;--- here</strong>", end='')
                print()
    print("""</pre></body></html>""")

elif path == '.':
    
    print("Content-Type: text/html;charset=utf-8\n")
    print("""<!DOCTYPE html>
    <html lang=en>
    <head>
    <title>CockroachDB Jepsen test results</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
    <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script></head>
    <body><div class="container-fluid">
    <h1>CockroachDB Jepsen test results</h1>
    <p class=lead>Welcome</p>
    <p class='alert alert-info'>For test descriptions, refer to <a href="https://github.com/cockroachdb/jepsen/blob/master/cockroachdb/README.rst">the README file</a>.
    <br/>
    <strong>Note</strong><br/>These tests are run irregularly.<br/>
    They may not use the latest code from the main CockroachDB repository.<br/>
    Some tests are run using unmerged change sets.<br/>
    <strong>Always refer to the Version column to place test results in context.</strong>
    </p>
    <style type=text/css>
    .table > tbody > tr > td { vertical-align: middle !important; }
    .selected > * { background-color: yellow !important; }
    </style>""")

    if filter != '*':
        print("<strong>Currently filtering on " + filter + ". <a href='" + cpath + "' class='btn btn-info'>Reset filter</a></p>")

    rl = sorted((x.split('/') for x in glob.glob('*/20*/results.edn') if fnmatch.fnmatch(x, filter+'/*')), key=lambda r:r[1],reverse=True)

    nemeses = sorted(set((x[0].split(':',1)[1] for x in rl if ':' in x[0])))
    tests = sorted(set((x[0].split(':',1)[0] for x in rl if ':' in x[0])))
    print("<h2>Overview of latest test results per test/nemesis combination</h2>")
    print("<table class='table table-striped table-hover table-responsive'><thead><tr><th>Test</th>")
    for n in nemeses:
        print("<th><a href='" + cpath + "?filter=*:" + n + "'>" +  n + "</a></th>")
    print("</tr></thead><tbody>")
    for t in tests:
        print("<tr><td><a href='" + cpath + "?filter=" + t + ":*'>" + t.replace("cockroachdb-","") + "</a></td>")
        for n in nemeses:
            print("<td>")
            tn = t + ':' + n
            dr = sorted([x for x in rl if x[0] == tn])
            if len(dr) > 0:
                d = dr[-1]
                dpath = os.path.join(d[0],d[1])
                ednpath = os.path.join(dpath, 'results.edn')
                with open(ednpath) as f:
                    r = edn_format.loads(f.read())
                    if r is not None:
                        ok = r[edn_format.Keyword('valid?')]
                        status = {True:'success',False:'danger'}[ok]
                        ts = d[1][:-5]
                        #lfile = os.path.join(dpath, "latency-raw.png")
                        #if os.path.exists(lfile):
                        #    print("<a href='/" + lfile + "'>" 
                        #          "<img height=60px src='/" + lfile + "' />"
                        #          "</a>")
                        print("<a href='" + cpath + "?entry=" + ts + "#" + ts + "' class='btn btn-%s btn-xs'>" % status + reltime(ts) +
                              ' <span class="glyphicon glyphicon-info-sign"></span>'
                              "</a>")
            print("</td>")
        print("</tr>")
    print("</tbody></table>")

    print("<h2>Latest test results in chronological order</h2>")
    rpgsize = pgsize
    if pgsize == -1:
       rpgsize = len(rl)
    if entry is not None:
        for i,v in enumerate(rl):
            if entry in v[1]:
                offset=i
                break
    if offset < 0:
        offset = 0
    elif offset >= len(rl):
        offset = len(rl)-1
    upper = min(offset + rpgsize, len(rl))
        
    if offset > 0:
        print("<a href='" + cpath + "?offset=0&pgsize=%d&filter=%s' class='btn btn-info'>First</a>" % (pgsize,filter))
        print("<a href='" + cpath + "?offset=%d&pgsize=%d&filter=%s' class='btn btn-info'>Previous %d</a>" % (max(offset-rpgsize, 0), pgsize, filter, rpgsize))
    print("<strong>Viewing entries", offset, "to", upper-1,"</strong>")
    if offset < (len(rl) - pgsize):
        print("<a href='" + cpath + "?offset=%d&pgsize=%d&filter=%s' class='btn btn-info'>Next %d</a>" % (max(min(offset+rpgsize, len(rl)-1), 0), pgsize, filter, rpgsize))
        print("<a href='" + cpath + "?offset=%d&pgsize=%d&filter=%s' class='btn btn-info'>Last</a>" % (max(len(rl)-rpgsize,0),pgsize, filter))
    print("Number of entries per page: ")
    print("<a href='" + cpath + "?offset=%d&pgsize=10&filter=%s' class='btn btn-info'>10</a>" % (offset, filter))
    print("<a href='" + cpath + "?offset=%d&pgsize=50&filter=%s' class='btn btn-info'>50</a>" % (offset, filter))
    print("<a href='" + cpath + "?offset=%d&pgsize=100&filter=%s' class='btn btn-info'>100</a>" % (offset, filter))
    print("<a href='" + cpath + "?offset=%d&pgsize=-1&filter=%s' class='btn btn-info'>All</a>" % (offset, filter))
        
    print("""
    <table class="sortable table table-striped table-hover table-responsive"><thead><tr>
    <th></th>
    <th>Timestamp</th>
    <th>Status</th>
    <th>Type</th>
    <th>Events</th>
    <th>Errors</th>
    <th>Latencies</th>
    <th>Rates</th>
    <th>Version</th>
    <th>Details</th>
    <th>Node logs</th>
    <th>Network traces</th>
    </tr></thead><tbody>""")
    db_lastver = None
    jt_lastver = None
    first = True
    for d in rl[offset:upper]:
        dpath = os.path.join(d[0],d[1])
        ednpath = os.path.join(dpath, 'results.edn')
        with open(ednpath) as f:
            r = edn_format.loads(f.read())
            if r is not None:
                ok = r[edn_format.Keyword('valid?')]
                status = {True:'success',False:'danger'}[ok]
                tstatus = {True:'OK',False:'WOOPS'}[ok]
                ts = d[1][:-5]

                jt_thisver = None
                jt_verfile =  os.path.join(dpath, 'jepsen-version.txt')
                if os.path.exists(jt_verfile):
                    with open(jt_verfile) as f:
                        jt_thisver = f.read().strip()
                if not first and jt_thisver != jt_lastver:
                    print("<tr class='info'><td colspan=12 class='text-center small'><strong>New Jepsen / test framework version</strong></td></tr>")
                jt_lastver = jt_thisver
                
                db_thisver = None
                dv = sorted(glob.glob(os.path.join(dpath, '*/version.txt')))
                db_version_file = None
                if len(dv) > 0:
                    db_version_file = dv[0]
                    # n = db_version_split.split('/')[-2]
                    with open(db_version_file) as vf:
                        db_thisver = vf.read().split('\n')[0].split(':')[1].strip()

                if not first and db_thisver != db_lastver:
                    print("<tr class='info'><td colspan=12 class='text-center small'><strong>New CockroachDB version</strong></td></tr>")
                first=False
                db_lastver = db_thisver
                selected = ''
                if entry is not None and ts == entry:
                    selected = 'selected'
                print("<tr class='%s %s' id='%s'>" % (status, selected, ts))
                # Anchor
                print("<td>")
                print("<a href='" + cpath + "?entry=" + ts + "#" + ts + "' class='btn btn-info'>#</a></td>")
                # Timestamp
                print("<td><a href='" + cpath + "?path=" + urllib.parse.quote_plus(dpath) + "' class='btn btn-%s'>" % status + reltime(ts) +
                      ' <span class="glyphicon glyphicon-info-sign"></span>'
                      "</a></td>")
                # Status
                print("<td>" + tstatus + "</td>")
                # Type
                tn = d[0]
                print("<td><a href='" + cpath + "?filter=" + tn + "'>" + tn.split('-', 1)[1] + "</a></td>")
                # History
                print("<td>")
                hfile = os.path.join(dpath, 'history.txt')
                errs = 0
                if os.path.exists(hfile):
                    print("<a href='/" + hfile + "' class='btn btn-%s'>" % status)
                    with open(hfile) as h:
                        lines = h.read().split('\n')
                        print(len(lines), '<span class="glyphicon glyphicon-info-sign"></span>')
                        errs = sum((1 for x in lines if 'ERROR' in x))
                    print("</a>")
                print("</td>")
                # Errors
                print("<td>")
                if errs != 0:
                    print("<a href='" + cpath + "?grep-err=1&path=" + urllib.parse.quote_plus(hfile) + "' class='btn btn-%s'>" % status +
                          str(errs) + ' <span class="glyphicon glyphicon-info-sign"></span></a>')
                print("</td>")
                # Latencies
                print("<td>")
                lfile = os.path.join(dpath, "latency-raw.png")
                if os.path.exists(lfile):
                    print("<a href='/" + lfile + "'>" 
                          "<img height=60px src='/" + lfile + "' />"
                          "</a>")
                print("</td>")
                # Rates
                print("<td>")
                rfile = os.path.join(dpath, "rate.png")
                if os.path.exists(rfile):
                    print("<a href='/" + rfile + "'>" 
                          "<img height=60px src='/" + rfile + "' />"
                          "</a>")
                print("</td>")
                # Version
                print("<td>")
                if db_version_file is not None:
                    print("<a href='" + cpath + "?version-details=1&path=" + urllib.parse.quote_plus(db_version_file) +
                          "' class='btn btn-%s btn-xs'>" % status + db_thisver + 
                          " <span class='glyphicon glyphicon-info-sign'></span></a>")
                print("</td>")
                # Details
                print("<td>")
                dtk = edn_format.Keyword('details')
                if dtk not in r:
                    dtk = edn_format.Keyword('error')
                if dtk in r:
                    dstr = edn_format.dumps(r[dtk])
                    if len(dstr) > 60:
                        dstr = dstr[:60] + "... <a href='" + cpath + "?path=" + urllib.parse.quote_plus(ednpath) + "'>(more)</a>"
                    print("<tt class='small'>" + dstr + "</tt>")
                print("</td>")

                # Node logs
                print("<td>")
                print("<a href='" + cpath + "?path=" + urllib.parse.quote_plus(dpath) + "&merge-logs=1' class='btn btn-%s btn-xs'>" % status +
                      "<span class='glyphicon glyphicon-filter'></span></a>")
                logs = sorted(glob.glob(os.path.join(dpath, "*/cockroach.stderr")))
                if len(logs) > 0:
                    for log in logs:
                        print("<a href='" + cpath + "?path=" + urllib.parse.quote_plus(log) + "' class='btn btn-%s btn-xs'>" % status +
                              "<span class='glyphicon glyphicon-info-sign'></span></a>")
                print("</td>")
                # Network traces
                print("<td>")
                logs = sorted(glob.glob(os.path.join(dpath, "*/trace.pcap")))
                if len(logs) > 0:
                    for log in logs:
                        print("<a href='/" + log + "' class='btn btn-%s btn-xs'>" % status +
                              "<span class='glyphicon glyphicon-info-sign'></span></a>")
                print("</td>")
                
                print("</tr>")
    print("</tbody></table>")
    print('<script src="/sorttable.js"></script>')
    print("</div></body></html>")

elif os.path.isdir(path):
    print("Content-Type: text/html;charset=utf-8\n")
    print("""<!DOCTYPE html><html lang=en><body><ul>""")
    print("<ul>")
    print("<li><a href='" + cpath + "?path=" + urllib.parse.quote_plus('/'.join(path.split('/')[:-1])) + "'>Up one level</a>")
    for d in sorted_ls(path):
        if d == "cgi-bin":
            continue
        
        ditem = os.path.join(path, d)
        if os.path.isdir(ditem) or d.split('.')[-1] in self_ext:
            dst = cpath + "?path=" + urllib.parse.quote_plus(ditem)
        else:
            dst = "/" + ditem
        print("<li><a href='" + dst + "'>" + d + "</a></li>")
    print("</ul></body></html>")

else:
    print("Content-Type: text/plain;charset=utf-8\n")
    print("You shouldn't be here.")
