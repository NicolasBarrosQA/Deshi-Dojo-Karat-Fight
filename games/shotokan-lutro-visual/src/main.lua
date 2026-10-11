-- Lua 5.1 / historical Lutro. Three actions and opponent-relative modifiers.
-- Combat emits technique/zone/distance/timing events; no health/damage model.
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
  action=nil,stun=0,points=0,contacts=0,blocks=0,parries=0,counter=0,phase='KAMAE'} end
 previous={{},{}}
end
local function modifier(input,face)
 if input.up~=input.down then return input.up and 'up' or 'down' end
 if input.left~=input.right then return (input.right and 1 or -1)==face and 'forward' or 'back' end
 return 'neutral'
end
local function choose(kind,input,p)
 local m=modifier(input,p.face)
 if kind=='defense' then return ({up='age',down='gedan',forward='soto',back='uchi',neutral='kamae'})[m] end
 if kind=='punch' then return m=='up' and 'jodan' or m=='forward' and 'oi' or 'gyaku' end
 return m=='down' and 'mae_low' or m=='forward' and 'mawashi' or 'mae'
end
local function startAction(p,id)
 p.action={id=id,age=1,spent=false,counter=p.counter>0,releasing=false}
 p.counter=0 p.age=1 p.pose=skills.techniques[id].poses[1]
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
 local z=zones[zone]
 return {x=p.x-14,y=z[1],w=28,h=z[2]}
end
local function hit(p)
 local a=p.action if not a then return nil end
 local t=skills.techniques[a.id]
 if t.kind~='attack' or a.age<=t.windup or a.age>t.windup+t.active then return nil end
 local h=t.hit
 return {x=p.face==1 and p.x+h.near or p.x-h.far,y=h.y,w=h.far-h.near,h=h.h}
end
local function overlap(a,b)
 return a.x<b.x+b.w and a.x+a.w>b.x and a.y<b.y+b.h and a.y+a.h>b.y
end
local function defended(target,zone)
 local a=target.action
 if not a or a.releasing or target.stun>0 then return false,false end
 local t=skills.techniques[a.id]
 local ready=t.kind=='defense' and t.zone==zone and a.age>t.windup
 return ready,ready and a.age<=t.windup+3 and a.id~='kamae'
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
 elseif i==1 and n==30 then
  input.b=id=='gyaku' or id=='oi' or id=='jodan'
  input.a=not input.b input.up=id=='jodan' input.down=id=='mae_low' input.right=id=='oi' or id=='mawashi'
 end
 return input
