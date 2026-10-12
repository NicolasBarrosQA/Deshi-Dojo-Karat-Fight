"""Persist complete 2D art jobs and choreography references; no game mutations."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/source/avatar-set-v3'
BODIES = {'adult':'adulto-masculino', 'teen':'adolescente-masculino',
          'child':'crianca-masculina', 'adult_female':'adulta-feminina',
          'teen_female':'adolescente-feminina', 'child_female':'crianca-feminina'}
DESCRIPTIONS = [
    'Kamae guard, front fist protecting chest, rear hand ready, knees flexed',
    'Same kamae guard, subtle breathing and weight shift',
    'Short sliding step, rear foot closing distance, hands stay in guard',
    'Middle of advancing sliding step, front knee slightly bent, guard maintained',
    'Complete sliding step, both feet stable, recover guard',
    'Gyaku-zuki preparation, rear fist chambered at hip, opposite leg forward',
    'Gyaku-zuki hip rotation beginning, rear fist advances, lead hand retracts',
    'Gyaku-zuki halfway straight extension, rear shoulder turning forward',
    'Gyaku-zuki fully extended straight chest punch, punching arm OPPOSITE forward leg',
    'Gyaku-zuki controlled contact, aligned wrist, grounded opposite leg stance',
    'Gyaku-zuki retracting punching arm toward chest, regain coverage',
    'Return to balanced kamae guard after punch',
    'Age-uke preparation, arm crossing lower chest, other fist chambered',
    'Age-uke rising bent forearm diagonally in front of face',
    'Age-uke complete high block, bent forearm above forehead, fist not punching upward',
    'Gedan-barai preparation, executing fist near opposite ear',
    'Gedan-barai diagonal downward sweep across torso, other arm retracting',
    'Gedan-barai completed low block near forward thigh, stable grounded stance',
    'Soto-uke preparation, executing fist outside near same-side ear',
    'Soto-uke forearm arcs from outside inward across chest',
    'Soto-uke complete middle block, bent elbow down, fist at shoulder height',
    'Uchi-uke preparation, executing fist tucked inside under opposite arm',
    'Uchi-uke opening bent forearm outward from inside',
    'Uchi-uke completed outward middle block, elbow close to torso',
    'Mae-geri preparation, transfer weight to supporting leg, hands guard',
    'Mae-geri knee chambered high, lower leg folded, toes pulled back',
    'Mae-geri completed front kick to waist, ball of bare foot leads, support foot grounded',
    'Mae-geri retract lower leg back to knee chamber, hands guard',
    'Low mae-geri preparation, hands guard, weight on supporting leg',
    'Low mae-geri lower knee chamber, support knee slightly bent',
    'Low mae-geri extension diagonally forward downward to shin height',
    'Low mae-geri retraction to low knee chamber',
    'Mawashi-geri preparation, hips starting to pivot',
    'Mawashi-geri lateral knee chamber, knee aimed sideways, heel near hip',
    'Mawashi-geri circular extension at waist height, foot horizontal instep leads',
    'Mawashi-geri retraction to lateral chamber, support foot still pivoted',
    'Oi-zuki beginning step with same-side forward arm preparing',
    'Oi-zuki passing feet, same-side forward fist beginning extension',
    'Oi-zuki contact, punching arm SAME side as forward leg, upright torso',
    'Oi-zuki retracting to guard after advancing punch',
    'Gyaku-zuki jodan rear fist preparation, opposite leg forward',
    'Gyaku-zuki jodan half extension, hip rotation toward head-height target',
    'Gyaku-zuki jodan full straight head-height punch, not uppercut',
    'Gyaku-zuki jodan retracting arm to guard',
    'Kizami-zuki lead fist preparation, SAME arm as forward leg',
    'Kizami-zuki lead straight punch half extension',
    'Kizami-zuki lead fist full chest-height extension, rear hand guards chin',
    'Kizami-zuki recover guard, no change of base',
    'Yoko-geri preparation, shift weight, turn hip sideways',
    'Yoko-geri chamber, knee folded across front of body, heel tucked',
    'Yoko-geri side kick full extension toward right, heel leads, supporting foot pivoted',
    'Yoko-geri side kick folded retraction, maintain balance',
    'High mawashi preparation, hip begins pivot',
    'High mawashi lateral knee chamber at waist height',
    'High mawashi circular extension at head height, instep horizontal',
    'High mawashi retraction to lateral knee chamber',
    'Ushiro preparation, look over shoulder toward opponent on screen right',
    'Ushiro turn back toward opponent, kicking knee folded below hip',
    'Ushiro straight backward heel thrust toward screen right, torso angled toward left',
    'Ushiro recoil kicking knee, begin turn back to guard',
    'Jump preparation, crouch with both knees flexed, hands guard',
    'Jump ascent, both knees partially tucked, both feet clear of ground',
    'Jump apex, bent knees naturally tucked, same body and HEAD SIZE as standing',
    'Jump landing, knees flexed absorbing impact, hands guard',
    'Air front-kick preparation, both feet airborne, torso upright',
    'Air front-kick knee chamber, other leg naturally bent',
    'Air front-kick extension toward screen right, ball of foot leads, no grounded foot',
    'Air front-kick rechamber both legs before landing',
    'Air straight-punch preparation, both feet airborne, knees bent',
    'Air straight-punch half extension, rear shoulder turning',
    'Air straight-punch full extension to right, fist aligned, both legs naturally tucked',
    'Air straight-punch retract to guard, both knees ready for landing',
    'Air mawashi preparation, both legs airborne',
    'Air mawashi lateral chamber, hips rotating, other knee bent',
    'Air mawashi circular extension right, instep horizontal, no support foot',
    'Air mawashi folded retraction before landing',
    'Air side-kick preparation, tuck both knees',
    'Air side-kick chamber knee across body, turn hip sideways',
    'Air side-kick heel extension to right, other leg bent, both feet airborne',
    'Air side-kick retract and prepare landing',
    'Air reverse kick preparation, torso turns left, look toward right',
    'Air reverse kick chamber heel under hip, both feet airborne',
    'Air reverse kick straight heel extension to right with back toward opponent',
    'Air reverse kick retract and turn toward guard',
    'Torso-hit reaction, slightly bend trunk backward, arms open briefly, both feet planted',
    'Head-hit reaction, head tilts back slightly, shoulders recoil, hands protect face',
    'Recover from impact, knees bent, hands drawing back toward guard',
    'Stable kamae after impact recovery',
    'Low gyaku preparation, squat lower with both knees flexed, rear fist chambered',
    'Low gyaku hip rotation, rear fist beginning straight projection',
    'Low gyaku fully extended chest punch from lowered stance, opposite leg forward',
    'Low gyaku retracting to low guard, both feet grounded',
]
SPECIALS = {
    'ashi_barai': ['guard','short distance adjustment','weight onto support leg','hip rotation, sweeping leg opens low','low circular sweep starts','bare sweeping foot crosses opponent ankle line at floor level','follow through low arc, trunk balanced','retract sweeping leg','recover upright guard'],
    'ashi_finish': ['identify fallen opponent to right','short approach step','establish stable wide base','bend knees and hip lowering torso','chamber rear fist','straight controlled punch diagonally down toward fallen torso','hold controlled contact pose, remain standing with knees flexed','retract arm','return to zanshin guard'],
    'knockdown': ['ankle loses support, hands open','trunk tips backward to screen RIGHT, knees buckle','hips descending, arms open to brace','halfway fall, torso diagonal, no abrupt rotated standing sprite','fully down on back or side, HEAD on screen RIGHT, feet screen LEFT','stay lying on floor, head right feet left','short ground contact reaction, remain lying, head right feet left','rise through side support on hand and bent knee, head lifts gradually','stand and recover guard'],
    'ura_mawashi': ['guard','prepare turn hip','raise knee chamber','begin reverse circular arc','high reverse hook extension','heel hooks inward toward screen RIGHT at head height','fold knee after hook','return foot to floor','recover guard'],
    'ushiro': ['guard','look over shoulder to right','rotate torso, back faces opponent on right','chamber heel below hip','begin straight BACKWARD heel extension to screen right','full straight backward heel strike to right, torso leaning left','retract knee','turn torso back toward opponent','recover guard'],
    'tai_sabaki': ['guard','short evasive diagonal step backward','rotate trunk away from incoming right-side punch','lean slightly off line without falling','finish evasive rotation, hands guard','stable repositioned base','rear fist chambered for optional counter','controlled gyaku-zuki counter extension to right','return guard'],
    'renzoku': ['guard','lead fist begins first straight punch','first lead punch full extension','retract lead fist while chambering rear fist','hip transfers and rear fist half extends','second reverse punch fully extended, visually different arm','hold controlled second contact','retract rear arm','recover guard'],
    'nidan': ['guard','crouch for takeoff','jump with first knee chambered','FIRST front kick fully extends to right, other leg bent','fold first knee and chamber OPPOSITE knee in midair','SECOND front kick with OPPOSITE leg fully extends to right','both knees tuck after second kick','landing knees flexed','recover guard'],
}

def unpack(part, i):
    f = part['frames'][i]
    a = Image.open(ROOT/'src/assets'/(part['right']+'.png')).convert('RGBA')
    result = Image.new('RGBA', (224, 144))
    result.paste(a.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']))
    return result

def main():
    assert len(DESCRIPTIONS)==92
    OUT.mkdir(parents=True,exist_ok=True)
    refs=OUT/'references';refs.mkdir(exist_ok=True)
    atlas=Image.open(ROOT/'docs/character-adult-atlas.png').convert('RGBA')
    specials=json.loads((ROOT/'assets/special-assets.json').read_text())['adult']
    groups=[]
    for start in range(0,92,9):
        indices=list(range(start,min(start+9,92)))
        name=f'base-{start+1:02d}'
        frames=[atlas.crop(((i%4)*224,(i//4)*144,(i%4+1)*224,(i//4+1)*144)) for i in indices]
        while len(frames)<9:frames.append(frames[-1])
        groups.append((name,frames,[DESCRIPTIONS[i] for i in indices],indices))
    for name,descriptions in SPECIALS.items():
        a=specials[name]
        frames=[Image.alpha_composite(unpack(a['body'],i),unpack(a['belts']['preta'],i)) for i in range(9)]
        groups.append((name,frames,descriptions,list(range(9))))
    jobs=[]
    for group,frames,descriptions,indices in groups:
        reference=Image.new('RGBA',(224*3,144*3))
        for i,frame in enumerate(frames):reference.paste(frame,((i%3)*224,(i//3)*144))
        reference=reference.resize((2016,1296),Image.Resampling.NEAREST)
        reference.save(refs/(group+'.png'))
        for body,name in BODIES.items():
            folder=OUT/body;folder.mkdir(exist_ok=True)
            subject=('child aged 8' if body.startswith('child') else 'adolescent' if body.startswith('teen') else 'adult') + (' female' if body.endswith('_female') else ' male')
            prompt=(f'Create original HAND DRAWN 2D karate fighting-game animation art of the {subject} in reference image 1. '
                'Image 1 is the APPROVED EXACT body, age, proportions, bald blank featureless head, skin tone, white karate gi design and fine outlined illustrated style. '
                'Image 2 is the APPROVED combat pose art style and character continuity. Image 3 is ONLY the old choreography reference; NEVER copy its face, hair, old body design or coarse pixel style. '
                'Render exactly NINE complete full-body poses in a square 3-column by 3-row sheet, ordered left to right then top to bottom, all with generous transparent margins, no touching between figures, no cropped hands/feet. '
                'All poses have exactly the SAME head size, limb lengths and body scale; crouching, jumping or lying changes posture, never person size. '
                'Opponent always at SCREEN RIGHT; for turning kicks torso may turn away, but strike remains toward RIGHT. '
                'Use high quality clean dark contour lines, detailed coherent anatomy, subtle cool white gi folds, warm neutral skin, exactly TWO arms and TWO legs, closed anatomical fists and true bare feet. '
                'The face is completely blank with NO eyes, eyebrows, mouth or nose, no hair. FULLY CLOTHED modest loose white karategi; preserve undershirt if present in reference. '
                'PRODUCTION MASK REQUIREMENT: draw ONLY the BELT (waistband, knot and BOTH hanging ends) in bright saturated MAGENTA/PINK instead of white. '
                'The belt keeps fabric folds and dark outline, but its entire cloth interior is unmistakably magenta, never black or white. All other cloth remains WHITE. No pink anywhere else. This marker will become a white belt during import. '
                'No 3D rendering, no mannequin joints, no stick figures, no labels, no grid, no numbers, no shadows, no floor, no motion trails, no effects. True transparent alpha background. '
                'Draw these specific ordered poses:\n' + '\n'.join(f'{i+1}. {d}.' for i,d in enumerate(descriptions)))
            if len(descriptions)<9:prompt+='\nFill remaining cells by repeating the final recovery pose; only first two cells are used.'
            jobs.append({'body':body,'group':group,'indices':indices,'target':str((folder/(group+'.png')).resolve()),
                'references':[str((ROOT/'assets/source/avatar-bases-v2'/(name+'.png')).resolve()),str((ROOT/'assets/source/avatar-poses-2d-v1'/(name+'.png')).resolve()),str((refs/(group+'.png')).resolve())], 'prompt':prompt})
    (OUT/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'{len(jobs)} persisted original art jobs; {6*(92+72)} production poses.')

if __name__=='__main__':main()
