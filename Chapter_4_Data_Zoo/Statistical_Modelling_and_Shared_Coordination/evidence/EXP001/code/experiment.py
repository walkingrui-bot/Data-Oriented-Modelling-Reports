"""INTERNAL_COORDINATION_001: tiny learned local mechanisms and a shared layer.

Run with Python 3, NumPy and pandas. No pretrained networks or external
architecture code is used. The simulator state is exposed only to the audit.
"""
from pathlib import Path
import json, time, platform, hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
CONFIG = dict(experiment='INTERNAL_COORDINATION_001', local_models=7,
              local_parameters=3, x_points=17, repetitions=30,
              observation_noise=[0.0, 0.03], coordinator_steps=80,
              coordinator_degree=[1, 2], initializations=['geometry', 'random'],
              updates=['joint_gradient', 'coupled_step'], gradient_rate=0.22,
              damping=0.001, max_step_norm=1.0, coordinate_tolerance=0.01,
              local_training_steps=500, created='2026-10-01')

def basis(x):
    return np.stack([np.ones_like(x), x, x*x], -1)

def create_data(seed, sigma, m=7):
    rng = np.random.default_rng(6100100 + seed)
    x = np.linspace(-1, 1, CONFIG['x_points'])
    hidden_s = np.linspace(-1, 1, m)
    # All local models observe different states of THIS ONE fixed system.
    W_true = np.array([[0.25, 0.80, -0.20],
                       [0.70, -0.25, 0.45],
                       [0.40, 0.35, -0.55]])
    theta_true = np.stack([np.ones(m), hidden_s, hidden_s**2], 1) @ W_true
    phi = basis(x)
    clean = theta_true @ phi.T
    observed = clean + sigma * rng.normal(size=clean.shape)
    init = rng.normal(0, 0.15, size=(m, 3))
    return x, phi, observed, clean, theta_true, hidden_s, W_true, init

def train_local(phi, observed, init, keep=False):
    # Three trainable output connections per local polynomial-neuron network.
    theta = init.copy()
    gram = phi.T @ phi / len(phi)
    rate = 0.9 / np.linalg.eigvalsh(gram).max()
    records=[]
    for t in range(CONFIG['local_training_steps'] + 1):
        error = theta @ phi.T - observed
        if keep and (t % 10 == 0 or t == CONFIG['local_training_steps']):
            for j in range(len(theta)):
                records.append(dict(step=t, evidence=j, rmse=np.sqrt(np.mean(error[j]**2)),
                                    a=theta[j,0], b=theta[j,1], c=theta[j,2]))
        if t < CONFIG['local_training_steps']:
            theta -= rate * error @ phi / len(phi)
    exact = np.linalg.lstsq(phi, observed.T, rcond=None)[0].T
    assert np.max(np.abs(theta-exact)) < 1e-8, 'local training convergence'
    return theta, records

def unpack(p, degree, m):
    n=3*(degree+1)
    return p[:n].reshape(degree+1, 3), p[n:n+m]

def mechanism(p, degree, m):
    W,z=unpack(p,degree,m)
    V=np.stack([z**k for k in range(degree+1)],1)
    return V @ W

def normalize_gauge(p, degree, m):
    # Exact affine reparameterization fixes mean(z)=0 and sd(z)=1.
    W,z=unpack(p,degree,m)
    mu=z.mean(); scale=max(z.std(),1e-9)
    newW=W.copy()
    if degree == 1:
        newW[0]=W[0]+mu*W[1]
        newW[1]=scale*W[1]
    else:
        newW[0]=W[0]+mu*W[1]+mu*mu*W[2]
        newW[1]=scale*(W[1]+2*mu*W[2])
        newW[2]=scale*scale*W[2]
    return np.r_[newW.ravel(), (z-mu)/scale]

def initialize(target_theta, degree, seed, kind):
    m=len(target_theta); rng=np.random.default_rng(77000+seed)
    centered=target_theta-target_theta.mean(0)
    u,s,vt=np.linalg.svd(centered,full_matrices=False)
    if kind == 'geometry':
        z=u[:,0]*s[0] + .18*rng.normal(size=m)*max(s[0]/np.sqrt(m),.1)
    else:
        z=rng.normal(size=m)
    z=(z-z.mean())/z.std()
    W=np.zeros((degree+1,3)); W[0]=target_theta.mean(0)
    W[1]=.25*(z@centered/m) + .015*rng.normal(size=3)
    return np.r_[W.ravel(),z]

