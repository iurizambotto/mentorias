import pandas as pd, numpy as np
df = pd.read_csv('BASE DE PACING_v2.csv.xls', encoding='utf-8-sig')
df['Data'] = pd.to_datetime(df['Data'])
p = df[df.Base=='Planejado'].copy(); r = df[df.Base=='Realizado'].copy()
p['ini'] = pd.to_datetime(p['Data de Inicio']); p['fim'] = pd.to_datetime(p['Data de Termino'])

# chave de atribuicao: Campanha + Veiculo + Publico + Modalidade + janela do flight
KEY = ['Campanha','Veiculo','Publico','Modalidade']
# os 2 flights Trade de Freeshop sao duplicata (mesma chave, janelas sobrepostas) -> viram 1 grupo
p['grupo'] = p.groupby(KEY+['ini']).ngroup()
dup = p.duplicated(KEY, keep=False) & p.duplicated(KEY+['ini'], keep=False)
p.loc[dup,'grupo'] = -1

def matched(sub, inclusive_end=True):
    tot = np.zeros(3)
    for _,t in sub.iterrows():
        fim = t['fim'] if inclusive_end else t['fim'] - pd.Timedelta(days=1)
        m = (r.Campanha==t.Campanha)&(r.Veiculo==t.Veiculo)&(r.Publico==t.Publico)&(r.Modalidade==t.Modalidade)&(r.Data>=t.ini)&(r.Data<=fim)
        tot = tot + r[m][['Soma de Investimento','Soma de Impressoes','Soma de Cliques']].sum().values
    return tot

out = []
for g, sub in p.groupby('grupo'):
    if g == -1:  # grupo duplicado: janela uniao, realizado contado 1x
        ini, fim = sub.ini.min(), sub.fim.max()
        t = sub.iloc[0]
        m = (r.Campanha==t.Campanha)&(r.Veiculo==t.Veiculo)&(r.Publico==t.Publico)&(r.Modalidade==t.Modalidade)&(r.Data>=ini)&(r.Data<=fim)
        real = r[m][['Soma de Investimento','Soma de Impressoes','Soma de Cliques']].sum().values
        realx = real
    else:
        t = sub.iloc[0]; ini, fim = sub.ini.min(), sub.fim.max()
        real = matched(sub); realx = matched(sub, False)
    plan = sub[['Soma de Investimento','Soma de Impressoes','Soma de Cliques']].sum().values
    out.append(dict(Campanha=t.Campanha, Veiculo=t.Veiculo, Publico=t.Publico, Modalidade=t.Modalidade,
        Inicio=ini.date(), Termino=fim.date(), Flights=len(sub),
        PlanInv=plan[0], RealInv=real[0], RealInvExcl=realx[0],
        PlanImp=plan[1], RealImp=real[1], PlanCli=plan[2], RealCli=real[2]))
o = pd.DataFrame(out)
for a,b,n in [('RealInv','PlanInv','Pac_Inv'),('RealImp','PlanImp','Pac_Imp'),('RealCli','PlanCli','Pac_Cli')]:
    o[n] = np.where(o[b]>0, o[a]/o[b], np.nan)
o = o.sort_values(['Inicio','Campanha','Veiculo'])
o.to_csv('pacing_por_flight.csv', index=False)

pd.set_option('display.width',300); pd.set_option('display.max_rows',80)
cols=['Campanha','Veiculo','Publico','Inicio','Termino','PlanInv','RealInv','Pac_Inv','PlanImp','RealImp','Pac_Imp','PlanCli','RealCli','Pac_Cli']
print(o[cols].round(2).to_string(index=False))
print()
print('=== TOTAIS (so linhas com plano > 0) ===')
v = o[o.PlanInv>0]
print('flights/grupos:', len(o), '| com verba planejada:', len(v))
for a,b,n in [('PlanInv','RealInv','Investimento'),('PlanImp','RealImp','Impressoes'),('PlanCli','RealCli','Cliques')]:
    print(f'{n:14s} plan {o[a].sum():>16,.0f}  real {o[b].sum():>16,.0f}  pacing {o[b].sum()/o[a].sum():.1%}')
print()
print('sensibilidade fim exclusivo: real inv', round(o.RealInvExcl.sum(),2), 'vs inclusivo', round(o.RealInv.sum(),2))
print()
print('=== realizado total do arquivo vs realizado dentro de plano ===')
print('realizado total arquivo:', round(r['Soma de Investimento'].sum(),2))
print('realizado jun-jul/2024 :', round(r[(r.Data>='2024-05-28')&(r.Data<='2024-07-31')]['Soma de Investimento'].sum(),2))
