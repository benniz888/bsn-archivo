from playwright.sync_api import sync_playwright
from pathlib import Path
import json
URL=Path("work.html").resolve().as_uri()
def boot(p): p.goto(URL); p.wait_for_load_state("load"); p.wait_for_timeout(400)
def solve(p,n):
    for _ in range(n):
        p.evaluate("""()=>{for(let i=0;i<3;i++)for(let j=0;j<3;j++){if(GB.ans[i][j]===null){
          const c=GB.sol[i][j].find(x=>!GB.used.has(x.n));if(!c)return;GB.sel=[i,j];
          document.querySelector('#gInput').disabled=false;
          document.querySelector('#gInput').value=c.n;submitGuess();return}}}""")
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True)

    print("=== A. tab left open across midnight ===")
    c=b.new_context(timezone_id="America/Puerto_Rico"); p=c.new_page()
    p.add_init_script("""(()=>{const F=Date;let fx=new F('2026-09-02T23:55:00').getTime();
      window.__adv=ms=>{fx+=ms};
      window.Date=class extends F{constructor(...a){if(!a.length)super(fx);else super(...a)}
        static now(){return fx}};Object.setPrototypeOf(window.Date,F);})();""")
    boot(p); p.evaluate("()=>document.querySelector(\"nav button[data-tab='juega']\").click()"); p.wait_for_timeout(200)
    before=p.evaluate("()=>({day:todayStamp(),puzzle:puzzleNo(),rows:GB.rows.join()})")
    solve(p,3)
    p.evaluate("()=>window.__adv(15*60*1000)")   # cross midnight
    solve(p,2)
    after=p.evaluate("()=>({day:todayStamp(),puzzle:puzzleNo(),rows:GB.rows.join(),filled:GB.ans.flat().filter(Boolean).length})")
    keys=p.evaluate("()=>Object.keys(localStorage).filter(k=>k.startsWith('bsn:grid'))")
    print(" before midnight:",before)
    print(" after  midnight:",after)
    print(" keys written:",keys)
    # now reload as the new day
    boot(p); p.evaluate("()=>document.querySelector(\"nav button[data-tab='juega']\").click()"); p.wait_for_timeout(300)
    print(" on reload -> puzzle:",p.evaluate("()=>puzzleNo()"),"| filled:",p.evaluate("()=>GB.ans.flat().filter(Boolean).length"),
          "| notice shown:",p.evaluate("()=>!!document.getElementById('gNote')"))
    c.close()

    print("=== B. do old daily keys ever get cleaned up? ===")
    c2=b.new_context(); p2=c2.new_page()
    p2.add_init_script("""(()=>{const d={};for(let i=1;i<=400;i++){
      const dt=new Date(Date.UTC(2025,0,i));
      const k='bsn:grid:'+dt.toISOString().slice(0,10);
      d[k]=JSON.stringify({v:1,rows:['a','b','c'],cols:['d','e','f'],ans:[[null,null,null],[null,null,null],[null,null,null]]});}
      for(const k in d)localStorage.setItem(k,d[k]);})();""")
    boot(p2); p2.evaluate("()=>document.querySelector(\"nav button[data-tab='juega']\").click()"); p2.wait_for_timeout(300)
    print(" seeded 400 old day-keys; after a full session run:",
          p2.evaluate("()=>Object.keys(localStorage).filter(k=>k.startsWith('bsn:grid')).length"),"remain")
    print(" total bsn bytes:",p2.evaluate("()=>Object.keys(localStorage).filter(k=>k.startsWith('bsn:')).reduce((s,k)=>s+k.length+localStorage.getItem(k).length,0)"))
    c2.close()

    print("=== C. keyboard + a11y spot check ===")
    c3=b.new_context(viewport={"width":1280,"height":900}); p3=c3.new_page(); boot(p3)
    print(" imgs without alt:",p3.evaluate("()=>[...document.querySelectorAll('img')].filter(i=>!i.getAttribute('alt')).length"))
    print(" buttons with no accessible name:",p3.evaluate("""()=>[...document.querySelectorAll('button')]
      .filter(b=>!b.textContent.trim()&&!b.getAttribute('aria-label')).length"""))
    print(" aria-live regions:",p3.evaluate("()=>document.querySelectorAll('[aria-live]').length"))
    print(" search results keyboard-reachable:",p3.evaluate("""()=>{const r=document.querySelectorAll('#gsRes .res');
      return r.length===0?'n/a (empty)':[...r].every(e=>e.tabIndex>=0||e.tagName==='BUTTON'||e.tagName==='A')}"""))
    p3.fill("#gs","torres"); p3.wait_for_timeout(300)
    print(" after typing, results are:",p3.evaluate("""()=>{const r=[...document.querySelectorAll('#gsRes .res')];
      return r.length? r[0].tagName+' tabIndex='+r[0].tabIndex : 'none'}"""))
    c3.close()
    b.close()