def forward_jacobian(p, degree, phi, m):
    W,z=unpack(p,degree,m); n=len(phi)
    powers=np.stack([z**k for k in range(degree+1)],1)
    theta=powers@W
    prediction=theta@phi.T
    J=np.zeros((m,n,len(p)))
    J[:,:,:3*(degree+1)]=(powers[:,None,:,None]*phi[None,:,None,:]).reshape(m,n,-1)
    dz=sum(k*z[:,None]**(k-1)*W[k][None,:] for k in range(1,degree+1))
    slope=dz@phi.T
    for i in range(m):
        J[i,:,3*(degree+1)+i]=slope[i]
    return prediction,J

def fit_coordinator(target_theta, phi, degree, seed, kind, update, keep=False):
    # This function only receives the LEARNED local mechanisms and x features.
    # Hidden simulator states, clean outputs and test scores are unavailable here.
    m=len(target_theta); target=target_theta@phi.T
    p=initialize(target_theta,degree,seed,kind)
    records=[]; snapshots=[]; initial=mechanism(p,degree,m)
    first_pass=None
    for t in range(CONFIG['coordinator_steps']+1):
        pred,J=forward_jacobian(p,degree,phi,m)
        residual=pred-target
        per_rmse=np.sqrt(np.mean(residual**2,axis=1))
        if first_pass is None and per_rmse.max() <= CONFIG['coordinate_tolerance']:
            first_pass=t
        if keep:
            flatJ=J.reshape(-1,len(p)); r=residual.ravel()
            g_by=np.einsum('mnp,mn->mp',J,residual)/len(phi)
            norms=np.linalg.norm(g_by,axis=1)
            cos=g_by@g_by.T/np.maximum(norms[:,None]*norms[None,:],1e-30)
            valid=(norms[:,None]*norms[None,:]>1e-16)&np.triu(np.ones((m,m),bool),1)
            conflict=np.mean(cos[valid]<-.05) if valid.any() else 0.
            W,z=unpack(p,degree,m)
            eig=np.linalg.eigvalsh(flatJ.T@flatJ/len(r))
            singular=np.linalg.svd(mechanism(p,degree,m)-mechanism(p,degree,m).mean(0),compute_uv=False)
            rec=dict(step=t,degree=degree,update=update,init=kind,
                     rmse=np.sqrt(np.mean(residual**2)),worst_rmse=per_rmse.max(),
                     conflict_fraction=conflict, tangent_rank=int(np.sum(eig>1e-8)),
                     gradient_norm=np.linalg.norm(flatJ.T@r/len(r)),
                     curvature_weight_norm=np.linalg.norm(W[2]) if degree==2 else 0.,
                     parameter_shift=np.linalg.norm(mechanism(p,degree,m)-initial))
            rec.update({f'singular_{k+1}':float(v) for k,v in enumerate(singular)})
            rec.update({f'evidence_{i+1}_rmse':float(v) for i,v in enumerate(per_rmse)})
            rec.update({f'weight_{k}':float(v) for k,v in enumerate(W.ravel())})
            rec.update({f'state_{i+1}':float(v) for i,v in enumerate(z)})
            rec.update({f'eigen_{i+1}':float(v) for i,v in enumerate(eig)})
            records.append(rec);snapshots.append(mechanism(p,degree,m))
        if t == CONFIG['coordinator_steps']: break
        flatJ=J.reshape(-1,len(p)); r=residual.ravel()
        g=flatJ.T@r/len(r)
        if update == 'joint_gradient':
            delta=-CONFIG['gradient_rate']*g
        else:
            H=flatJ.T@flatJ/len(r)
            delta=np.linalg.solve(H+CONFIG['damping']*np.eye(len(p)),-g)
        norm=np.linalg.norm(delta)
        if norm>CONFIG['max_step_norm']:
            delta*=CONFIG['max_step_norm']/norm
        p=normalize_gauge(p+delta,degree,m)
        assert np.all(np.isfinite(p))
    return p,first_pass,records,np.asarray(snapshots)

def verify_derivatives():
    rng=np.random.default_rng(818)
    phi=basis(np.linspace(-1,1,9)); m=5
    checks=[]
    for degree in [1,2]:
        p=rng.normal(0,.3,3*(degree+1)+m)
        y,J=forward_jacobian(p,degree,phi,m)
        fd=[]
        for k in range(len(p)):
            eps=np.zeros_like(p);eps[k]=1e-6
            ya=forward_jacobian(p+eps,degree,phi,m)[0]
            yb=forward_jacobian(p-eps,degree,phi,m)[0]
            fd.append((ya-yb)/2e-6)
        error=np.max(np.abs(np.stack(fd,-1)-J))
        gauge_error=np.max(np.abs(mechanism(p,degree,m)-mechanism(normalize_gauge(p,degree,m),degree,m)))
        assert error<1e-7 and gauge_error<1e-10
        checks.append(dict(degree=degree,jacobian_max_error=error,gauge_output_max_error=gauge_error))
    return checks

