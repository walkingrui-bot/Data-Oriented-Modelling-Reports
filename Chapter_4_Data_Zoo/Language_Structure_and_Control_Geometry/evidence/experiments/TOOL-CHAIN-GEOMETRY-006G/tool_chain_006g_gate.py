import json,torch,importlib.util
spec=importlib.util.spec_from_file_location('g','/mnt/data/tool_chain_006g_train.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
z=torch.load('/mnt/data/tool_chain_006g_evidence/planner.pt',map_location='cpu')
m=g.GenPlanner(z['D'],len(z['vocab']),z['emb'],z['ctx'],z['hid']);m.load_state_dict(z['state']);m.eval()
pp=g.prefix_pilot(m,350,g.SEEN_STYLES);bp=g.baseline_pilot(m,240)
gate={'prefix_exact_threshold':0.85,'canonical_final_threshold':0.65,'seen_raw_final_threshold':0.65,'passed':bool(pp['exact']>=0.85 and bp['P1_N1']>=0.65 and bp['P1_N0']>=0.65)}
res={'experiment':'TOOL-CHAIN-GEOMETRY-006G pilot gate','seed':g.SEED,'train_tasks':6000,'feature_dim':g.D,'training_nll':z['history'],'seen_styles':list(g.SEEN_STYLES),'heldout_styles':list(g.UNSEEN_STYLES),'prefix_pilot_seen':pp,'baseline_seen':bp,'prospective_gate':gate}
json.dump(res,open('/mnt/data/tool_chain_006g_evidence/pilot_gate.json','w'),indent=2)
print(json.dumps(res))
