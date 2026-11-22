#!/usr/bin/env python3
"""Start/stop this local-only OpenCut checkout; no login startup registration."""
from pathlib import Path
import os, signal, subprocess, sys, time, urllib.request
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.local'; STATE.mkdir(exist_ok=True)
URL='http://127.0.0.1:3210/projects'
PID=STATE/'server.pid'
def ready():
    try:
        with urllib.request.urlopen(URL,timeout=2) as r: return r.status==200
    except Exception:return False
if '--stop' in sys.argv:
    if PID.exists():
        pid=int(PID.read_text())
        cmd=subprocess.run(['/bin/ps','-p',str(pid),'-o','command='],capture_output=True,text=True).stdout
        if str(ROOT) in cmd:
            os.killpg(pid,signal.SIGTERM)
            print('OpenCut 已停止。')
        else:print('记录的进程已结束；未停止其他进程。')
        PID.unlink(missing_ok=True)
    else:print('没有本启动器管理的服务。')
    raise SystemExit()
if not ready():
    bun=ROOT/'.local-runtime/node_modules/.bin/bun'
    if not bun.exists():raise SystemExit('缺少本地 Bun，请先按本地使用说明安装依赖。')
    env=dict(os.environ,NEXT_TELEMETRY_DISABLED='1',PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:'+os.environ.get('PATH',''))
    with (STATE/'server.log').open('ab') as log:
        p=subprocess.Popen([str(bun),'run','dev','--hostname','127.0.0.1','--port','3210'],cwd=ROOT/'apps/web',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    PID.write_text(str(p.pid))
    for _ in range(60):
        if ready():break
        if p.poll() is not None:raise SystemExit('启动失败，请查看 .local/server.log')
        time.sleep(1)
    else:raise SystemExit('启动仍未就绪，请查看 .local/server.log')
print('OpenCut 已启动：'+URL)
if '--no-open' not in sys.argv:
    subprocess.run(['/usr/bin/open','-a','Google Chrome',URL],check=True)
