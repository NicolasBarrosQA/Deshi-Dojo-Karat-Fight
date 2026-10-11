-- Lua 5.1 / historical Lutro: two ports, three physical action buttons.
-- Real technique vocabulary; jump physics/link timing are arcade adaptations.
local g=lutro.graphics
local skills=require('techniques')
local art=require('art')
local image,quad,fontQuad={},{},{}
Scene={tick=0,freeze=0,flash=0,debug=false,demo=false,lesson='age',players={}}
local W,H,FLOOR=224,144,195
local previous={{},{}}
local keys={'up','down','left','right','b','y','a','select','start'}
local indices={up=5,down=6,left=7,right=8,b=1,y=2,a=9,select=3,start=4}
local function clamp(v,a,b) return math.max(a,math.min(b,v)) end
local function color(r,b,c) g.setColor(r,b,c,255) end
local function box(x,y,w,h,r,b,c,outline)
 color(r,b,c) g.rectangle(outline and 'line' or 'fill',math.floor(x),math.floor(y),w,h)
end
local function text(s,x,y)
 color(255,255,255)
 for i=1,#s do local q=fontQuad[string.byte(s,i)] if q then g.draw(image.font,q,x+(i-1)*6,y) end end
end
local function centered(s,y) text(s,math.floor((384-#s*6)/2),y) end
function Scene.reset()
 Scene.tick=0 Scene.freeze=0 Scene.flash=0 Scene.message='DISTANCIA, TEMPO E CONTROLE' Scene.messageTicks=0 Scene.lastContact=nil
 Scene.players={}
 for i=1,2 do Scene.players[i]={x=i==1 and 104 or 280,face=i==1 and 1 or -1,pose=1,walk=0,age=0,
  action=nil,stun=0,points=0,contacts=0,blocks=0,parries=0,counter=0,phase='KAMAE',
  air=false,height=0,vy=0,jumpAge=0,jumpVX=0,landing=0,low=false,
  chain=0,chainTime=0,lastTechnique=nil,queued=nil,jumps=0,maxChain=0,executed=0} end
 previous={{},{}}
end
local function modifier(input,face)
 if input.up~=input.down then return input.up and 'up' or 'down' end
 if input.left~=input.right then return (input.right and 1 or -1)==face and 'forward' or 'back' end
 return 'neutral'
end
local function horizontal(input,face)
 if input.left==input.right then return 0 end
 return (input.right and 1 or -1)==face and 1 or -1
end
local function choose(kind,input,p)
 local m=modifier(input,p.face)
 if kind=='defense' then return ({up='age',down='gedan',forward='soto',back='uchi',neutral='kamae'})[m] end
 if p.air then return kind=='punch' and 'air_tsuki' or horizontal(input,p.face)==1 and 'air_mawashi' or 'tobi_mae' end
 if kind=='punch' then return ({up='jodan',forward='oi',back='kizami'})[m] or 'gyaku' end
 if input.down and not input.up and horizontal(input,p.face)==-1 then return 'ushiro' end
 return ({down='mae_low',forward='mawashi',back='yoko',up='mawashi_high'})[m] or 'mae'
end
local function links(from,to)
 for _,id in ipairs(skills.links[from] or {}) do if id==to then return true end end
 return false
end
local function startAction(p,id)
 local t=skills.techniques[id]
 if t.kind=='attack' then
  local linked=not p.air and p.chainTime>0 and p.chain<skills.combo.max_links and links(p.lastTechnique,id)
  p.chain=linked and p.chain+1 or 1
  p.chainTime=skills.combo.idle_ticks p.lastTechnique=id p.executed=p.executed+1
  p.maxChain=math.max(p.maxChain,p.chain)
 else p.chain=0 p.chainTime=0 p.lastTechnique=nil end
 p.action={id=id,age=1,spent=false,counter=p.counter>0,releasing=false,link=p.chain}
 p.counter=0 p.age=1 p.pose=t.poses[1] p.low=false p.queued=nil
end
local function total(t)
 local n=0 for _,v in ipairs(t.durations) do n=n+v end return n
end
local function poseAt(t,age)
 local n=0
 for i,d in ipairs(t.durations) do n=n+d if age<=n then return t.poses[i],i end end
 return t.poses[#t.poses],#t.poses
end
local function phaseAt(t,a)
 if a.releasing then return 'RETORNO' end
 if a.age<=t.windup then return 'PREPARA' end
 if t.kind=='defense' then return a.age<=t.windup+3 and 'RECEBE' or 'COBERTURA' end
 return a.age<=t.windup+t.active and 'CONTATO' or 'RECOLHE'
end
local function zoneBox(p,zone)
 local zones={jodan={65,28},chudan={93,43},gedan={137,37}}
 local z=zones[zone];local compact=p.air or p.low
 local shift=compact and (zone=='jodan' and 25 or zone=='chudan' and 12 or 0) or 0
 return {x=p.x-14,y=z[1]+shift-p.height,w=28,h=z[2]-(compact and (zone=='chudan' and 12 or zone=='jodan' and 13 or 0) or 0)}
end
local function hit(p)
 local a=p.action if not a then return nil end
 local t=skills.techniques[a.id]
 if t.kind~='attack' or a.age<=t.windup or a.age>t.windup+t.active then return nil end
 local h=t.hit
 return {x=p.face==1 and p.x+h.near or p.x-h.far,y=h.y-p.height,w=h.far-h.near,h=h.h}
end
local function overlap(a,b)
 return a.x<b.x+b.w and a.x+a.w>b.x and a.y<b.y+b.h and a.y+a.h>b.y
end
local function defended(target,zone)
 local a=target.action
 if not a or a.releasing or target.stun>0 or target.air then return false,false end
 local t=skills.techniques[a.id]
 local ready=t.kind=='defense' and t.zone==zone and a.age>t.windup
 return ready,ready and a.age<=t.windup+3 and a.id~='kamae'
end
local function jump(p,input)
 p.air=true p.height=0 p.vy=0 p.jumpAge=0 p.jumpVX=horizontal(input,p.face)*p.face*1.5
 p.pose=61 p.jumps=p.jumps+1 p.chain=0 p.chainTime=0 p.queued=nil p.low=false p.airPending=nil p.airUsed=false
end
local function flight(p)
 if not p.air then return end
 p.jumpAge=p.jumpAge+1
 if p.jumpAge==4 then p.vy=4.6 end
 if p.jumpAge>=4 then
  p.height=p.height+p.vy p.vy=p.vy-.28 p.x=clamp(p.x+p.jumpVX,72,312)
  if p.height<=0 then
   p.height=0 p.vy=0 p.air=false p.landing=5 p.action=nil p.queued=nil p.airPending=nil
   p.pose=64 p.phase='POUSAR' p.chain=0 p.chainTime=0
  end
 end
end
local function lessonInput(i)
 local id=Scene.lesson or 'age';local t=skills.techniques[id] or skills.techniques.age
 local n=Scene.tick%180
 if n==1 then Scene.players[1].x=150 Scene.players[2].x=217 end
 local input={}
 if t.kind=='defense' then
  if i==1 and n>=20 and n<=78 then
   input.y=true
   if id=='age' then input.up=true elseif id=='gedan' then input.down=true elseif id=='soto' then input.right=true elseif id=='uchi' then input.left=true end
  end
  if i==2 and n==31 then
   if t.zone=='gedan' then input.a=true input.down=true else input.b=true input.up=t.zone=='jodan' end
  end
 elseif i==1 then
  if t.air and n==20 then input.up=true end
  if n==30 then
   input[t.button=='punch' and 'b' or 'a']=true
   if t.direction=='up' then input.up=true elseif t.direction=='down' then input.down=true
   elseif t.direction=='forward' then input.right=true elseif t.direction=='back' then input.left=true
   elseif t.direction=='down_back' then input.down=true input.left=true end
  end
 end
 return input
end
function Scene.advance()
 Scene.tick=Scene.tick+1
 local input={}
 for i=1,2 do
  input[i]={} for _,k in ipairs(keys) do input[i][k]=lutro.joystick.isDown(i,indices[k]) end
 end
 for i=1,2 do
  if input[i].start and not previous[i].start then Scene.reset() previous=input return end
  if input[i].select and not previous[i].select then Scene.debug=not Scene.debug end
  if Scene.demo then input[i]=lessonInput(i) end
 end
 if Scene.flash>0 then Scene.flash=Scene.flash-1 end
 if Scene.messageTicks>0 then Scene.messageTicks=Scene.messageTicks-1 end
 -- Buffer fresh physical presses even during contact freeze; holding never repeats.
 for i,p in ipairs(Scene.players) do
  local c=input[i];local punch=c.b and not previous[i].b;local kick=c.a and not previous[i].a
  if (punch or kick) and not c.y and p.action and skills.techniques[p.action.id].kind=='attack' then
   local a=p.action;local t=skills.techniques[a.id];local id=choose(punch and 'punch' or 'kick',c,p)
   if not p.air and a.age>t.windup+t.active and total(t)-a.age<skills.combo.buffer_ticks
      and p.chain<skills.combo.max_links and links(a.id,id) then p.queued={id=id,ttl=skills.combo.buffer_ticks} end
  end
 end
 if Scene.freeze>0 then Scene.freeze=Scene.freeze-1 previous=input return end
 for i,p in ipairs(Scene.players) do
  local other=Scene.players[3-i];local control=input[i]
  if not p.action and not p.air then p.face=p.x<other.x and 1 or -1 end
  p.counter=math.max(0,p.counter-1)
  if p.queued then p.queued.ttl=p.queued.ttl-1 if p.queued.ttl<0 then p.queued=nil end end
  if not p.action then p.chainTime=math.max(0,p.chainTime-1) end
  local punch=control.b and not previous[i].b;local kick=control.a and not previous[i].a
  -- Guard can replace takeoff while the feet are still grounded. This lets a
  -- stick+guard chord settle without accidentally launching an aerial block.
  if p.air and p.height==0 and p.jumpAge<4 and control.y then
   p.air=false p.jumpAge=0 p.jumpVX=0 p.airPending=nil p.jumps=p.jumps-1
   startAction(p,choose('defense',control,p))
  end
  flight(p)
  if p.stun>0 then p.stun=p.stun-1 p.pose=p.air and 63 or 12 p.phase='RECOMPOR'
  elseif p.landing>0 then p.landing=p.landing-1 p.pose=64 p.phase='POUSAR'
  elseif p.action then
   local a=p.action;local t=skills.techniques[a.id]
   if t.kind=='defense' and not a.releasing then
    if not control.y then
     if (punch or kick) and p.counter>0 then startAction(p,choose(punch and 'punch' or 'kick',control,p))
     else a.releasing=true a.release=0 end
    elseif a.age>t.windup+t.active and choose('defense',control,p)~=a.id then startAction(p,choose('defense',control,p)) end
   end
   a=p.action;t=skills.techniques[a.id]
   if a.releasing then
    a.release=a.release+1 p.pose=12 p.phase='RETORNO'
    if a.release>=5 then p.action=nil end
   else
    if t.kind=='attack' and (t.step or 0)>0 and a.age<t.windup then p.x=clamp(p.x+p.face*t.step/(t.windup-1),72,312) end
    a.age=a.age+1 p.age=a.age p.pose=poseAt(t,a.age) p.phase=phaseAt(t,a)
    if t.kind=='attack' and a.age>total(t) then
     local queued=p.queued p.action=nil p.queued=nil p.pose=p.air and 63 or 12 p.phase=p.air and 'SALTO' or 'KAMAE'
     if queued and not control.y and not p.air then startAction(p,queued.id) end
    end
   end
  elseif p.air then
   if (punch or kick) and not p.airUsed then p.airPending=choose(punch and 'punch' or 'kick',control,p) end
   if p.airPending and p.jumpAge>=4 then
    local id=p.airPending p.airPending=nil p.airUsed=true startAction(p,id) p.phase='PREPARA'
   else p.pose=p.jumpAge<4 and 61 or p.vy>1 and 62 or 63 p.phase='SALTO' end
  elseif control.y then startAction(p,choose('defense',control,p)) p.phase='PREPARA'
  elseif punch or kick then startAction(p,choose(punch and 'punch' or 'kick',control,p)) p.phase='PREPARA'
  elseif control.up and not control.down and not previous[i].up then jump(p,control) p.phase='IMPULSAO'
  elseif control.down and not control.up then p.low=true p.pose=61 p.phase='BASE BAIXA'
  elseif control.left~=control.right then
   p.low=false local dir=control.right and 1 or -1
   p.x=clamp(p.x+dir*(dir==p.face and 1.2 or .9),72,312)
   p.walk=p.walk+1 p.pose=({1,3,4,5})[1+math.floor(p.walk/6)%4] p.phase='DESLOCAR'
  else p.low=false p.walk=0 p.pose=({1,2,12,2})[1+math.floor(Scene.tick/18)%4] p.phase='KAMAE' end
  p.guard=p.action and skills.techniques[p.action.id].kind=='defense' and not p.action.releasing or false
 end
 local a,b=Scene.players[1],Scene.players[2]
 if math.abs(b.x-a.x)<58 then
  local middle=clamp((a.x+b.x)/2,101,283)
  if a.x<b.x then a.x=middle-29 b.x=middle+29 else a.x=middle+29 b.x=middle-29 end
 end
 -- Snapshot both contacts and defences before stun, preserving simultaneous trades.
 local events={}
 for i,p in ipairs(Scene.players) do
  local h=hit(p);local act=p.action
  if h and not act.spent then
   local t=skills.techniques[act.id];local target=Scene.players[3-i]
   -- Airborne trajectories are judged at their actual height, not a fixed label.
   local zone=nil;local best=0;local candidates={t.zone,'jodan','chudan','gedan'}
   for _,z in ipairs(candidates) do
    local b=zoneBox(target,z)
    if overlap(h,b) then
     local coverage=math.min(h.y+h.h,b.y+b.h)-math.max(h.y,b.y)
     if coverage>best then zone=z best=coverage end
    end
   end
   if zone then
    local blocked,parry=defended(target,zone);local hurt=zoneBox(target,zone)
    events[#events+1]={player=i,technique=act.id,zone=zone,distance=math.abs(p.x-target.x),
     blocked=blocked,parry=parry,counter=act.counter,tick=Scene.tick,airborne=p.air,
     height=p.height,link=act.link,overlap=math.min(h.x+h.w,hurt.x+hurt.w)-math.max(h.x,hurt.x),quality='prototype'}
   end
  end
 end
 for _,e in ipairs(events) do
  local p,target=Scene.players[e.player],Scene.players[3-e.player]
  if p.action then p.action.spent=true end
  p.contacts=p.contacts+1
  if e.blocked then
   target.blocks=target.blocks+1
   if e.parry then target.parries=target.parries+1 target.counter=18 end
   Scene.message=e.parry and 'RECEBEU NO TEMPO / CONTRA-ATAQUE' or 'DEFESA / '..string.upper(e.zone)
  else
   p.points=p.points+1 target.action=nil target.queued=nil target.chain=0 target.chainTime=0 target.guard=false target.low=false target.stun=10
   Scene.message=skills.techniques[e.technique].label..' / '..string.upper(e.zone)
  end
  Scene.messageTicks=75 Scene.flash=e.blocked and 4 or 6 Scene.freeze=e.blocked and 2 or 4
  Scene.impactX=target.x-target.face*12 Scene.impactY=skills.techniques[e.technique].hit.y-e.height+5
  Scene.lastContact=e
 end
 previous=input
end
local accumulator=0
function lutro.load()
 for _,name in ipairs({'dojo','fighter-right','fighter-left','font','shadow'}) do image[name]=g.newImage('assets/'..name..'.png') end
 for i=1,art.frames do quad[i]=g.newQuad(((i-1)%4)*W,math.floor((i-1)/4)*H,W,H,art.width,art.height) end
 for i=32,126 do fontQuad[i]=g.newQuad((i-32)*6,0,6,6,570,6) end
 Scene.reset()
end
function lutro.update(dt)
 accumulator=math.min(accumulator+math.min(dt or 1/60,.1),.1)
 while accumulator>=1/60 do Scene.advance() accumulator=accumulator-1/60 end
end
function lutro.draw()
 color(255,255,255) g.draw(image.dojo,0,0)
 for _,p in ipairs(Scene.players) do color(255,255,255) g.draw(image.shadow,math.floor(p.x-31),FLOOR-3) end
 local ordered=Scene.players;local first=Scene.players[1]
 if first.action and skills.techniques[first.action.id].kind=='attack' then ordered={Scene.players[2],first} end
 for _,p in ipairs(ordered) do
  color(255,255,255) g.draw(image[p.face==1 and 'fighter-right' or 'fighter-left'],quad[p.pose],math.floor(p.x-W/2),math.floor(FLOOR-H-p.height))
  if Scene.debug then
   for _,zone in ipairs({'jodan','chudan','gedan'}) do
    local h=zoneBox(p,zone);local ready=defended(p,zone)
    box(h.x,h.y,h.w,h.h,ready and 90 or 155,ready and 220 or 165,90,true)
   end
   local h=hit(p) if h then box(h.x,h.y,h.w,h.h,245,140,65,true) end
  end
 end
 if Scene.flash>0 then local x,y=Scene.impactX,Scene.impactY box(x-5,y,10,1,240,215,155) box(x,y-4,1,9,240,215,155) end
 -- HUD drawn after sprites: jumping never overwrites scores.
 box(0,0,384,38,16,27,31) box(0,37,384,1,173,133,78)
 centered('DESHI DOJO / SHOTOKAN',6)
 for i,p in ipairs(Scene.players) do
  local x=i==1 and 9 or 218
  text('P'..i..' ACERTOS '..string.format('%02d',p.points),x,18)
  local label=p.action and skills.techniques[p.action.id].label or p.phase
  text(label,x,29)
  if p.chain>1 and (p.action or p.chainTime>0) then text('RENZOKU '..p.chain,x,41) end
 end
 box(0,198,384,26,16,27,31)
 for i,p in ipairs(Scene.players) do text(p.phase,i==1 and 9 or 276,201) end
 centered(Scene.messageTicks>0 and Scene.message or 'DISTANCIA, TEMPO E CONTROLE',214)
end
