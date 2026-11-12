import json,re,math,collections
C=json.load(open('corpus.json'))
def norm(t):
  t=t.replace("\u2019","'").replace("\u2018","'")
  return t
def toks(t):
  t=norm(t).lower(); t=re.sub(r"[*_#`>|]+"," ",t)
  return re.findall(r"[a-z]+(?:'[a-z]+)?",t)
groups={"ai":[o["ai"] for o in C],"human":[" ".join(o["human"]) for o in C],"chatgpt2022":[" ".join(o["chatgpt_2022"]) for o in C if o["chatgpt_2022"]]}
STOP=set("the a an and or of to in is it that this for on with as are be by at from was were can if not but your you i we they their there which these those have has had will would its it's do does so".split())
stats={}
for g,docs in groups.items():
  cnt=collections.Counter(); df=collections.Counter(); W=0
  for d in docs:
    tk=toks(d); W+=len(tk); seen=set()
    for n in (1,2,3,4):
      for i in range(len(tk)-n+1):
        ng=" ".join(tk[i:i+n]); cnt[ng]+=1; seen.add(ng)
    for s in seen: df[s]+=1
  stats[g]={"cnt":cnt,"df":df,"W":W,"N":len(docs)}
  if g=="ai":
    srcdf=collections.defaultdict(collections.Counter)
    for o,d in zip(C,docs):
      tk=toks(d); seen=set()
      for n in (1,2,3,4):
        for i in range(len(tk)-n+1): seen.add(" ".join(tk[i:i+n]))
      for x in seen: srcdf[x][o["source"]]+=1
  print(g,"docs",len(docs),"words",W)
A,H,O=stats["ai"],stats["human"],stats["chatgpt2022"]
def rate(s,ng): return s["cnt"][ng]/s["W"]*10000
def ratio(ng): return ((A["cnt"][ng]+1)/A["W"])/((H["cnt"][ng]+1)/H["W"])
cands=[]
for ng,c in A["cnt"].items():
  ws=ng.split()
  if A["df"][ng]<8: continue
  sd=srcdf[ng]
  if len(sd)<3 or max(sd.values())/sum(sd.values())>0.6: continue
  if ng in {"e g","vs","etc","e","g","i e"}: continue
  if all(w in STOP for w in ws): continue
  if ws[0] in STOP and len(ws)==1: continue
  r=ratio(ng)
  if r<3: continue
  cands.append((ng,r))
# prune: drop n-gram if a longer one containing it has >=80% of its count; drop longer one if it adds no info (count ~ same as shorter and ratio not higher)
cands.sort(key=lambda x:-x[1])
keep=[]
cset={ng for ng,_ in cands}
for ng,r in cands:
  sup=[o for o in cset if o!=ng and (" "+ng+" ") in (" "+o+" ") and A["cnt"][o]>=0.8*A["cnt"][ng]]
  if sup: continue
  sub=[k for k,_ in keep if (" "+k+" ") in (" "+ng+" ")]
  if sub: continue
  keep.append((ng,r))
# merge overlapping chains ("if you want i" / "you want i can")
merged=[]
for ng,r in keep:
  w=ng.split()
  if any(len(w)>1 and (" ".join(w[1:]) in k or " ".join(w[:-1]) in k) and abs(A["cnt"][k]-A["cnt"][ng])<=2 for k,_ in merged): continue
  merged.append((ng,r))
keep=merged
# re-rank by evidence: log ratio * log(df)
keep.sort(key=lambda x:-(math.log(x[1])*math.log(A["df"][x[0]])))
out=[]
for ng,r in keep[:120]:
  out.append({"phrase":ng,"ratio":round(r,1),"ai_per_10k":round(rate(A,ng),2),"human_per_10k":round(rate(H,ng),2),"chatgpt2022_per_10k":round(rate(O,ng),2),"ai_docs_pct":round(100*A["df"][ng]/A["N"],1),"human_docs_pct":round(100*H["df"][ng]/H["N"],1)})
json.dump(out,open("ranked.json","w"),indent=1)
for o in out[:150]: print(f'{o["phrase"]:30s} x{o["ratio"]:<6} ai{o["ai_per_10k"]:<6} hu{o["human_per_10k"]:<6} docs{o["ai_docs_pct"]}%/{o["human_docs_pct"]}%')

print("N candidates",len(keep))
# formatting / structure stats
def fstats(docs):
  W=sum(len(toks(d)) for d in docs)
  em=sum(d.count("\u2014") for d in docs); bul=sum(len(re.findall(r"(?m)^\s*(?:[-*\u2022]|\d+\.)\s",d)) for d in docs)
  bold=sum(len(re.findall(r"\*\*[^*]+\*\*",d)) for d in docs); hd=sum(len(re.findall(r"(?m)^#{1,6}\s",d)) for d in docs)
  colon=sum(d.count(":") for d in docs); semi=sum(d.count(";") for d in docs); excl=sum(d.count("!") for d in docs)
  sents=[len(x.split()) for d in docs for x in re.split(r"(?<=[.!?])\s+",re.sub(r"\s+"," ",d)) if len(x.split())>2]
  import statistics
  return {"words":W,"em_dash_per_1k":round(em/W*1000,2),"bullets_per_1k":round(bul/W*1000,2),"bold_per_1k":round(bold/W*1000,2),"headings_per_1k":round(hd/W*1000,2),"colons_per_1k":round(colon/W*1000,2),"semicolons_per_1k":round(semi/W*1000,2),"exclaim_per_1k":round(excl/W*1000,2),"sentence_len_mean":round(statistics.mean(sents),1),"sentence_len_sd":round(statistics.pstdev(sents),1)}
F={g:fstats(d) for g,d in groups.items()}
F["by_model"]={m:fstats([o["ai"] for o in C if o["model"]==m]) for m in sorted({o["model"] for o in C})}
print(json.dumps(F,indent=1))
# curated rules measured
rules=json.load(open("slop-rules.json"))["rules"]
cur=[]
for r in rules:
  if r.get("regex"): continue
  ng=" ".join(toks(r["phrase"]))
  if not ng: continue
  cur.append({"phrase":r["phrase"],"ai_per_10k":round(rate(A,ng),2),"chatgpt2022_per_10k":round(rate(O,ng),2),"human_per_10k":round(rate(H,ng),2)})
json.dump({"ranked":out[:100],"formatting":F,"curated":cur,"corpus":{"questions":len(C),"ai_words":A["W"],"human_words":H["W"],"chatgpt2022_words":O["W"],"models":{m:sum(1 for o in C if o["model"]==m) for m in sorted({o["model"] for o in C})},"sources":dict(collections.Counter(o["source"] for o in C))}},open("results.json","w"),indent=1)
top=sorted(cur,key=lambda x:-(x["ai_per_10k"]+x["chatgpt2022_per_10k"]))[:20]
for t in top: print(t)
