-- title: Deshi Dojo Karate Fight - Shotokan Arcade
-- author: Deshi Dojo contributors
-- script: lua
-- license: MIT
-- Original raster sprite art, single palette and 2019 TIC-80 APIs.
G={mode="title",frame=0,selections={1,2},ready={false,false},hold=0,
   target=5,duration=3600,clock=3600,pause=0,freeze=0,event=nil,
   result=nil,intro=0,resultLock=0,inputs={{held={},previous={}},{held={},previous={}}}}
G.characters={{id="ren",name="REN",style="AVANCO",color=12,belt="VERMELHA"},
              {id="aki",name="AKI",style="DISTANCIA",color=13,belt="AZUL"}}
local FLOOR=122
G.moves={
 {name="OI-ZUKI",prep="oi0",mid="oiM",pose="oi1",retract="oiR",start=9,active=5,recovery=17,advance=4,points=1,box={x=14,y=21,w=19,h=9}},
 {name="GYAKU-ZUKI",prep="gyaku0",mid="gyakuM",pose="gyaku1",retract="gyakuR",start=7,active=4,recovery=18,advance=0,points=1,box={x=12,y=25,w=19,h=8}},
 {name="MAE-GERI",prep="mae0",mid="maeM",pose="mae1",retract="maeR",start=13,active=5,recovery=23,advance=0,points=2,box={x=23,y=36,w=18,h=9}},
 {name="MAWASHI-GERI",prep="mawashi0",mid="mawashiM",pose="mawashi1",retract="mawashiR",start=16,active=6,recovery=25,advance=0,points=2,box={x=23,y=25,w=19,h=12}}
}
G.audio={{18,3,4},{30,5,8},{24,7,8},{43,5,9},{20,8,12},{48,12,9},{48,24,10}}
function G.sound(id,channel)
 local a=G.audio[id+1] sfx(id,a[1],a[2],channel or 2,a[3],0)
end
local function clamp(x,a,b) return math.max(a,math.min(b,x)) end
local function readInputs()
 for i,c in ipairs(G.inputs) do
  for b=0,7 do c.previous[b]=c.held[b] or false c.held[b]=btn((i-1)*8+b) end
 end
end
local function down(i,b) return G.inputs[i].held[b] end
local function edge(i,b) return down(i,b) and not G.inputs[i].previous[b] end
local function player(i)
 return {id=i,character=G.selections[i],x=i==1 and 58 or 182,face=i==1 and 1 or -1,
         score=0,attack=nil,tick=0,spent=false,guard=false,stun=0,walking=false,pose="idle0",walkTick=0,buffer=nil,block=0}
end
function G.startFight()
 G.p={player(1),player(2)} G.clock=G.duration G.pause=0 G.freeze=0 G.event=nil G.result=nil G.mode="fight"
 G.hold=0 G.intro=36 G.resultLock=0
end
G.p={player(1),player(2)}
function G.select() G.mode="select" G.ready={false,false} G.event=nil end
function G.diagnostic() G.mode="diagnostic" G.p={player(1),player(2)} G.hold=0 end
local function intersects(a,b)
 return a.x<b.x+b.w and b.x<a.x+a.w and a.y<b.y+b.h and b.y<a.y+a.h
end
function G.hurt(p)
 local b=HURT[G.characters[p.character].id][p.pose]
 return {x=p.face==1 and p.x+b.x or p.x-b.x-b.w,y=FLOOR-64+b.y,w=b.w,h=b.h}
end
function G.attackPose(p)
 local m,t=p.attack,p.tick
 if t<m.start then return t<math.floor(m.start*.55) and m.prep or m.mid end
 if t<m.start+m.active then return m.pose end
 return t<m.start+m.active+math.ceil(m.recovery*.6) and m.retract or "recover"
end
function G.hit(p)
 if not p.attack or p.spent or p.tick<p.attack.start or p.tick>=p.attack.start+p.attack.active then return nil end
 local b=p.attack.box
 return {x=p.face==1 and p.x+b.x or p.x-b.x-b.w,y=FLOOR-64+b.y,w=b.w,h=b.h}
end
-- Replaceable rules: no life bar and no claim of official Shotokan refereeing.
function G.judge(e,move)
 if e.result~="contact" or e.quality<40 then return 0 end
 return move.points
end
local function contact(a,b)
 local h=G.hit(a)
 if not h or not intersects(h,G.hurt(b)) then return nil end
 local distance=math.abs(a.x-b.x)
 local ideal=a.attack.box.x+a.attack.box.w-2
 local quality=clamp(math.floor(100-math.abs(distance-ideal)*3),0,100)
 local e={source=a.id,target=b.id,technique=a.attack.name,distance=math.floor(distance),
          quality=quality,zone="chudan",result=b.guard and "blocked" or "contact",
          x=a.face==1 and h.x+h.w-2 or h.x+2,y=h.y+h.h/2,frame=G.frame,
          counter=b.attack~=nil and b.tick>=b.attack.start+b.attack.active}
 e.points=G.judge(e,a.attack)
 return e
