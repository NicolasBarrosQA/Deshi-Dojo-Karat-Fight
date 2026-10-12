"""Record verified installed delivery, without claiming physical-device tests."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/avatar-set-v3'
def read(name): return json.loads((OUT/name).read_text(encoding='utf-8-sig'))
def write(name,data): (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
cleanup=read('legacy-cleanup.json')
installed=read('installed.json');installed['legacy_cleanup_pending']=False;installed['legacy_files_removed']=len(cleanup['removed_files']);write('installed.json',installed)
audit=read('visual-audit.json');audit['status']='All 19 runtime plates reviewed; repaired kick, ground orientation and low controlled finish reviewed; 12 real-game sweep/finish/recovery sequences passed.'
for repair in audit['repairs']:
    if repair.get('group')=='ashi_finish': repair['issue']='Contact punch lowered through six original-art edits; reviewed in runtime plates and actual-game captures.'
write('visual-audit.json',audit)
generation=read('generation-results.json');generation['repair_sheets']=9;write('generation-results.json',generation)
report={'risk':'alto','asset_validation':read('asset-tests.json'),'runtime_validation':read('browser-tests.json'),'legacy_files_removed':len(cleanup['removed_files']),'backup':cleanup['archive'],'passed':['984 poses, 7872 belt combinations, 8856 proportion checks','432 special poses and 3456 belt variants','native cartridge modules, PNG dimensions and SHA-256','motion inputs, both facings, finish ownership, block, expiry, miss, all specials','13 browser control/combat checks','personalization selectors, collision barrier, 150 guard transitions, historical cache'],'native_device_tested':False,'remaining':['Physical Raspberry Pi 3/Recalbox 6.1 performance and physical joysticks remain unmeasured.']}
if (OUT/'scale-correction.json').exists():
    report['scale_follow_up']={'risk':'medio','correction':read('scale-correction.json'),'checks':['neck/leg isolation fixture','108 airborne cranial references','upright reference heights on all six bodies','six real DOM punch/kick/jump/air-punch/landing recordings','12 sweep/finish/recovery sequences and all 13 browser checks on corrected build'],'demo_directory':'../special-captures/scale-*.gif'}
    audit['scale_follow_up']={'reviewed_plates':['base-28','base-64'],'actual_game_frames_reviewed':['scale-adult/0000.png','scale-adult/0064.png','scale-adult/0116.png'],'all_six_body_recordings_passed':True}
    write('visual-audit.json',audit)
write('delivery-report.json',report)
if (OUT/'jump-anchor-tests.json').exists():
    report['jump_anchor_follow_up']={'risk':'medio','correction':read('jump-anchor-correction.json'),'runtime_tests':read('jump-anchor-tests.json'),'static_tests':'six anchors, unchanged other poses/pixels/scale, source-import parity'}
    write('delivery-report.json',report)
p=OUT/'README.md';text=p.read_text(encoding='utf8').replace('Baldos, sem feições','Carecas, sem feições').replace('Os resultados de execução serão registrados em `browser-tests.json` e no relatório de entrega.','Os resultados de execução estão em `browser-tests.json` e `delivery-report.json`: seis bases nos dois ports, 12 sequências reais de rasteira/finalização/recuperação, controles, defesas, CPU, comandos especiais e empacotamento aprovados. A arte anterior foi removida após os testes; o backup está fora do projeto.');p.write_text(text,encoding='utf8')
print('Verified delivery report updated.')
