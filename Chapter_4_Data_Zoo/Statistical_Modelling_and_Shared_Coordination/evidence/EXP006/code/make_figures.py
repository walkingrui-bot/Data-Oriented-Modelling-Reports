import numpy as np,pandas as pd,matplotlib.pyplot as plt,os
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));fig=root+'/figures';os.makedirs(fig,exist_ok=True)
df=pd.read_csv(root+'/results/per_seed.csv')
# Figure 1: reconstruction across change regimes
cats=['none','drift','world','both']
x=np.arange(len(cats));w=0.36
state=[df[f'state_rmse_{c}'].median() for c in cats]
nost=[df[f'nostate_rmse_{c}'].median() for c in cats]
plt.figure(figsize=(7.4,4.6))
plt.bar(x-w/2,nost,w,label='No dynamic state')
plt.bar(x+w/2,state,w,label='Recurrent channel state')
plt.xticks(x,['No change','Channel drift','World change','Both'])
plt.ylabel('Held-out RMSE')
plt.title('Dynamic state improves reconstruction without changing the frozen reality core')
plt.legend(frameon=False);plt.tight_layout();plt.savefig(fig+'/fig1_reconstruction_regimes.png',dpi=180);plt.close()
# Figure 2: incremental state localization under channel drift
ch=np.arange(6)
med=[df[f'state_energy_drift_c{i}'].median() for i in ch]
plt.figure(figsize=(7.4,4.6))
plt.bar(ch,med)
plt.xticks(ch,[f'Channel {i+1}' for i in ch])
plt.ylabel('Incremental recurrent-state norm')
plt.title('Channel-only drift is localized to the affected measurement channel')
plt.tight_layout();plt.savefig(fig+'/fig2_state_localization.png',dpi=180);plt.close()
# Figure 3: probe and separation metrics across seeds
x=np.arange(len(df))
plt.figure(figsize=(7.4,4.6))
plt.plot(x,df.world_probe_r2,'o-',label='World change readout $R^2$')
plt.plot(x,df.drift_probe_r2,'o-',label='Channel drift readout $R^2$')
plt.xticks(x,[f'Seed {i}' for i in df.seed])
plt.ylim(0,1.02);plt.ylabel('$R^2$')
plt.title('Two hidden changes remain separately readable')
plt.legend(frameon=False);plt.tight_layout();plt.savefig(fig+'/fig3_separate_readouts.png',dpi=180);plt.close()
# Figure 4: seed0 temporal routing, paired against no-change episodes
z=np.load(root+'/results/seed0_dynamic_arrays.npz',allow_pickle=True)
S=z['S'];R=z['R'];W=z['W'];D=z['D'];k=z['kinds']
n=S.shape[0]//4;T=S.shape[1]
S4=S.reshape(n,4,T,6,-1);R4=R.reshape(n,4,T,-1);W4=W.reshape(n,4,T);D4=D.reshape(n,4,T)
drift_state=np.linalg.norm(S4[:,1,:,5,:]-S4[:,0,:,5,:],axis=-1).mean(0)
world_move=np.linalg.norm(R4[:,2,:,:]-R4[:,0,:,:],axis=-1).mean(0)
drift_truth=D4[:,1,:].mean(0);world_truth=np.abs(W4[:,2,:]).mean(0)
# normalize for trajectory shape comparison only
norm=lambda a:a/(a.max()+1e-8)
plt.figure(figsize=(7.4,4.6))
plt.plot(np.arange(T),norm(drift_truth),'o-',label='True channel drift')
plt.plot(np.arange(T),norm(drift_state),'o-',label='Channel-6 state response')
plt.xlabel('Episode step');plt.ylabel('Normalized amplitude')
plt.title('The recurrent channel state follows measurement drift')
plt.legend(frameon=False);plt.tight_layout();plt.savefig(fig+'/fig4_drift_trajectory.png',dpi=180);plt.close()
plt.figure(figsize=(7.4,4.6))
plt.plot(np.arange(T),norm(world_truth),'o-',label='True world change')
plt.plot(np.arange(T),norm(world_move),'o-',label='Reality-core movement')
plt.xlabel('Episode step');plt.ylabel('Normalized amplitude')
plt.title('The shared reality state follows coherent world change')
plt.legend(frameon=False);plt.tight_layout();plt.savefig(fig+'/fig5_world_trajectory.png',dpi=180);plt.close()
