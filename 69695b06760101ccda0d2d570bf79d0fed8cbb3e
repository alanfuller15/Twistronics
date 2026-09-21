"""Explicit schema/claim registry; unknown versions never inherit acceptance."""
ENGINES=['bm_lab','ref_lab']
CUTOFFS=[4,6]
# family, batch, adapter, path, role, scope, expected station count
FAMILIES=[
 ('preparation','v054','frame','results/prep_{engine}_N{N}/summary.json','primary','original flat-pair sampled frame replay',19),
 ('preparation_prior','v053','frame','results/prep_{engine}_N{N}/summary.json','superseded_replay','original evidence; v054 is the fresh replay of the same 76 stations',19),
 ('early_braid','v044','frame','results/early_{engine}_N{N}/summary.json','primary','first braid, deepening and flat-pair unlink legs',37),
 ('pre_ann','v043','frame','results/pre_ann_{engine}_N{N}/summary.json','primary','flat-pair connection to first annihilation',19),
 ('post_ann','v043','frame','results/post_ann_{engine}_N{N}/summary.json','primary','upper-pair connection after first annihilation',21),
 ('cleanup','v046','frame','results/cleanup_{engine}_N{N}/summary.json','primary','upper-pair cleanup after second braid',17),
 ('braid2','v042','braid','results/second_{engine}_N{N}.json','primary','second braid with sampled charge flip and singular path rejection',11),
 ('post_transfer','v042','pair','results/post_transfer_{engine}_N{N}.json','primary','post-transfer upper-pair checkpoint',1),
 ('first_ann','v042','fold','results/first_ann_{engine}_N{N}.json','primary','flat-pair fold and finite full-chart gap searches',9),
 ('upper_ann','v046','fold','results/upper_ann_{engine}_N{N}_refined.json','primary','upper-pair fold and finite full-chart gap searches',9),
 ('flat_birth','v048','fold','results/flat_birth_{engine}_N{N}_refined.json','primary','late flat-pair birth and finite full-chart gap searches',9),
 ('final_ann','v048','fold','results/final_ann_{engine}_N{N}_refined.json','primary','late flat-pair annihilation and finite full-chart gap searches',9),
 ('prep_upper_birth','v050','fold','results/prep_upper_birth_{engine}_N{N}_refined.json','primary','preparation upper-pair birth and finite full-chart gap searches',9),
 ('extra_flat_birth','v051','local_fold','results/extra_flat_birth_{engine}_N{N}.json','primary','LOCAL domain extra-pair birth; original flat roots persist',9),
 ('extra_flat_ann','v051','local_fold','results/extra_flat_ann_{engine}_N{N}.json','primary','LOCAL domain extra-pair annihilation; original flat roots persist',9),
 ('prep_lower_birth','v052','lower_fold','results/prep_lower_birth_{engine}_N{N}.json','primary','preparation lower-pair birth and finite full-chart gap searches',9),
 ('lower_unlink','v055','lower_fold','results/lower_unlink_{engine}_N{N}.json','primary','lower unlink fold and finite full-chart/edge searches',9),
 ('gapped_connections','v048','gapped','results/gapped_{engine}_N{N}/summary.json','primary','sampled gapped connections and per-band/group cycle signs',8),
 ('bridge_checkpoint','v042','gapped_checkpoint','results/bridge_{engine}_N{N}.json','corroborating_checkpoint','bridge checkpoint repeated in v048',1),
 ('endpoint_checkpoint','v042','gapped_checkpoint','results/endpoint_{engine}_N{N}.json','corroborating_checkpoint','endpoint checkpoint repeated in v048',1),
]
VERSIONS={'v042':'v042-lab-two-engine','v043':'v043','v044':'v044','v046':'v046','v048':'v048','v050':'v050','v051':'our_v051','v052':'our_v052','v053':'our_v053','v054':'our_v054','v055':'our_v055'}
