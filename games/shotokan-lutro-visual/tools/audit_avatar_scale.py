"""Measure the cranial cap, excluding exposed neck/chest and folded legs."""
import json,statistics
from pathlib import Path
from avatar_set_import import ROOT,SOURCE,figures,cranial_width
from PIL import Image

if __name__=='__main__':
    report=json.loads((ROOT/'docs/avatar-set-v3/import-report.json').read_text())
    for body in report['bodies']:
        cells=figures(Image.open(SOURCE/body['body']/'base-01.png').convert('RGBA'))
        reference=cranial_width(cells[0])*body['sheets'][0]['frames'][0]['scale']
        print(body['body'],'reference',round(reference,2))
        for sheet in body['sheets']:
            cells=figures(Image.open(SOURCE/body['body']/(sheet['group']+'.png')).convert('RGBA'))
            ratios=[reference/(cranial_width(c)*e['scale']) for c,e in zip(cells,sheet['frames'])]
            print(sheet['group'],','.join(str(round(r,2)) for r in ratios))
