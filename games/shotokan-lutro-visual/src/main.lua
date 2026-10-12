-- Two-player arcade combat on Lua 5.1 / historical Lutro.
-- Physical bodies, buffered inputs and technique events are separate systems.
local g=lutro.graphics
local skills=require('techniques')
local art=require('art')
local CPU=require('cpu')
local Characters=require('characters')
local Specials=require('specials')
local Ceremony=require('ceremony')
local rules=skills.arcade
local W,H,FLOOR=224,144,195
local image,fontQuad={},{}
local previous={{},{}}
local physicalPrevious={{},{}}
local keys={'up','down','left','right','b','y','a','select','start'}
local indices={up=5,down=6,left=7,right=8,b=1,y=2,a=9,select=3,start=4}
Scene={tick=0,freeze=0,flash=0,debug=false,demo=false,practice=false,lesson='gyaku',players={},wins={0,0},mode='cpu',difficulty='easy',menu=false}
local function clamp(v,a,b) return math.max(a,math.min(b,v)) end
local function color(r,b,c) g.setColor(r,b,c,255) end
local function box(x,y,w,h,r,b,c,outline)
 color(r,b,c)
 g.rectangle(outline and 'line' or 'fill',math.floor(x),math.floor(y),math.floor(w),math.floor(h))
end
local function text(s,x,y)
 color(255,255,255)
 for i=1,#s do
  local q=fontQuad[string.byte(s,i)]
  if q then g.draw(image.font,q,x+(i-1)*6,y) end
 end
