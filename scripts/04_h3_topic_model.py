
"""H3 final stage: k fixed at the tuned value; corpus streamed so peak memory stays modest."""
import json, gc, numpy as np, pandas as pd, scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from scipy.stats import mannwhitneyu, shapiro, spearmanr
import statsmodels.api as sm

RNG=20261106; SRC='h3/dept_abstracts.jsonl'
DOMAIN_STOP=set("""abstract description project research study studies aim aims specific proposed propose
proposal provided applicant candidate narrative text unavailable public health relevance significance
approach innovation investigator investigators data will using use used new novel important understanding
results result years year award grant funding support program training development patients patient
subjects human clinical disease diseases treatment therapy cells cell protein gene genes expression
mechanisms mechanism role increased decreased associated effects effect analysis identify determine
examine test testing evaluate assess based including""".split())

def stream():
    seen=set()
    for line in open(SRC):
        try: r=json.loads(line)
        except Exception: continue
        a=r.get('appl_id')
        if a is None or a in seen: continue
        seen.add(a)
        d=r.get('dept')
        if not d: continue
        t=((r.get('title') or '')+' '+(r.get('abs') or '')).strip()
        if len(t.split())<30: continue
        yield d, t, r.get('amt'), r.get('pi')

K=int(pd.read_csv('h3/tuning.csv').sort_values('score').iloc[-1]['k'])
print('K =',K, flush=True)

import os
if os.path.exists('h3/X.npz') and os.path.exists('h3/meta.csv'):
    X=sp.load_npz('h3/X.npz'); meta=pd.read_csv('h3/meta.csv'); vocab=np.load('h3/vocab.npy',allow_pickle=True)
    print('loaded cached X',X.shape, flush=True)
else:
  rs=np.random.RandomState(RNG); samp=[]
  for i,(d,t,a,p) in enumerate(stream()):
      if len(samp)<30000: samp.append(t)
      elif rs.rand() < 30000/(i+1): samp[rs.randint(30000)]=t
  vec=CountVectorizer(lowercase=True, stop_words='english', min_df=25, max_df=0.30,
                      max_features=15000, token_pattern=r"(?u)\b[a-zA-Z]{4,}\b")
  vec.fit(samp); del samp; gc.collect()
  keep=np.array([i for i,t in enumerate(vec.get_feature_names_out()) if t not in DOMAIN_STOP])
  vocab=vec.get_feature_names_out()[keep]
  print('vocab', len(vocab), flush=True)

  blocks=[]; dept=[]; amt=[]; pi=[]; buf=[]
  def flush():
      global buf
      if buf:
          blocks.append(vec.transform(buf)[:,keep].astype(np.float32)); buf=[]
  for d,t,a,p in stream():
      dept.append(d); amt.append(a); pi.append(p); buf.append(t)
      if len(buf)>=10000: flush()
  flush()
  X=sp.vstack(blocks).tocsr(); del blocks; gc.collect()
  X.indices=X.indices.astype(np.int32); X.indptr=X.indptr.astype(np.int32)
  meta=pd.DataFrame({'dept':dept,'amt':pd.Series(pd.to_numeric(amt,errors='coerce')).fillna(0).values,'pi':pi})
  del dept,amt,pi; gc.collect()
  sp.save_npz('h3/X.npz',X); meta.to_csv('h3/meta.csv',index=False); np.save('h3/vocab.npy',vocab)
print('X',X.shape,'nnz',X.nnz, flush=True)

lda=LatentDirichletAllocation(n_components=K, learning_method='online', batch_size=1024,
                              max_iter=15, random_state=RNG, n_jobs=1, evaluate_every=-1)
lda.fit(X)
pd.DataFrame({'topic':range(K),'terms':[', '.join(vocab[np.argsort(c)[::-1][:12]]) for c in lda.components_]}
            ).to_csv('h3/topics.csv',index=False)
print('fitted', flush=True)

sums={}; counts={}
dv=meta['dept'].values
for s in range(0, X.shape[0], 10000):
    dt=lda.transform(X[s:s+10000]); dt=dt/dt.sum(1,keepdims=True)
    for d,row in zip(dv[s:s+10000], dt):
        if d not in sums: sums[d]=np.zeros(K); counts[d]=0
        sums[d]+=row; counts[d]+=1
    del dt
recs=[]
for d,v in sums.items():
    g=meta[meta.dept==d]; p=v/v.sum(); ent=float(-(p*np.log(p+1e-300)).sum())
    recs.append({'department':d,'n_projects':counts[d],'total_funding':float(g.amt.sum()),
                 'n_pis':int(g.pi.nunique()),'entropy':ent,'entropy_norm':ent/np.log(K),
                 'hhi':float((p**2).sum()),'top_topic':int(np.argmax(p)),'top_topic_share':float(p.max())})
S=pd.DataFrame(recs).sort_values('total_funding',ascending=False)
S['funding_per_pi']=S.total_funding/S.n_pis
S.to_csv('h3/dept_specialization.csv',index=False)
print(S.to_string(index=False), flush=True)

cut=S.total_funding.quantile(0.75); top,avg=S[S.total_funding>=cut],S[S.total_funding<cut]
res={'k_topics':K,'n_departments':int(len(S)),'n_documents':int(X.shape[0]),'vocab':int(len(vocab)),
     'top_cut_usd':float(cut),'n_top':int(len(top)),'n_avg':int(len(avg))}
for v in ['entropy_norm','hhi']:
    u,pv=mannwhitneyu(top[v],avg[v],alternative='two-sided')
    res.update({v+'_top_median':float(top[v].median()), v+'_avg_median':float(avg[v].median()),
                v+'_U':float(u), v+'_p':float(pv), v+'_shapiro_p':float(shapiro(S[v]).pvalue)})
rho,pr=spearmanr(S.hhi,S.total_funding); res['spearman_hhi_funding_rho']=float(rho); res['spearman_hhi_funding_p']=float(pr)
Xr=sm.add_constant(pd.DataFrame({'hhi':S.hhi.values,'log_n_projects':np.log(S.n_projects.values),
                                 'funding_per_pi_musd':S.funding_per_pi.values/1e6}))
fit=sm.OLS(np.log(S.total_funding.values),Xr).fit(cov_type='HC3')
res['ols']={'n':int(fit.nobs),'r2':float(fit.rsquared),
            'params':{k:float(v) for k,v in fit.params.items()},
            'pvalues':{k:float(v) for k,v in fit.pvalues.items()}}
json.dump(res,open('h3/h3_results.json','w'),indent=2)
print(json.dumps(res,indent=2), flush=True)
