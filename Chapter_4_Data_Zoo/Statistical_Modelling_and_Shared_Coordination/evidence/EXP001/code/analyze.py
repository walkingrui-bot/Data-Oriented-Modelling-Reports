from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import experiment as ex

ROOT=ex.ROOT; R=ROOT/'results'; F=ROOT/'figures'
F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                    'axes.spines.right':False,'axes.titleweight':'bold',
                    'savefig.dpi':180,'figure.facecolor':'white'})
BLUE='#2563A6';TEAL='#008A83';ORANGE='#D88620';RED='#B34654';GREY='#637083'
data=pd.read_csv(R/'run_metrics.csv'); traces=pd.read_csv(R/'coordination_traces.csv')
teachers=pd.read_csv(R/'teacher_metrics.csv')
refs=pd.read_csv(R/'exact_representation_controls.csv')
extended=pd.read_csv(R/'extended_budget_controls.csv')
inits=pd.read_csv(R/'initial_state_audit.csv')

def wilson(k,n):
    z=1.95996398454;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half,center+half]

def bootstrap(v):
    v=np.asarray(v);rng=np.random.default_rng(3388)
    s=rng.integers(0,len(v),size=(20000,len(v)))
    return np.quantile(np.median(v[s],axis=1),[.025,.975]).tolist()

summary=[]
for keys,g in data.groupby(['noise','init','degree','update']):
    row=dict(zip(['noise','init','degree','update'],keys))
    row.update(n=len(g),pass_count=int(g.all_sources_pass.sum()),
               pass_wilson_95=wilson(g.all_sources_pass.sum(),len(g)),
               median_rmse=float(g.rmse_target.median()),median_worst=float(g.worst_target.median()),
               median_clean_rmse=float(g.rmse_clean.median()),
               median_hidden_corr=float(g.hidden_state_abs_corr.median()),
               median_first_pass=float(g.loc[g.first_pass_step>=0,'first_pass_step'].median()) if (g.first_pass_step>=0).any() else None)
    summary.append(row)
pd.DataFrame(summary).to_csv(R/'group_summary.csv',index=False)
paired=data[(data.noise==.03)&(data.init=='geometry')&(data.degree==2)&(data['update']=='coupled_step')].merge(teachers,on=['seed','noise'],suffixes=('_coord','_teacher'))
gain=100*(1-paired.rmse_clean_coord/paired.rmse_clean_teacher)
exact=data[(data.init=='geometry')&(data.degree==1)&(data['update']=='coupled_step')].merge(refs,on=['seed','noise'])
chosen=traces[(traces.noise==0)&(traces.init=='geometry')&(traces.degree==2)&(traces['update']=='coupled_step')]
long_rows=[]
for keys,g in extended.groupby(['init','update']):
    long_rows.append(dict(init=keys[0],update=keys[1],n=len(g),steps=int(g.steps.iloc[0]),
                         pass_count=int(g.all_sources_pass.sum()),median_rmse=float(g.rmse_target.median()),
                         median_first_pass=float(g.loc[g.first_pass_step>=0,'first_pass_step'].median()) if (g.first_pass_step>=0).any() else None))
stats=dict(groups=summary,extended=long_rows,
           denoising=dict(n=len(gain),median_relative_improvement_percent=float(np.median(gain)),
                          bootstrap_95=bootstrap(gain),improved_count=int((gain>0).sum()),
                          teacher_median=float(paired.rmse_clean_teacher.median()),
                          coordinator_median=float(paired.rmse_clean_coord.median())),
           line_reference_max_abs_difference=float(np.max(abs(exact.rmse_target-exact.exact_best_line_rmse))),
           seed0_changes=chosen[['step','rmse','worst_rmse','tangent_rank','curvature_weight_norm','singular_1','singular_2','singular_3']].iloc[[0,1,2,3,5,80]].to_dict(orient='records'),
           initial_audit=inits.groupby(['noise','init'])[['rmse_target','hidden_state_abs_corr']].median().reset_index().to_dict(orient='records'))
(R/'summary.json').write_text(json.dumps(stats,indent=2,default=lambda x:x.item()))

# Figure 1: seven separately learned local mechanisms within one fixed system.
arrays=np.load(ROOT/'data'/'all_experiment_arrays.npz')
x=arrays['n0_s0_x'];theta=arrays['n0_s0_teacher_theta']
colors=plt.cm.viridis(np.linspace(.08,.92,7))
fig,ax=plt.subplots(1,2,figsize=(10.2,3.8),layout='constrained')
for i,c in enumerate(colors):ax[0].plot(x,theta[i]@ex.basis(x).T,color=c,lw=2,label=f'Local {i+1}')
ax[0].set(xlabel='Shared input x',ylabel='Learned output',title='Seven local models, three weights each')
ax[0].legend(ncol=2,fontsize=8,frameon=False)
im=ax[1].imshow(theta,aspect='auto',cmap='coolwarm',vmin=-1.2,vmax=1.4)
ax[1].set(xticks=range(3),xticklabels=['a: offset','b: linear','c: quadratic'],yticks=range(7),
          yticklabels=[f'Local {i+1}' for i in range(7)],title='Learned local parameters')
for i in range(7):
    for j in range(3):ax[1].text(j,i,f'{theta[i,j]:.2f}',ha='center',va='center',fontsize=9)
fig.colorbar(im,ax=ax[1],fraction=.035,pad=.02)
fig.savefig(F/'01_local_models.png');plt.close(fig)