end
local function centered(s,y) text(s,math.floor((384-#s*6)/2),y) end
local function total(t)
 local n=0 for _,v in ipairs(t.durations) do n=n+v end return n
end
local function poseAt(t,age)
 local n=0
 for i,d in ipairs(t.durations) do n=n+d if age<=n then return t.poses[i] end end
 return t.poses[#t.poses]
end
local function phaseAt(t,a)
 if a.age<=t.windup then return 'PREPARA' end
 if t.kind=='defense' then
  local line=({jodan='ALTA',chudan='MEDIA',gedan='BAIXA'})[t.zone]
  return (a.id~='kamae' and a.age<=t.windup+3 and 'RECEBE ' or 'GUARDA ')..line
 end
 return a.age<=t.windup+t.active and 'GOLPE' or 'RECOLHE'
end
local function newPlayers()
 Scene.players={}
 for i=1,2 do
  Scene.players[i]={x=i==1 and 104 or 280,face=i==1 and 1 or -1,pose=1,walk=0,age=0,
   action=nil,stun=0,blockstun=0,points=0,contacts=0,blocks=0,parries=0,counter=0,phase='KAMAE',
   air=false,height=0,vy=0,jumpAge=0,jumpVX=0,landing=0,low=false,
   chain=0,chainTime=0,lastTechnique=nil,queued=nil,jumps=0,maxChain=0,executed=0,
   energy=rules.energy,knockVX=0,cooldown=0,comboHits=0,comboTicks=0,inputs={},character=Characters.definition(i)}
  Specials.init(Scene.players[i])
 end
 Scene.left=1 Scene.freeze=0 Scene.flash=0 Scene.lastContact=nil
 Scene.timer=rules.round_ticks Scene.result=nil Scene.roundWait=0 Scene.impact=nil
 Scene.cpu=CPU.new(Scene.difficulty,103+Scene.round*977)
 Ceremony.start(Scene)
end
function Scene.character(port,definition)
 local d=Characters.select(port,definition)
 if Scene.players[port] then Scene.players[port].character=d end
 return d
end
function Scene.student(port,id)
 local d=Characters.student(port,id)
 if Scene.players[port] then Scene.players[port].character=d end
 return d
end
function Scene.reset(skipIntro)
 Scene.tick=0 Scene.wins={0,0} Scene.round=1 Scene.matchWinner=nil
 Scene.message='SOCO > SOCO > CHUTE' Scene.messageTicks=100
 newPlayers() previous={{},{}} physicalPrevious={{},{}} Scene.menu=false
 if skipIntro then Ceremony.finish(Scene) end
end
local menuOptions={{mode='cpu',level='easy',label='CPU FACIL'},
 {mode='cpu',level='medium',label='CPU MEDIO'},
 {mode='cpu',level='hard',label='CPU DIFICIL'},
 {mode='versus',level='easy',label='2 JOGADORES'},
 {port=1,field='belt',label='P1 FAIXA'},
 {port=2,field='belt',label='P2 FAIXA'},
 {port=1,field='student',label='P1 ALUNO'}, {port=2,field='student',label='P2 ALUNO'}}
function Scene.configure(mode,level,skipIntro)
 assert(mode=='cpu' or mode=='versus','Unknown match mode')
 assert(CPU.profiles[level],'Unknown difficulty')
 Scene.mode=mode Scene.difficulty=level Scene.demo=false
 Scene.reset(skipIntro)
end
local function openMenu()
 Scene.menu=true
 for i,option in ipairs(menuOptions) do
  if option.mode==Scene.mode and (option.mode=='versus' or option.level==Scene.difficulty) then Scene.menuChoice=i break end
 end
end
local function horizontal(input,face)
 if input.left==input.right then return 0 end
 return (input.right and 1 or -1)==face and 1 or -1
end
local function modifier(input,face)
 if input.up~=input.down then return input.up and 'up' or 'down' end
 local h=horizontal(input,face)
 return h==1 and 'forward' or h==-1 and 'back' or 'neutral'
end
local function choose(kind,input,p)
 local m=modifier(input,p.face)
 if kind=='defense' then return ({up='age',down='gedan',forward='soto',back='uchi',neutral='kamae'})[m] end
 if p.air then return kind=='punch' and 'air_tsuki' or 'tobi_mae' end
 if kind=='kick' then return m=='forward' and 'mawashi' or m=='down' and 'mae_low' or 'mae' end
 if m=='up' then return 'jodan' end
 if m=='down' then return 'gyaku_low' end
 if m=='forward' then return 'gyaku_step' end
 if m=='back' then return 'gyaku' end
 -- Repeated neutral punch naturally links the lead hand into the reverse hand.
 local current=p.action and p.action.id or p.chainTime>0 and p.lastTechnique
 return current=='kizami' and 'gyaku' or 'kizami'
end
local function links(from,to)
 for _,id in ipairs(skills.links[from] or {}) do if id==to then return true end end
 return false
end
local function startAction(p,id)
 local t=skills.techniques[id]
 local old=p.action
 if t.kind=='defense' and old and skills.techniques[old.id].kind=='defense' then
  if old.age>skills.techniques[old.id].windup then p.coverage=old.id end
 else p.coverage=nil end
 local linked=t.kind=='attack' and not p.air and p.chainTime>0 and p.chain<skills.combo.max_links and links(p.lastTechnique,id)
 if t.kind=='attack' then
  p.chain=linked and p.chain+1 or 1
  p.chainTime=skills.combo.idle_ticks p.lastTechnique=id p.executed=p.executed+1
  p.maxChain=math.max(p.maxChain,p.chain)
 else p.chain=0 p.chainTime=0 p.lastTechnique=nil end
 p.action={id=id,age=1,spent=false,counter=p.counter>0,link=p.chain,
  step=(t.step or 0)+(linked and (t.link_step or 0) or 0)}
 p.counter=0 p.age=1 p.pose=t.poses[1] p.low=t.low or false p.queued=nil
 p.phase='PREPARA'
end
local function move(p,dx) p.x=clamp(p.x+dx,rules.stage_min,rules.stage_max) end
-- Preserve the order from before movement, never from already overlapping positions.
-- Correction follows who moved into the barrier; an idle opponent is not dragged.
function Scene.resolveBodies(leftIndex,old)
 local l,r=Scene.players[leftIndex],Scene.players[3-leftIndex]
 local k=l.knockdown or r.knockdown
 local separation=k and skills.special_rules.ground_push_distance or rules.push_distance
 if k and k.rising then separation=separation+(rules.push_distance-separation)*math.min(1,k.rising/skills.special_rules.rise_ticks) end
 local penetration=l.x+separation-r.x
 if penetration>0 then
  local lc=math.max(0,l.x-old[leftIndex]);local rc=math.max(0,old[3-leftIndex]-r.x)
  local weight=lc+rc
  local share=weight>0 and lc/weight or .5
  l.x=l.x-penetration*share r.x=r.x+penetration*(1-share)
  if l.x<rules.stage_min then l.x=rules.stage_min r.x=math.max(r.x,l.x+separation) end
  if r.x>rules.stage_max then r.x=rules.stage_max l.x=math.min(l.x,r.x-separation) end
 end
 l.x=clamp(l.x,rules.stage_min,rules.stage_max)
 r.x=clamp(r.x,rules.stage_min,rules.stage_max)
 Scene.left=leftIndex
end
local function zoneBox(p,zone)
 if p.knockdown then return {x=p.x-34,y=178,w=68,h=17} end
 local bounds=art.bounds[p.pose] or {60,14,166,142}
 local top=FLOOR-H+bounds[2]-p.height
 local height=bounds[4]-bounds[2]
 local bands={jodan={.02,.21},chudan={.23,.60},gedan={.62,.92}}
 local z=bands[zone]
 return {x=p.x+p.face*12-22,y=top+height*z[1],w=44,h=height*(z[2]-z[1])}
end
local function hit(p)
 local a=p.action
 if not a or a.spent then return nil end
 local t=skills.techniques[a.id]
 if t.kind~='attack' or a.age<=t.windup or a.age>t.windup+t.active then return nil end
 local h=t.hit
 return {x=p.face==1 and p.x+h.near or p.x-h.far,y=h.y-p.height,w=h.far-h.near,h=h.h}
end
local function overlap(a,b)
 return a.x<b.x+b.w and a.x+a.w>b.x and a.y<b.y+b.h and a.y+a.h>b.y
end
local function defended(p,zone)
 local a=p.action
 if not a or p.stun>0 or p.air then return false,false,nil,'indisponivel' end
 local t=skills.techniques[a.id]
 if t.kind~='defense' then return false,false,nil,'sem guarda' end
 local prepared=a.age>t.windup
 local id=prepared and a.id or p.coverage
 if not id then return false,false,nil,'preparando' end
 local covers=id=='kamae' and (zone=='jodan' or zone=='chudan') or skills.techniques[id].zone==zone
 return covers,covers and prepared and a.age<=t.windup+3 and a.id~='kamae',covers and id or nil,covers and 'coberto' or 'linha descoberta'
end
Scene.defended=defended
Scene.zoneBox=zoneBox
local function jump(p,input)
 p.air=true p.height=0 p.vy=0 p.jumpAge=0 p.jumpVX=horizontal(input,p.face)*p.face*2.1
 p.pose=61 p.jumps=p.jumps+1 p.chain=0 p.chainTime=0 p.queued=nil p.low=false p.airUsed=false
 p.phase='IMPULSAO'
end
local function flight(p)
 if not p.air then return end
 p.jumpAge=p.jumpAge+1
 if p.jumpAge==3 then p.vy=5.3 end
 if p.jumpAge>=3 then
  p.height=p.height+p.vy p.vy=p.vy-.34 move(p,p.jumpVX)
  if p.height<=0 then
   p.height=0 p.vy=0 p.air=false p.landing=2 p.action=nil p.queued=nil
   p.pose=64 p.phase='POUSAR' p.chain=0 p.chainTime=0
  end
 end
end
local function lessonInput(i)
 local t=skills.techniques[Scene.lesson] or skills.techniques.gyaku
 local n=Scene.tick%150
 if n==1 then Scene.players[1].x=142 Scene.players[2].x=238 end
 local input={}
 if t.kind=='defense' then
  if i==1 and n>=15 and n<=70 then
   input.y=true
   if t.direction=='up' then input.up=true elseif t.direction=='down' then input.down=true
   elseif t.direction=='forward' then input.right=true elseif t.direction=='back' then input.left=true end
  end
  if i==2 and n==28 then input.b=t.zone~='gedan';input.a=t.zone=='gedan';input.up=t.zone=='jodan';input.down=t.zone=='gedan' end
 elseif i==1 then
  if t.air and n==15 then input.up=true end
  if n==25 then input[t.button=='punch' and 'b' or 'a']=true end
 end
 return input
end
local function finishRound()
 if Scene.practice or Scene.demo or Scene.result then return end
 local a,b=Scene.players[1],Scene.players[2]
 if a.energy>0 and b.energy>0 and Scene.timer>0 then return end
 local winner=a.energy>b.energy and 1 or b.energy>a.energy and 2 or 0
 Scene.result=winner Scene.roundWait=95
 if winner>0 then
  Scene.wins[winner]=Scene.wins[winner]+1
  if Scene.wins[winner]>=rules.rounds_to_win then Scene.matchWinner=winner end
 end
 Scene.message=winner==0 and 'EMPATE' or (winner==2 and Scene.mode=='cpu' and 'CPU' or 'P'..winner)..' VENCEU O ROUND'
 Scene.messageTicks=95
end
function Scene.advance()
 Scene.tick=Scene.tick+1
 local input={}
 for i=1,2 do
  input[i]={}
  for _,k in ipairs(keys) do input[i][k]=lutro.joystick.isDown(i,indices[k]) end
 end
 local physical={input[1],input[2]}
 local oldPhysical=physicalPrevious
 physicalPrevious=physical
 for i=1,2 do
  if physical[i].select and not oldPhysical[i].select then
   if Scene.menu then Scene.menu=false previous[1]=physical[1]
    if Scene.mode=='versus' then previous[2]=physical[2] end
   else openMenu() end
   return
  end
 end
 if Scene.menu then
  for i=1,2 do
   local c,old=physical[i],oldPhysical[i]
   if (c.up and not old.up) or (c.left and not old.left) then Scene.menuChoice=(Scene.menuChoice-2)%#menuOptions+1
   elseif (c.down and not old.down) or (c.right and not old.right) then Scene.menuChoice=Scene.menuChoice%#menuOptions+1 end
   if (c.start and not old.start) or (c.b and not old.b) or (c.a and not old.a) then
    local option=menuOptions[Scene.menuChoice]
    if option.port then
     local values=Characters.data[option.field=='student' and 'student_order' or option.field=='body' and 'body_order' or 'belt_order']
     local current=option.field=='student' and Characters.selected[option.port] or Characters.definition(option.port)[option.field];local nextIndex=1
     for n,value in ipairs(values) do if value==current then nextIndex=n%#values+1 end end
     if option.field=='student' then Scene.student(option.port,values[nextIndex]) else Scene.character(option.port,{[option.field]=values[nextIndex]}) end
    else Scene.practice=false Scene.configure(option.mode,option.level) end
    physicalPrevious=physical previous=physical return
   elseif c.y and not old.y then
    Scene.menu=false previous[1]=physical[1]
    if Scene.mode=='versus' then previous[2]=physical[2] end
    return
   end
  end
  return
 end
 for i=1,2 do
  if physical[i].start and not oldPhysical[i].start then
   Scene.reset() physicalPrevious=physical previous=physical return
  end
  if Scene.demo then input[i]=lessonInput(i) end
 end
 if Ceremony.update(Scene) then
  -- Consume button edges during the greeting; no motion/buffer reaches combat.
  previous=physical
  return
 end
 if Scene.mode=='cpu' and not Scene.demo then
  input[2]=Scene.result and {} or CPU.update(Scene.cpu,Scene.players[2],Scene.players[1],Scene.freeze>0)
 end
 for i=1,2 do Scene.players[i].inputs=input[i] end
 if Scene.flash>0 then Scene.flash=Scene.flash-1 end
 if Scene.messageTicks>0 then Scene.messageTicks=Scene.messageTicks-1 end
 if Scene.result then
  Scene.roundWait=math.max(0,Scene.roundWait-1)
  if Scene.roundWait==0 and not Scene.matchWinner then
   Scene.round=Scene.round+1 newPlayers() Scene.message='ROUND '..Scene.round Scene.messageTicks=55
  end
  previous=input return
 end
 -- Capture button edges before hitstop/stun. Buffer survives all temporary locks.
 for i,p in ipairs(Scene.players) do
  local c=input[i]
  local punch=c.b and not previous[i].b;local kick=c.a and not previous[i].a
  -- A fresh defense command replaces an older buffered attack. A later fresh
  -- punch while holding defense can still request a deliberate counterattack.
  if c.y and not previous[i].y then p.queued=nil end
  local special=Specials.request(Scene,i,c,previous[i])
  if not special and (punch or kick) and not (c.y and not previous[i].y) and not (p.air and p.airUsed) then
   local id=choose(punch and 'punch' or 'kick',c,p)
   if Scene.demo and i==1 then id=Scene.lesson end
   p.queued={id=id,ttl=skills.combo.buffer_ticks}
  end
 end
 if Scene.freeze>0 then Scene.freeze=Scene.freeze-1 previous=input return end
 if not Scene.practice and not Scene.demo then Scene.timer=math.max(0,Scene.timer-1) end
 local old={Scene.players[1].x,Scene.players[2].x}
 local leftIndex=old[1]<old[2] and 1 or old[2]<old[1] and 2 or Scene.left
 for i,p in ipairs(Scene.players) do
  p.ceremonyPose=nil
  local c=input[i];local other=Scene.players[3-i]
  if not p.action and not p.air and not p.special and not p.knockdown then p.face=i==leftIndex and 1 or -1 end
  p.counter=math.max(0,p.counter-1) p.cooldown=math.max(0,p.cooldown-1)
  p.comboTicks=math.max(0,p.comboTicks-1)
  if p.comboTicks==0 then p.comboHits=0 end
  if p.queued then p.queued.ttl=p.queued.ttl-1 if p.queued.ttl<0 then p.queued=nil end end
  if not p.action then p.chainTime=math.max(0,p.chainTime-1) end
  if p.air and p.height==0 and p.jumpAge<3 and c.y then
   p.air=false p.jumpAge=0 p.jumpVX=0 p.jumps=p.jumps-1 p.queued=nil
   startAction(p,choose('defense',c,p))
  end
  local specialLocked=Specials.update(Scene,i,move)
  if not specialLocked then flight(p) end
  if math.abs(p.knockVX)>.05 then move(p,p.knockVX);p.knockVX=p.knockVX*.72 end
  if specialLocked then
   p.queued=nil
  elseif p.stun>0 then
   p.stun=p.stun-1 p.pose=p.air and 63 or p.reaction or 85 p.low=false p.phase='IMPACTO'
   if p.stun==0 then p.pose=1 p.phase='KAMAE' end
  elseif p.blockstun>0 then
   p.blockstun=p.blockstun-1 p.phase='DEFENDE'
  elseif p.landing>0 then p.landing=p.landing-1 p.pose=64 p.phase='POUSAR'
  else
   local a=p.action;local t=a and skills.techniques[a.id]
   if a and t.kind=='attack' then
    if a.step>0 and a.age<=t.windup then move(p,p.face*a.step/t.windup) end
    a.age=a.age+1 p.age=a.age p.pose=poseAt(t,a.age) p.phase=phaseAt(t,a)
    local queued=p.queued
    if queued and not p.air and p.chain<skills.combo.max_links and a.age>=t.link_at and links(a.id,queued.id) then
     startAction(p,queued.id)
    elseif a.age>total(t) then
     p.action=nil p.pose=p.air and 63 or 1 p.phase=p.air and 'SALTO' or 'KAMAE'
     -- Only an authored link can skip the end of an attack. Starting a new
     -- string (including repeating the same technique) must leave a response
     -- window. Walking, jumping and guarding remain available during it.
     if not t.air then p.cooldown=skills.combo.restart_ticks end
    end
   elseif a and t.kind=='defense' then
    if p.queued and p.cooldown==0 then startAction(p,p.queued.id)
    elseif not c.y then p.action=nil p.guard=false p.pose=1 p.phase='KAMAE'
    else
     local id=choose('defense',c,p)
     if id~=a.id then startAction(p,id)
     else a.age=a.age+1 p.age=a.age p.pose=poseAt(t,a.age) p.phase=phaseAt(t,a) end
     if c.left~=c.right then move(p,(c.right and 1 or -1)*.85) end
    end
   elseif p.air then
    if p.queued and not p.airUsed and p.jumpAge>=3 then
     local id=p.queued.id p.airUsed=true startAction(p,id)
    else p.pose=p.jumpAge<3 and 61 or p.vy>1 and 62 or 63 p.phase='SALTO' end
   elseif p.queued and p.cooldown==0 then startAction(p,p.queued.id)
   elseif c.y then startAction(p,choose('defense',c,p))
   elseif c.up and not c.down and not previous[i].up then jump(p,c)
   -- Keep the existing low-base collision bands; draw authored kiba instead.
   elseif c.down and not c.up then p.low=true p.pose=90 p.ceremonyPose={group='ceremony',frame=9} p.phase='KIBA-DACHI'
   elseif c.left~=c.right then
    p.low=false local dir=c.right and 1 or -1
    move(p,dir*(dir==p.face and rules.walk_speed or rules.back_speed))
    p.walk=p.walk+1
    local stride={1,3,4,5,4,3};local n=math.floor(p.walk/4)%#stride
    p.pose=stride[dir==p.face and n+1 or #stride-n] p.phase='DESLOCAR'
   else p.low=false p.walk=0 p.pose=Scene.tick%48<36 and 1 or 2 p.phase='KAMAE' end
  end
  p.guard=p.action and skills.techniques[p.action.id].kind=='defense' or false
 end
 Scene.resolveBodies(leftIndex,old)
 -- Determine trades from the same state before applying either reaction.
 local events={}
 for i,p in ipairs(Scene.players) do
  local h=hit(p);local act=p.action
  if h and not Scene.players[3-i].knockdown then
   local t=skills.techniques[act.id];local target=Scene.players[3-i]
   local zone=nil;local best=0
   for _,z in ipairs({t.zone,'jodan','chudan','gedan'}) do
    local b=zoneBox(target,z)
    if overlap(h,b) then
     local coverage=math.min(h.y+h.h,b.y+b.h)-math.max(h.y,b.y)
     if coverage>best then zone=z best=coverage end
    end
   end
   if zone and not Specials.evading(target,zone) then
    local blocked,parry,defense,reason=defended(target,zone)
    local targetBox=zoneBox(target,zone)
    events[#events+1]={player=i,technique=act.id,zone=zone,distance=math.abs(p.x-target.x),
     blocked=blocked,parry=parry,defense=defense,defenseReason=reason,counter=act.counter,tick=Scene.tick,airborne=p.air,
     height=p.height,link=act.link,damage=t.damage,wasStunned=target.stun>0,
     overlap=math.min(h.x+h.w,targetBox.x+targetBox.w)-math.max(h.x,targetBox.x),
     contactX=(math.max(h.x,targetBox.x)+math.min(h.x+h.w,targetBox.x+targetBox.w))/2,
     contactY=(math.max(h.y,targetBox.y)+math.min(h.y+h.h,targetBox.y+targetBox.h))/2,quality='arcade'}
   end
  end
 end
 for _,e in ipairs(events) do
  local p,target=Scene.players[e.player],Scene.players[3-e.player]
  local t=skills.techniques[e.technique]
  if p.action then p.action.spent=true p.action.age=t.windup+t.active end
  p.contacts=p.contacts+1
  if e.blocked then
   target.blocks=target.blocks+1 target.blockstun=rules.blockstun target.knockVX=p.face*.65
   p.comboHits=0 p.comboTicks=0
   if e.parry then target.parries=target.parries+1 target.counter=16 end
   Scene.message=e.parry and 'DEFESA NO TEMPO / RESPONDA COM SOCO' or string.upper(e.defense)..' COBRE '..string.upper(e.zone)
  else
   p.points=p.points+1 p.comboHits=e.wasStunned and p.comboHits+1 or 1 p.comboTicks=45
   e.comboHits=p.comboHits
   if target.special and target.special.id=='nidan' then target.height=0 end
   target.action=nil target.special=nil target.specialPose=nil target.chain=0 target.chainTime=0 target.guard=false target.low=false
   target.blockstun=0 target.stun=rules.hitstun target.reaction=e.zone=='jodan' and 86 or 85
   target.pose=target.air and 63 or target.reaction target.phase='IMPACTO'
   target.knockVX=p.face*1.6
   if not Scene.practice and not Scene.demo then target.energy=math.max(0,target.energy-e.damage) end
   if target.x==rules.stage_max or target.x==rules.stage_min then p.knockVX=-p.face*.6 end
   Scene.message=t.label..' / '..string.upper(e.zone)..' / '..string.upper(e.defenseReason)
  end
  Scene.messageTicks=55 Scene.flash=e.blocked and 4 or 6
  Scene.freeze=math.max(Scene.freeze,e.blocked and rules.blockstop or rules.hitstop)
  Scene.impact={x=e.contactX,y=e.contactY,blocked=e.blocked}
  Scene.lastContact=e
  if Scene.onContact then Scene.onContact(e) end
 end
 Specials.contacts(Scene,defended)
 if Scene.dust then Scene.dust.age=Scene.dust.age+1;if Scene.dust.age>18 then Scene.dust=nil end end
 if Scene.finishEmphasis then Scene.finishEmphasis=Scene.finishEmphasis-1;if Scene.finishEmphasis<=0 then Scene.finishEmphasis=nil end end
 finishRound() previous=input
end
local accumulator=0
function lutro.load()
 local sounds={}
 if lutro.audio and lutro.audio.newSource then
  for _,name in ipairs({'sweep','ground','finish'}) do local ok,source=pcall(lutro.audio.newSource,'assets/special-'..name..'.wav');if ok then sounds[name]=source end end
 end
 Scene.sound=function(name) if sounds[name] and lutro.audio and lutro.audio.play then lutro.audio.play(sounds[name]) end end
 for _,name in ipairs({'dojo','font','shadow'}) do image[name]=g.newImage('assets/'..name..'.png') end
 Characters.prepare()
 for i=32,126 do fontQuad[i]=g.newQuad((i-32)*6,0,6,6,570,6) end
 Scene.reset()
end
function lutro.update(dt)
 accumulator=math.min(accumulator+math.min(dt or 1/60,.1),.1)
 while accumulator>=1/60 do Scene.advance() accumulator=accumulator-1/60 end
end
function lutro.draw()
 color(255,255,255) g.draw(image.dojo,0,0)
 for i,p in ipairs(Scene.players) do
  color(255,255,255)
  if p.knockdown and p.specialPose and p.specialPose.frame>=4 and p.specialPose.frame<=7 then
   g.draw(image.shadow,math.floor(p.x-58),FLOOR-3);g.draw(image.shadow,math.floor(p.x-4),FLOOR-3)
  else g.draw(image.shadow,math.floor(p.x-31),FLOOR-3) end
  box(p.x-13,FLOOR,26,2,i==1 and 84 or 224,i==1 and 176 or 147,i==1 and 209 or 89)
 end
 -- Stable depth order: an attack never makes whole torsos swap layers.
 for _,i in ipairs({3-Scene.left,Scene.left}) do
  local p=Scene.players[i]
  color(255,255,255)
  Characters.draw(p,math.floor(p.x-W/2),math.floor(FLOOR-H-p.height))
  local top=FLOOR-H+Characters.bounds(p)[2]-p.height
  box(p.x-8,math.max(43,top-11),16,8,i==1 and 37 or 111,i==1 and 94 or 67,i==1 and 124 or 44)
  text(i==2 and Scene.mode=='cpu' and not Scene.demo and 'C' or 'P'..i,p.x-6,math.max(44,top-10))
  if Scene.debug then
   box(p.x-rules.push_distance/2,80-p.height,rules.push_distance,115,90,190,220,true)
   for _,zone in ipairs({'jodan','chudan','gedan'}) do
    local b=zoneBox(p,zone);local ready=defended(p,zone)
    box(b.x,b.y,b.w,b.h,ready and 90 or 180,ready and 220 or 170,90,true)
   end
   local h=hit(p) if h then box(h.x,h.y,h.w,h.h,245,140,65,true) end
  end
 end
 if Scene.dust then
  local d=Scene.dust;local spread=5+d.age
  for n=-2,2 do box(d.x+n*spread/2,192-math.abs(n)*(18-d.age)/5,3,2,188,166,119) end
 end
 if Scene.finishEmphasis then box(1,40,382,157,193,157,98,true) end
 if Scene.flash>0 and Scene.impact then
  local e=Scene.impact;local x,y=e.x,e.y
  local r,b,c=e.blocked and 102 or 248,e.blocked and 203 or 207,e.blocked and 226 or 133
  box(x-6,y,12,2,r,b,c) box(x,y-5,2,10,r,b,c)
  box(x-4,y-3,2,2,r,b,c) box(x+4,y+3,2,2,r,b,c)
 end
 box(0,0,384,39,13,23,29) box(0,38,384,1,173,133,78)
 text('DESHI DOJO',162,3)
 centered((Scene.practice or Scene.demo) and 'TREINO' or string.format('%02d',math.ceil(Scene.timer/60)),16)
 for i,p in ipairs(Scene.players) do
  local x=i==1 and 8 or 232
  local cpu=i==2 and Scene.mode=='cpu' and not Scene.demo
  local profile=CPU.profiles[Scene.difficulty]
  local label=p.character.display_name or p.character.name
  text(cpu and 'CPU '..string.sub(label,1,12)..' '..string.upper(Scene.difficulty) or 'P'..i..'  '..label,x,5)
  local belt=Characters.data.belts[p.character.belt]
  box(x+130,4,13,7,belt[1],belt[2],belt[3]);box(x+130,4,13,7,210,210,201,true)
  box(x,16,144,8,49,57,57)
  local width=math.floor(142*p.energy/rules.energy)
  local rgb=cpu and (Scene.difficulty=='hard' and {175,183,190} or profile.color) or i==1 and {84,176,209} or {224,147,89}
  box(i==1 and x+1 or x+143-width,17,width,6,rgb[1],rgb[2],rgb[3])
  for n=1,2 do box(x+(n-1)*7,28,5,4,Scene.wins[i]>=n and 220 or 70,Scene.wins[i]>=n and 180 or 78,Scene.wins[i]>=n and 100 or 76) end
  local label=p.action and skills.techniques[p.action.id].label or p.phase
  text(label,x+19,28)
  if p.comboHits>1 and p.comboTicks>0 then text(p.comboHits..' COMBO',i==1 and 8 or 330,43) end
 end
 box(0,199,384,25,13,23,29)
 text('P1 '..Scene.players[1].phase,8,202) text('P2 '..Scene.players[2].phase,232,202)
 centered(Scene.messageTicks>0 and Scene.message or 'SOCO > SOCO > CHUTE / DEFESA PARA RECEBER',214)
 if Scene.result then
  box(72,94,240,34,13,23,29)
  local winner=Scene.matchWinner==2 and Scene.mode=='cpu' and 'CPU' or 'P'..(Scene.matchWinner or 0)
  centered(Scene.matchWinner and winner..' VENCEU A PARTIDA' or Scene.message,103)
  centered(Scene.matchWinner and 'START / ENTER: REVANCHE' or 'PROXIMO ROUND',116)
 end
 if Scene.intro then
  local intro=Scene.intro;local digit=math.ceil((intro.total-intro.age)/60)
  local segments={{0,0,1,0,0,1,0},{1,0,1,1,1,0,1},{1,0,1,1,0,1,1},{0,1,1,1,0,1,0},{1,1,0,1,0,1,1}}
  local rects={{0,0,18,3},{0,0,3,22},{15,0,3,22},{0,20,18,3},{0,22,3,22},{15,22,3,22},{0,42,18,3}}
  box(174,49,36,54,13,23,29);box(174,49,36,54,185,151,94,true)
  for i,on in ipairs(segments[digit]) do local r=rects[i];if on==1 then box(183+r[1],54+r[2],r[3],r[4],245,208,128) end end
  centered('ROUND '..Scene.round,43);centered(intro.label,109)
  box(152,120,80,2,60,71,71);box(152,120,80*(intro.total-intro.age)/intro.total,2,185,151,94)
 end
 if Scene.menu then
  Characters.portrait(1,28,3) Characters.portrait(2,324,3)
  box(28,45,328,174,13,23,29) box(28,45,328,174,185,151,94,true)
  centered('MODO E PERSONAGENS',53)
  for i,option in ipairs(menuOptions) do
   if Scene.menuChoice==i then box(40,66+(i-1)*13,304,12,60,71,71) end
   local rgb=option.mode=='cpu' and CPU.profiles[option.level].color or {84,176,209}
   box(46,68+(i-1)*13,8,7,rgb[1],rgb[2],rgb[3]);box(46,68+(i-1)*13,8,7,210,210,201,true)
   local d=option.port and Characters.definition(option.port)
   local value=d and (option.field=='student' and (d.display_name or d.name) or d[option.field]) or ''
  if d and option.field=='student' and d.display_nickname and d.display_nickname~='' then value=value..' / '..d.display_nickname end
   text(option.label..' '..string.upper(value),64,69+(i-1)*13)
  end
  centered('DIRECOES: ESCOLHER / SOCO: ALTERAR',203)
  centered('DEFESA: VOLTAR / SELECT: MENU',213)
 end

end
