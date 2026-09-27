import importlib.util, torch, json, os, sys
spec=importlib.util.spec_from_file_location('t','/mnt/data/tool_chain_006f_train_pilot.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
z=torch.load('/mnt/data/tool_chain_006f_evidence/planner.pt',map_location='cpu')
m=t.GenPlanner(z['D'],len(z['vocab']),z['emb'],z['ctx'],z['hid']);m.load_state_dict(z['state']);m.eval()
pp=t.prefix_pilot(m,350); bp=t.baseline_pilot(m,240)
gate={'prefix_exact_threshold':0.85,'baseline_final_state_threshold':0.65,'passed':bool(pp['exact']>=0.85 and bp['final_state_accuracy']>=0.65)}
res={'training_nll':z['history'],'prefix_pilot':pp,'baseline_pilot_P1_N1':bp,'prospective_gate':gate}
json.dump(res,open('/mnt/data/tool_chain_006f_evidence/pilot_gate.json','w'),indent=2);print(json.dumps(res,indent=2))