end
function Scene.advance()
 Scene.tick=Scene.tick+1
 local input={}
 for i=1,2 do
  input[i]={} for _,k in ipairs(keys) do input[i][k]=lutro.joystick.isDown(i,indices[k]) end
  if input[i].start and not previous[i].start then Scene.reset() return end
  if input[i].select and not previous[i].select then Scene.debug=not Scene.debug end
  if Scene.demo then input[i]=lessonInput(i) end
 end
 if Scene.flash>0 then Scene.flash=Scene.flash-1 end
 if Scene.messageTicks>0 then Scene.messageTicks=Scene.messageTicks-1 end
 if Scene.freeze>0 then Scene.freeze=Scene.freeze-1 previous=input return end
 for i,p in ipairs(Scene.players) do
  local other=Scene.players[3-i];local control=input[i]
  if not p.action then p.face=p.x<other.x and 1 or -1 end
  p.counter=math.max(0,p.counter-1)
  local punch=control.b and not previous[i].b
  local kick=control.a and not previous[i].a
  if p.stun>0 then p.stun=p.stun-1 p.pose=12 p.phase='RECOMPOR'
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
    if t.kind=='attack' and a.age>total(t) then p.action=nil p.pose=12 p.phase='KAMAE' end
   end
  elseif control.y then startAction(p,choose('defense',control,p)) p.phase='PREPARA'
  elseif punch or kick then startAction(p,choose(punch and 'punch' or 'kick',control,p)) p.phase='PREPARA'
  elseif control.left~=control.right then
   local dir=control.right and 1 or -1
   p.x=clamp(p.x+dir*(dir==p.face and 1.2 or .9),72,312)
   p.walk=p.walk+1 p.pose=({1,3,4,5})[1+math.floor(p.walk/6)%4] p.phase='DESLOCAR'
  else p.walk=0 p.pose=({1,2,12,2})[1+math.floor(Scene.tick/18)%4] p.phase='KAMAE' end
  p.guard=p.action and skills.techniques[p.action.id].kind=='defense' and not p.action.releasing or false
 end
 local a,b=Scene.players[1],Scene.players[2]
 if math.abs(b.x-a.x)<58 then
  local middle=clamp((a.x+b.x)/2,101,283)
  if a.x<b.x then a.x=middle-29 b.x=middle+29 else a.x=middle+29 b.x=middle-29 end
 end
 -- Snapshot both contacts/defences before applying stun: trades are simultaneous.
 local events={}
 for i,p in ipairs(Scene.players) do
  local h=hit(p);local act=p.action
  if h and not act.spent then
   local t=skills.techniques[act.id];local target=Scene.players[3-i]
   if overlap(h,zoneBox(target,t.zone)) then
    local blocked,parry=defended(target,t.zone)
    local hurt=zoneBox(target,t.zone)
    events[#events+1]={player=i,technique=act.id,zone=t.zone,distance=math.abs(p.x-target.x),
     blocked=blocked,parry=parry,counter=act.counter,tick=Scene.tick,
     overlap=math.min(h.x+h.w,hurt.x+hurt.w)-math.max(h.x,hurt.x),quality='prototype'}
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
   p.points=p.points+1 target.action=nil target.guard=false target.stun=10
   Scene.message=skills.techniques[e.technique].label..' / '..string.upper(e.zone)
  end
  Scene.messageTicks=75 Scene.flash=e.blocked and 4 or 6 Scene.freeze=e.blocked and 2 or 4
  Scene.impactX=target.x-target.face*12 Scene.impactY=skills.techniques[e.technique].hit.y+5
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
 box(0,0,384,38,16,27,31) box(0,37,384,1,173,133,78)
 centered('DESHI DOJO / SHOTOKAN',6)
 for i,p in ipairs(Scene.players) do
  local x=i==1 and 9 or 218
  text('P'..i..' ACERTOS '..string.format('%02d',p.points),x,18)
  local label=p.action and skills.techniques[p.action.id].label or p.phase
  text(label,x,29)
 end
 for _,p in ipairs(Scene.players) do color(255,255,255) g.draw(image.shadow,math.floor(p.x-31),FLOOR-3) end
 local ordered=Scene.players
 local first=Scene.players[1]
 if first.action and skills.techniques[first.action.id].kind=='attack' then ordered={Scene.players[2],first} end
 for _,p in ipairs(ordered) do
  color(255,255,255) g.draw(image[p.face==1 and 'fighter-right' or 'fighter-left'],quad[p.pose],math.floor(p.x-W/2),FLOOR-H)
  if Scene.debug then
   for _,zone in ipairs({'jodan','chudan','gedan'}) do
    local h=zoneBox(p,zone);local ready=defended(p,zone)
    box(h.x,h.y,h.w,h.h,ready and 90 or 155,ready and 220 or 165,90,true)
   end
   local h=hit(p) if h then box(h.x,h.y,h.w,h.h,245,140,65,true) end
  end
 end
 if Scene.flash>0 then local x,y=Scene.impactX,Scene.impactY box(x-5,y,10,1,240,215,155) box(x,y-4,1,9,240,215,155) end
 box(0,198,384,26,16,27,31)
 for i,p in ipairs(Scene.players) do text(p.phase,i==1 and 9 or 300,201) end
 centered(Scene.messageTicks>0 and Scene.message or 'DISTANCIA, TEMPO E CONTROLE',214)
end