end
local function bound()
 local a,b=G.p[1],G.p[2]
 a.x=clamp(a.x,20,220) b.x=clamp(b.x,20,220)
 if b.x-a.x<24 then local middle=clamp((a.x+b.x)/2,32,208) a.x=middle-12 b.x=middle+12 end
end
local function finish(reason)
 local a,b=G.p[1].score,G.p[2].score
 G.result={winner=a==b and 0 or (a>b and 1 or 2),reason=reason}
 G.mode="result" G.rematch=1 G.resultLock=24
 for i,p in ipairs(G.p) do
  p.x=i==1 and 58 or 182 p.attack=nil p.stun=0 p.block=0
  p.pose=G.result.winner==0 and "idle0" or (G.result.winner==i and "victory0" or "defeat")
 end
 G.sound(6,3)
end
local function beginAttack(p,index)
 p.attack=G.moves[index] p.tick=0 p.spent=false p.guard=false p.buffer=nil
 p.pose=p.attack.prep
end
local function combat()
 if G.intro>0 then
  G.intro=G.intro-1
  for _,p in ipairs(G.p) do p.pose=({"idle0","idle1","idle2","idle1"})[math.floor(G.frame/12)%4+1] end
  return
 end
 if G.freeze>0 then G.freeze=G.freeze-1 return end
 if G.pause>0 then
  G.pause=G.pause-1
  for i,p in ipairs(G.p) do
   if p.stun>0 then p.stun=p.stun-1 p.pose=p.stun>6 and "react" or "react1"
   elseif p.attack then
    p.tick=p.tick+1
    if p.tick<p.attack.start+p.attack.active+p.attack.recovery then p.pose=G.attackPose(p)
    else p.attack=nil p.pose="idle0" end
   else p.pose="idle1" end
   if G.pause<12 then
    local goal=i==1 and 58 or 182
    p.x=p.x+(goal-p.x)/(G.pause+1)
    p.pose=({"step0","step1","step2","step3"})[math.floor(G.frame/4)%4+1]
   end
  end
  if G.pause==0 then
   for _,p in ipairs(G.p) do
    p.attack=nil p.tick=0 p.stun=0 p.block=0 p.guard=false p.buffer=nil p.pose="idle0"
   end
  end
  return
 end
 G.clock=math.max(0,G.clock-1)
 for i,p in ipairs(G.p) do
  p.walking=false p.guard=false
  if p.buffer and p.buffer.expires<G.frame then p.buffer=nil end
  if p.stun>0 then
   p.stun=p.stun-1 p.attack=nil p.buffer=nil
   p.pose=p.block>0 and (p.stun>2 and "block0" or "block1") or (p.stun>6 and "react" or "react1")
   if p.stun==0 then p.block=0 end
  elseif p.attack then
   p.tick=p.tick+1 local m=p.attack
   -- One fresh input can be buffered only in the last four recovery ticks.
   if p.tick>=m.start+m.active+m.recovery-4 and not (down(i,4) and down(i,5)) then
    for b=4,7 do if edge(i,b) then p.buffer={move=b-3,expires=G.frame+4} break end end
   end
   if p.tick<m.start+m.active+m.recovery then p.pose=G.attackPose(p)
   else p.attack=nil p.pose="idle0" end
   -- Oi-zuki advances during anticipation, not as an instant teleport.
   if p.attack and p.tick<=m.start and m.advance>0 then p.x=p.x+p.face*m.advance/m.start end
  else
   local direction=(down(i,3) and 1 or 0)-(down(i,2) and 1 or 0)
   p.walking=direction~=0 p.guard=direction==-p.face
   if p.walking then p.walkTick=p.walkTick+1 else p.walkTick=0 end
   p.x=p.x+direction*(p.guard and .74 or .9)
   local cycle=math.floor(p.walkTick/4)%4+1
   if p.guard then p.pose=cycle<3 and "guard" or "guard1"
   elseif p.walking then p.pose=({"step0","step1","step2","step3"})[cycle]
   else p.pose=({"idle0","idle1","idle2","idle1"})[math.floor(G.frame/12)%4+1] end
   if p.walking and p.walkTick%12==0 then G.sound(0,i-1) end
   if not (down(i,4) and down(i,5)) then
    if p.buffer then beginAttack(p,p.buffer.move)
    else for b=4,7 do if edge(i,b) then beginAttack(p,b-3) break end end end
   end
  end
  if p.attack and p.tick==p.attack.start then G.sound(p.attack.points==1 and 1 or 2,i-1) end
 end
 bound()
 local a,b=contact(G.p[1],G.p[2]),contact(G.p[2],G.p[1])
 local scored=false
 for _,e in ipairs({a or false,b or false}) do
  if e then
   local attacker,target=G.p[e.source],G.p[e.target]
   attacker.spent=true attacker.score=attacker.score+e.points G.event=e
   target.buffer=nil
   if e.result=="contact" then
    target.stun=12 target.block=0 target.pose="react" target.x=target.x-target.face*2
    G.sound(4,target.id-1) G.freeze=math.max(G.freeze,5)
   else
    target.stun=5 target.block=5 target.pose="block0"
    G.sound(3,target.id-1) G.freeze=math.max(G.freeze,3)
   end
   if e.points>0 then G.pause=42 scored=true end
  end
 end
 if scored then G.sound(5,2) end
 bound()
 if G.p[1].score>=G.target or G.p[2].score>=G.target then finish("PONTUACAO")
 elseif G.clock==0 then finish("TEMPO") end