# Figure 2: convergence with matched architectures and identical inputs.
fig,ax=plt.subplots(1,2,figsize=(10.2,3.8),layout='constrained')
labels={(1,'joint_gradient'):'Line / joint gradient',(1,'coupled_step'):'Line / coupled step',
        (2,'joint_gradient'):'Curve / joint gradient',(2,'coupled_step'):'Curve / coupled step'}
styles={(1,'joint_gradient'):(GREY,'--'),(1,'coupled_step'):(ORANGE,'-'),
        (2,'joint_gradient'):(BLUE,'--'),(2,'coupled_step'):(TEAL,'-')}
for degree,method in labels:
    s=traces[(traces.noise==0)&(traces.init=='geometry')&(traces.degree==degree)&(traces['update']==method)]
    color,ls=styles[degree,method]
    for a in ax:a.plot(s.step,np.maximum(s.worst_rmse,1e-14),label=labels[degree,method],color=color,ls=ls,lw=2)
for a in ax:
    a.axhline(.01,color=RED,ls=':',lw=1.5,label='All-source threshold')
    a.set_yscale('log');a.set_xlabel('Internal update');a.set_ylabel('Worst local target RMSE');a.set_ylim(1e-14,2)
ax[0].set(xlim=(0,80),title='Full 80-step window')
ax[1].set(xlim=(0,8),ylim=(1e-8,2),title='First eight internal updates')
ax[0].legend(fontsize=8,frameon=False,loc='lower left')
fig.savefig(F/'02_convergence.png');plt.close(fig)

# Figure 3: identify which internal direction appears.
fig,ax=plt.subplots(1,3,figsize=(10.2,3.35),layout='constrained')
for degree,col in [(1,ORANGE),(2,TEAL)]:
    key=f'n0_s0_geometry_d{degree}_coupled_step_final_parameters'
    p=arrays[key];W,z=ex.unpack(p,degree,7);zgrid=np.linspace(z.min(),z.max(),200)
    curved=np.stack([zgrid**k for k in range(degree+1)],1)@W
    ax[0].plot(curved[:,0],curved[:,2],color=col,lw=2,label='Line layer' if degree==1 else 'Curve layer')
ax[0].scatter(theta[:,0],theta[:,2],c=colors,s=36,zorder=3)
ax[0].set(xlabel='Local weight a',ylabel='Local weight c',title='Local mechanism curve')
ax[0].legend(fontsize=8,frameon=False)
ss=chosen[chosen.step<=8]
ax[1].plot(ss.step,ss.curvature_weight_norm,'o-',color=TEAL,label='Curvature weights')
ax[1].plot(ss.step,ss.singular_2,'s-',color=BLUE,label='Second mechanism singular value')
ax[1].set(xlabel='Internal update',ylabel='Magnitude',title='Curvature grows at update 1')
ax[1].legend(fontsize=7.5,frameon=False)
ax[2].step(ss.step,ss.tangent_rank,where='post',color=TEAL,lw=2)
ax[2].scatter(ss.step,ss.tangent_rank,color=TEAL,s=20)
ax[2].set(xlabel='Internal update',ylabel='Jacobian rank',ylim=(12.6,14.4),yticks=[13,14],title='Jacobian rank rises')
fig.savefig(F/'03_internal_changes.png');plt.close(fig)

# Figure 4: initialization and the independent truth audit under observation noise.
fig,ax=plt.subplots(1,2,figsize=(10.2,3.8),layout='constrained')
d=data[(data.noise==0)&(data.degree==2)&(data['update']=='coupled_step')]
g=d[d.init=='geometry'];r=d[d.init=='random']
ax[0].bar([0,1],[g.all_sources_pass.mean()*100,r.all_sources_pass.mean()*100],color=[TEAL,ORANGE],width=.55)
for k,q in enumerate([g,r]):
    lo,hi=np.array(wilson(q.all_sources_pass.sum(),len(q)))*100;pct=q.all_sources_pass.mean()*100
    ax[0].errorbar(k,pct,yerr=[[pct-lo],[hi-pct]],color='black',capsize=5)
    ax[0].text(k,pct+4,f'{int(q.all_sources_pass.sum())}/30',ha='center',fontweight='bold')
ax[0].set(xticks=[0,1],xticklabels=['Data geometry start','Random start'],ylim=(0,116),
          ylabel='All seven local targets pass (%)',title='Initialization selects different solutions')
for _,row in paired.iterrows():
    ax[1].plot([0,1],[row.rmse_clean_teacher,row.rmse_clean_coord],color=GREY,alpha=.3,lw=.7)
ax[1].scatter(np.zeros(len(paired)),paired.rmse_clean_teacher,color=ORANGE,s=18,label='Seven learned teachers')
ax[1].scatter(np.ones(len(paired)),paired.rmse_clean_coord,color=TEAL,s=18,label='Coordinated functions')
ax[1].set(xticks=[0,1],xticklabels=['Local models','Shared curve'],ylabel='RMSE against clean simulator output',
          title='Noisy local learning then coordination')
fig.savefig(F/'04_initialization_noise.png');plt.close(fig)

# Full numerical tables, with target functions for convenient inspection.
table=[]
for i in range(7):
    row=dict(local_model=i+1,a=theta[i,0],b=theta[i,1],c=theta[i,2],simulator_state_audit_only=float(arrays['n0_s0_hidden_s_audit_only'][i]))
    table.append(row)
pd.DataFrame(table).to_csv(R/'seed0_local_mechanisms.csv',index=False)
print(json.dumps({k:v for k,v in stats.items() if k in ['denoising','line_reference_max_abs_difference','extended']},indent=2))
