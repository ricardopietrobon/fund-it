import json, os, time, urllib.request, urllib.error, sys
URL='https://api.reporter.nih.gov/v2/projects/search'
FIELDS=["ApplId","ProjectNum","CoreProjectNum","FiscalYear","Organization","ActivityCode",
        "AwardAmount","ProjectTitle","AbstractText","ContactPiName","AgencyCode"]
def post(payload, tries=6):
    for a in range(tries):
        try:
            req=urllib.request.Request(URL,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            return json.loads(urllib.request.urlopen(req,timeout=180).read())
        except Exception as e:
            if a==tries-1: raise
            time.sleep(3*(a+1))
def run(keyfield, keys, years, out, logf):
    done=set()
    if os.path.exists(out+'.keys'): done=set(open(out+'.keys').read().split('\n'))
    f=open(out,'a'); kf=open(out+'.keys','a')
    for k in keys:
        for y in years:
            tag=f"{k}|{y}"
            if tag in done: continue
            off=0; n=0
            while True:
                crit={"fiscal_years":[y], keyfield:[k]}
                d=post({"criteria":crit,"limit":500,"offset":off,"include_fields":FIELDS})
                rs=d.get('results') or []
                for r in rs:
                    o=r.get('organization') or {}
                    f.write(json.dumps({"appl_id":r.get('appl_id'),"project_num":r.get('project_num'),
                      "core":r.get('core_project_num'),"fy":r.get('fiscal_year'),
                      "dept":o.get('dept_type'),"org":o.get('org_name'),"ipf":o.get('org_ipf_code'),
                      "state":o.get('org_state'),"city":o.get('org_city'),
                      "act":r.get('activity_code'),"agency":r.get('agency_code'),
                      "amt":r.get('award_amount'),"title":r.get('project_title'),
                      "abs":r.get('abstract_text'),"pi":r.get('contact_pi_name')})+'\n')
                n+=len(rs); off+=500
                if len(rs)<500 or off>=14500: break
                time.sleep(0.35)
            f.flush(); kf.write(tag+'\n'); kf.flush()
            print(f"{tag} {n}", file=logf, flush=True)
            time.sleep(0.35)
    f.close()
if __name__=='__main__':
    depts=[l.strip() for l in open('h3/depts.txt') if l.strip()]
    with open('h3/fetch.log','a') as lg:
        run("dept_types", depts, [2020,2021,2022,2023,2024], 'h3/dept_abstracts.jsonl', lg)
    print('DONE', file=sys.stderr)