end
local function background() memcpy(0,0x8000,16320) end
local function text(s,x,y,c,scale)
 return print(s,math.floor(x),math.floor(y),c or 8,true,scale or 1)
end
local function centered(s,y,c,scale)
 scale=scale or 1 text(s,(240-#s*6*scale)/2,y,c,scale)
end
local function sprite(character,pose,x,ground,face)
 local f=face==-1 and 1 or 0
 for _,cell in ipairs(ART[G.characters[character].id][pose]) do
  local sx=face==1 and x-32+cell[1] or x+32-cell[1]-8
  local id=cell[3]
  if id>=480 then memcpy(0x7c00,0xbfc0+(id-480)*32,32) id=480 end
  spr(id,math.floor(sx),ground-64+cell[2],0,1,f,0,1,1)
 end
end
local function shadow(x,radius)
 radius=radius or 13
 for y=0,2 do line(math.floor(x-radius+y*3),FLOOR+y,math.floor(x+radius-y*3),FLOOR+y,3) end
 line(math.floor(x-radius+3),FLOOR+3,math.floor(x+radius-3),FLOOR+3,11)
end
local function fighter(p)
 local kick=p.pose:sub(1,3)=="mae" or p.pose:sub(1,7)=="mawashi"
 shadow(p.x-(kick and 7*p.face or 0),kick and 7 or 13)
 sprite(p.character,p.pose,p.x,FLOOR,p.face)
end
local function hud()
 rect(0,0,240,27,0) line(0,25,239,25,6) line(0,26,239,26,3)
 local first,second=G.characters[G.p[1].character],G.characters[G.p[2].character]
 text("P1 "..first.name,8,3,8)
 rect(8,11,43,2,first.color) rect(24,10,3,4,first.color)
 text("P2 "..second.name,196,3,8)
 rect(190,11,43,2,second.color) rect(215,10,3,4,second.color)
 local seconds=math.ceil(G.clock/60)
 text(string.format("%02d",seconds),108,4,7,2)
 for i,p in ipairs(G.p) do
  for n=1,G.target do
   local x=i==1 and 8+(n-1)*13 or 225-(n-1)*13
   rectb(x,17,8,6,2)
   if p.score>=n then rect(x+1,18,6,4,i==1 and 12 or 13) end
  end
 end
end
local function arena()
 background() hud()
 for _,p in ipairs(G.p) do fighter(p) end
 if G.event and G.frame-G.event.frame<40 then
  local e=G.event
  if G.frame-e.frame<8 then
   local x=math.floor(e.x) local y=math.floor(e.y)
   local radius=G.frame-e.frame<3 and 3 or 5
   local color=e.result=="blocked" and 13 or 7
   line(x-radius,y-1,x+radius,y+1,color)
   line(x-2,y-radius,x+2,y+radius,8)
   if e.result=="contact" then
    line(x-radius,y-radius,x-2,y-2,color) line(x+2,y+2,x+radius,y+radius,color)
   end
  end
  if e.points>0 then
   centered((e.counter and "CONTRA " or "")..e.technique.." +"..e.points,31,7)
  elseif e.result=="blocked" then centered("DEFESA",31,13) end
 end
 rect(0,128,240,8,0) text("KUMITE SHOTOKAN",5,130,9) text("5 PONTOS",187,130,9)
 if G.intro>0 then
  rect(74,42,92,16,0) centered(G.intro>22 and "PRONTOS" or "HAJIME!",46,7)
 end
end
local function title()
 background()
 centered("KUMITE / SHOTOKAN",9,6)
 local breathe=({"idle0","idle1","idle2","idle1"})[math.floor(G.frame/12)%4+1]
 sprite(1,breathe,39,FLOOR,1) sprite(2,breathe,200,FLOOR,-1)
 rect(47,28,146,61,0) rectb(49,30,142,57,6)
 line(49,31,96,31,12) line(144,86,190,86,13)
 centered("DESHI DOJO",38,8,2) centered("KARATE FIGHT",57,7)
 line(72,68,167,68,12) line(76,71,163,71,13)
 centered("SHOTOKAN ARCADE",77,9)
 if math.floor(G.frame/30)%2==0 then centered("A: JOGAR",99,8) end
 centered("B: TESTAR CONTROLES",109,9)
 centered("DOIS JOGADORES / OFFLINE",129,7)
 if edge(1,4) or edge(2,4) then G.select()
 elseif edge(1,5) then G.diagnostic() end
end
local function selectScreen()
 background()
 rect(0,0,240,25,0) centered("ESCOLHA SEU KARATECA",7,7)
 line(7,22,232,22,6) line(120,29,120,124,3)
 for i=1,2 do
  if not G.ready[i] then
   if edge(i,2) or edge(i,3) then G.selections[i]=3-G.selections[i] G.sound(0,i-1) end
   if edge(i,4) then G.ready[i]=true G.sound(5,i-1) end
  elseif edge(i,5) then G.ready[i]=false end
  local x=i==1 and 61 or 179 local who=G.characters[G.selections[i]]
  text("P"..i,x-6,29,i==1 and 12 or 13)
  text(who.name,x-#who.name*3,40,8)
 text(who.belt,x-#who.belt*3,49,who.color)
  shadow(x) sprite(G.selections[i],({"idle0","idle1","idle2","idle1"})[math.floor(G.frame/12)%4+1],x,FLOOR,i==1 and 1 or -1)
  text(G.ready[i] and "PRONTO" or "<  A  >",x-21,129,G.ready[i] and 7 or 8)
 end
 if G.ready[1] and G.ready[2] then G.startFight() end
end
local function diagnostic()
 background() rect(0,0,240,65,0) centered("DIAGNOSTICO DOS CONTROLES",5,7)
 local labels={"U","D","L","R","A","B","X","Y"}
 for i,p in ipairs(G.p) do
  local x=i==1 and 9 or 130
  text("P"..i,x,20,i==1 and 12 or 13)
  for b=0,7 do
   local bx=x+(b%4)*24 local by=32+math.floor(b/4)*13
   rect(bx,by,20,10,down(i,b) and (i==1 and 12 or 13) or 2) text(labels[b+1],bx+7,by+2,8)
  end
  p.x=clamp(p.x+(down(i,3) and 1 or 0)-(down(i,2) and 1 or 0),20,220)
  p.pose=(down(i,2) or down(i,3)) and "step0" or "idle0"
  fighter(p)
 end
 centered("P1 A+B 1s: VOLTAR",129,7)
end
local function results()
 if G.resultLock>0 then G.resultLock=G.resultLock-1 end
 local result=G.result
 for i,p in ipairs(G.p) do
  p.pose=result.winner==0 and "idle0" or (result.winner==i and (math.floor(G.frame/12)%2==0 and "victory0" or "victory1") or "defeat")
 end
 arena()
 rect(0,29,240,27,0) line(0,55,239,55,6)
 local name=result.winner==0 and "EMPATE" or G.characters[G.p[result.winner].character].name.." VENCEU"
 centered(name,32,7,2)
 centered(G.p[1].score.." - "..G.p[2].score.."  /  "..result.reason,48,9)
 rect(0,125,240,11,0)
 text((G.rematch==1 and "> " or "  ").."REVANCHE",7,129,G.rematch==1 and 7 or 9)
 text((G.rematch==2 and "> " or "  ").."SELECAO",137,129,G.rematch==2 and 7 or 9)
 if G.resultLock==0 then
  if edge(1,2) or edge(1,3) or edge(2,2) or edge(2,3) then G.rematch=3-G.rematch G.sound(0,2) end
  if edge(1,4) or edge(2,4) then
   if G.rematch==1 then G.startFight() else G.select() end
  end
 end
end
function TIC()
 G.frame=G.frame+1 readInputs()
 G.hold=(down(1,4) and down(1,5)) and G.hold+1 or 0
 if G.hold==60 then
  if G.mode=="diagnostic" then G.mode="title" else G.diagnostic() end
 end
 if G.mode=="title" then title()
 elseif G.mode=="select" then selectScreen()
 elseif G.mode=="fight" then combat() if G.mode=="result" then results() else arena() end
 elseif G.mode=="result" then results()
 elseif G.mode=="diagnostic" then diagnostic() end
end