def audit(p, degree, phi, target_theta, clean, theta_true, hidden_s):
    m=len(target_theta); theta=mechanism(p,degree,m)
    predicted=theta@phi.T; target=target_theta@phi.T
    errors=np.sqrt(np.mean((predicted-target)**2,axis=1))
    _,z=unpack(p,degree,m)
    cov_real=np.cov(clean); cov_pred=np.cov(predicted)
    Z=np.c_[np.ones(m),z]
    aligned=Z@np.linalg.lstsq(Z,hidden_s,rcond=None)[0]
    return dict(rmse_target=float(np.sqrt(np.mean((predicted-target)**2))),
                worst_target=float(errors.max()),
                all_sources_pass=int(errors.max()<=CONFIG['coordinate_tolerance']),
                rmse_clean=float(np.sqrt(np.mean((predicted-clean)**2))),
                local_parameter_rmse=float(np.sqrt(np.mean((theta-theta_true)**2))),
                hidden_state_abs_corr=float(abs(np.corrcoef(z,hidden_s)[0,1])),
                hidden_state_aligned_rmse=float(np.sqrt(np.mean((aligned-hidden_s)**2))),
                joint_cov_relative_error=float(np.linalg.norm(cov_pred-cov_real)/np.linalg.norm(cov_real)))

def main():
    t0=time.time(); checks=verify_derivatives()
    (ROOT/'protocol.json').write_text(json.dumps(CONFIG,indent=2))
    rows=[]; traces=[]; teacher_rows=[]; assets={}; snapshot_assets={}
    for sigma in CONFIG['observation_noise']:
        for seed in range(CONFIG['repetitions']):
            x,phi,observed,clean,theta_true,s,W_true,init=create_data(seed,sigma)
            theta,local_trace=train_local(phi,observed,init,keep=(seed==0))
            teacher_rows.append(dict(seed=seed,noise=sigma,
                rmse_clean=float(np.sqrt(np.mean((theta@phi.T-clean)**2))),
                local_parameter_rmse=float(np.sqrt(np.mean((theta-theta_true)**2)))))
            tag=f'n{sigma:g}_s{seed}'
            for name,obj in [('x',x),('observed',observed),('clean_audit_only',clean),
                             ('teacher_theta',theta),('true_theta_audit_only',theta_true),
                             ('hidden_s_audit_only',s),('true_W_audit_only',W_true)]:
                assets[f'{tag}_{name}']=obj
            if seed==0:
                pd.DataFrame(local_trace).to_csv(OUT/f'local_training_noise_{sigma:g}.csv',index=False)
            for kind in CONFIG['initializations']:
                for degree in CONFIG['coordinator_degree']:
                    for update in CONFIG['updates']:
                        keep=(seed==0)
                        p,first,trace,snaps=fit_coordinator(theta,phi,degree,seed,kind,update,keep)
                        row=dict(seed=seed,noise=sigma,init=kind,degree=degree,update=update,
                                 stored_parameters=len(p),effective_parameters=len(p)-2,
                                 first_pass_step=first if first is not None else -1)
                        row.update(audit(p,degree,phi,theta,clean,theta_true,s));rows.append(row)
                        assets[f'{tag}_{kind}_d{degree}_{update}_final_parameters']=p
                        for r in trace:r.update(noise=sigma,seed=seed)
                        traces.extend(trace)
                        if keep:snapshot_assets[f'{tag}_{kind}_d{degree}_{update}']=snaps
            if (seed+1)%10==0:
                pd.DataFrame(rows).to_csv(OUT/'run_metrics.csv',index=False)
                print(f'noise={sigma:g}, repeats={seed+1}/30, fits={len(rows)}, elapsed={time.time()-t0:.1f}s',flush=True)
    np.savez_compressed(ROOT/'data'/'all_experiment_arrays.npz',**assets)
    np.savez_compressed(OUT/'local_parameter_trajectories.npz',**snapshot_assets)
    pd.DataFrame(rows).to_csv(OUT/'run_metrics.csv',index=False)
    pd.DataFrame(traces).to_csv(OUT/'coordination_traces.csv',index=False)
    pd.DataFrame(teacher_rows).to_csv(OUT/'teacher_metrics.csv',index=False)
    runtime=dict(seconds=time.time()-t0,python=platform.python_version(),numpy=np.__version__,
                 derivative_checks=checks,total_fits=len(rows))
    (OUT/'runtime_and_checks.json').write_text(json.dumps(runtime,indent=2))
    print(json.dumps(runtime,indent=2),flush=True)

if __name__=='__main__':main()
