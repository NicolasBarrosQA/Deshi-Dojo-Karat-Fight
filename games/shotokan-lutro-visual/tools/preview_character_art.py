"""Inspect imported art at native size and integer nearest-neighbor zoom."""
from pathlib import Path
import statistics
from PIL import Image,ImageDraw
from import_characters import HERE,binary
from sheet_cells import figures

def sample(body):
    path=HERE/'assets/source/characters-v2'/body/'karateca-sheet.png'
    cells=figures(binary(Image.open(path)),4,3)
    scale={'teen':112,'child':94}[body]/statistics.median(c.height for c in cells)
    result=[]
    for i,cell in enumerate(cells):
        resized=cell.resize((round(cell.width*scale),round(cell.height*scale)),Image.Resampling.NEAREST)
        original=Image.open(HERE/'src/assets'/f'pose-{i+1:02d}.png').getbbox()
        relative=((original[0]+original[2])/2-112)*({'teen':112,'child':94}[body]/128)
        frame=Image.new('RGBA',(224,144));frame.paste(resized,(round(112+relative-resized.width/2),143-resized.height));result.append(frame)
    return result

def main():
    rows=[('ADULTO ORIGINAL',[Image.open(HERE/'src/assets'/f'pose-{i:02d}.png') for i in range(1,13)])]
    for body in ('teen','child'):
        old=Image.open(HERE/'docs'/f'character-{body}-v1-rejected-atlas.png')
        rows.append((body.upper()+' ANTERIOR',[old.crop(((i%4)*224,(i//4)*144,(i%4+1)*224,(i//4+1)*144)) for i in range(12)]))
        rows.append((body.upper()+' V2',sample(body)))
    board=Image.new('RGB',(3*224+180,len(rows)*155),(21,29,35));d=ImageDraw.Draw(board)
    for row,(name,frames) in enumerate(rows):
        d.text((8,row*155+60),name,fill='white')
        for col,pose in enumerate((0,2,7)):
            frame=frames[pose].convert('RGBA');board.paste(frame,(180+col*224,row*155),frame)
    board.save(HERE/'docs/character-art-v2-native-review.png')
    zoom=Image.new('RGB',(5*168*2,144*2+24),(21,29,35));d=ImageDraw.Draw(zoom)
    for i,(name,frames) in enumerate(rows):
        im=frames[0].convert('RGBA').crop((28,0,196,144)).resize((336,288),Image.Resampling.NEAREST)
        d.text((i*336+6,5),name,fill='white');zoom.paste(im,(i*336,24),im)
    zoom.save(HERE/'docs/character-art-v2-zoom-review.png')

if __name__=='__main__':main()
