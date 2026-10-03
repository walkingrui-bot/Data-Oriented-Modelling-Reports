import pandas as pd, numpy as np, matplotlib.pyplot as plt, os
root='/mnt/data/INTERNAL_COORDINATION_005'
r=pd.read_csv(root+'/results/per_seed.csv'); h=pd.read_csv(root+'/results/holdout_channel.csv'); d=pd.read_csv(root+'/results/dynamic_state.csv')
os.makedirs(root+'/figures',exist_ok=True)
# Fig1: fixed + drift
fig,axs=plt.subplots(1,2,figsize=(10,4.2))
for k,mode in enumerate(['affine','neural']):
    g=r[r['mode']==mode]
    axs[0].scatter(np.full(len(g),k),g.base_cross_rmse,s=32)
    axs[0].plot([k-.16,k+.16],[g.base_cross_rmse.median()]*2,lw=2)
axs[0].set_xticks([0,1],['Affine channel','Neural channel']);axs[0].set_ylabel('Cross-channel RMSE');axs[0].set_title('Stable measurement mechanisms')
# drift focus
labels=['Pre-drift adaptation','Channel-only adaptation','Whole-model adaptation']
x=np.arange(3)
for mode,off in [('affine',-.08),('neural',.08)]:
    g=r[r['mode']==mode]
    vals=[g.shift_pre_focus_cross_rmse.median(),g.shift_channel_post_focus_cross_rmse.median(),g.shift_whole_post_focus_cross_rmse.median()]
    axs[1].plot(x+off,vals,marker='o',label=mode)
# dynamic state on neural
axs[1].scatter([1.32],[d.state_post_focus_rmse.median()],marker='D',s=50,label='neural + 64-state')
axs[1].set_xticks(x,labels,rotation=15,ha='right');axs[1].set_ylabel('RMSE involving drifted channel');axs[1].set_title('When one channel changes');axs[1].legend(frameon=False)
fig.tight_layout();fig.savefig(root+'/figures/fig1_channel_network_and_drift.png',dpi=180);plt.close(fig)
# Fig2 new-channel onboarding and collateral damage
fig,axs=plt.subplots(1,2,figsize=(10,4.2))
for k,mode in enumerate(['affine','neural']):
    g=h[h['mode']==mode]
    for _,row in g.iterrows(): axs[0].plot([k-.13,k+.13],[row.new_channel_pre_rmse,row.new_channel_post_rmse],alpha=.5)
    axs[0].scatter(np.full(len(g),k-.13),g.new_channel_pre_rmse,s=25)
    axs[0].scatter(np.full(len(g),k+.13),g.new_channel_post_rmse,s=25)
axs[0].set_xticks([0,1],['Affine','Neural']);axs[0].set_ylabel('New-channel focused RMSE');axs[0].set_title('Attach a previously unseen channel')
# core movement & unaffected damage whole vs local
modes=['affine','neural']; x=np.arange(2)
local=[r[r['mode']==m].unaffected_channel_post_rmse.median() for m in modes]
whole=[r[r['mode']==m].unaffected_whole_post_rmse.median() for m in modes]
axs[1].bar(x-.16,local,width=.32,label='local channel update')
axs[1].bar(x+.16,whole,width=.32,label='whole-model update')
axs[1].set_xticks(x,modes);axs[1].set_ylabel('RMSE on unaffected channels');axs[1].set_title('Collateral change after drift adaptation');axs[1].legend(frameon=False)
fig.tight_layout();fig.savefig(root+'/figures/fig2_onboarding_and_localization.png',dpi=180);plt.close(fig)
