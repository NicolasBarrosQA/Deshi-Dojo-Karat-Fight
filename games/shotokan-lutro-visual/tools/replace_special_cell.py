"""Pack existing transparent artwork, replacing one rejected source cell."""
import argparse
from pathlib import Path
from PIL import Image
from sheet_cells import figures

def run(source,replacement,frame,output):
 cells=figures(Image.open(source).convert('RGBA'),9,3,strict=False)
 fixes=figures(Image.open(replacement).convert('RGBA'),1,3,strict=False)
 for row,fix in enumerate(fixes):
  old=cells[row*9+frame-1]
  scale=old.height/fix.height
  cells[row*9+frame-1]=fix.resize((round(fix.width*scale),old.height),Image.Resampling.NEAREST)
 w=max(c.width for c in cells)+32;h=max(c.height for c in cells)+32
 sheet=Image.new('RGBA',(w*9,h*3))
 for i,c in enumerate(cells):sheet.paste(c,((i%9)*w+(w-c.width)//2,(i//9)*h+h-16-c.height))
 sheet.save(output)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('replacement',type=Path);p.add_argument('frame',type=int);p.add_argument('output',type=Path);a=p.parse_args();run(a.source,a.replacement,a.frame,a.output)
