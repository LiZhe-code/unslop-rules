import json,random,os,re,concurrent.futures as cf,urllib.request,time
random.seed(20261112)
rows=[json.loads(l) for l in open('hc3_all.jsonl')]
want={'reddit_eli5':120,'finance':60,'open_qa':60,'medicine':30,'wiki_csai':30}
by={}
for r in rows:
  if r['human_answers'] and len(' '.join(r['human_answers']).split())>=40: by.setdefault(r['source'],[]).append(r)
sample=[]
for s,n in want.items(): sample+=random.sample(by[s],n)
def detok(t):
  t=re.sub(r" (n't|'s|'re|'ve|'ll|'d|'m)\b",r"\1",t); t=re.sub(r" ([,.;:!?%)])",r"\1",t); t=re.sub(r"([($]) ",r"\1",t)
  t=re.sub(r'" ([^"]*?) "',r'"\1"',t); t=t.replace(" - ","-") if False else t
  return re.sub(r"\s+"," ",t).strip()
def q(r):
  x=detok(r['question']); return re.sub(r"\s*Please explain like I'm five\.?$","",x)
MODELS=[("gpt-6-luna",{"reasoning_effort":"none"}),("gpt-5.4-nano",{"reasoning_effort":"none"}),("gpt-4o-mini",{})]
K=os.environ["OPENAI_API_KEY"]
def ask(i):
  r=sample[i]; model,extra=MODELS[i%3]
  body={"model":model,"messages":[{"role":"user","content":q(r)}],"max_completion_tokens":700,**extra}
  for attempt in range(3):
    try:
      req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+K,"content-type":"application/json"})
      d=json.load(urllib.request.urlopen(req,timeout=90))
      return {"i":i,"source":r['source'],"question":q(r),"model":model,"ai":d["choices"][0]["message"]["content"],"usage":d["usage"],"human":[detok(h) for h in r['human_answers']],"chatgpt_2022":[detok(c) for c in r['chatgpt_answers']]}
    except Exception as e:
      err=str(e); time.sleep(2)
  return {"i":i,"error":err}
with cf.ThreadPoolExecutor(10) as ex: out=list(ex.map(ask,range(len(sample))))
json.dump(out,open('corpus.json','w'),ensure_ascii=False)
PR={"gpt-6-luna":(0.10,0.50),"gpt-5.4-nano":(0.20,1.25),"gpt-4o-mini":(0.15,0.60)}
cost=sum((o["usage"]["prompt_tokens"]*PR[o["model"]][0]+o["usage"]["completion_tokens"]*PR[o["model"]][1])/1e6 for o in out if "usage" in o)
print("ok",sum(1 for o in out if "ai" in o),"err",sum(1 for o in out if "error" in o),"cost $%.4f"%cost)
errs=[o for o in out if "error" in o][:3]; print(errs)
