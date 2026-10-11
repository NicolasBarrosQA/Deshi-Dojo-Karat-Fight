-- title: Deshi Dojo Karate Fight - prova P1/P2
-- author: Deshi Dojo contributors
-- desc: Diagnostico e kumite experimental offline
-- script: lua
-- license: MIT

-- APIs basicas presentes no commit TIC-80 de setembro de 2019.
DD={mode="diagnostic",frame=0,hold=0,resetHold=0,pointsToWin=5,
    event=nil,pause=0,winner=nil}
local moves={
 {name="OI-ZUKI",start=8,active=4,recovery=15,reach=24,advance=6,points=1},
 {name="GYAKU-ZUKI",start=6,active=3,recovery=17,reach=21,advance=0,points=1},
 {name="MAE-GERI",start=11,active=4,recovery=20,reach=30,advance=0,points=2},
 {name="MAWASHI-GERI",start=14,active=5,recovery=24,reach=33,advance=0,points=2}
}
DD.moves=moves
local function clamp(v,a,b) return math.max(a,math.min(b,v)) end
local function player(i,x)
 return {id=i,x=x,y=105,face=i==1 and 1 or -1,points=0,
         attack=nil,tick=0,spent=false,guard=false,stun=0,
         buttons={},previous={},color=i==1 and 9 or 3}
end
function DD.reset()
 DD.p={player(1,68),player(2,172)}
 DD.event=nil DD.pause=0 DD.winner=nil DD.roundFrame=0
end
DD.reset()
local function inputs()
 for i,p in ipairs(DD.p) do
  for b=0,7 do
   p.previous[b]=p.buttons[b] or false
   p.buttons[b]=btn((i-1)*8+b)
  end
 end
end
local function pressed(p,b) return p.buttons[b] and not p.previous[b] end
local function overlap(a,b)
 return a.x<b.x+b.w and b.x<a.x+a.w and a.y<b.y+b.h and b.y<a.y+a.h
end
local function hurt(p) return {x=p.x-7,y=88,w=14,h=30} end
local function hit(p)
 local m=p.attack
 if not m or p.spent or p.tick<m.start or p.tick>=m.start+m.active then return nil end
 return {x=p.face==1 and p.x+7 or p.x-7-m.reach,y=100,w=m.reach,h=9}
end
-- Regra substituivel: pontuacao arcade experimental, nao arbitragem oficial.
function DD.judge(event,move)
 if event.result~="contact" then return 0 end
 if event.quality<35 then return 0 end
 return move.points
end
local function evaluate(a,b)
 local box=hit(a)
 if not box or not overlap(box,hurt(b)) then return nil end
 local m=a.attack
 local distance=math.abs(a.x-b.x)
 local optimal=14+m.reach*0.65
 local quality=clamp(math.floor(100-math.abs(distance-optimal)*4),0,100)
 local e={technique=m.name,source=a.id,target=b.id,distance=distance,
          targetZone="chudan",quality=quality,
          result=b.guard and "blocked" or "contact",frame=DD.frame}
 e.points=DD.judge(e,m)
 return e
end
local function constrain()
 local a,b=DD.p[1],DD.p[2]
 a.x=clamp(a.x,12,228) b.x=clamp(b.x,12,228)
 -- Os lutadores nunca trocam de lado; colisao simetrica dos corpos.
 if b.x-a.x<18 then
  local middle=clamp((a.x+b.x)/2,21,219)
  a.x=middle-9 b.x=middle+9
 end
end
local function fight()
 if DD.winner then return end
 if DD.pause>0 then
  DD.pause=DD.pause-1
  if DD.pause==0 then
   for i,p in ipairs(DD.p) do
    p.x=i==1 and 68 or 172 p.attack=nil p.tick=0 p.stun=0 p.spent=false
   end
  end
  return
 end
 DD.roundFrame=DD.roundFrame+1
 for _,p in ipairs(DD.p) do
  p.guard=false
  if p.stun>0 then p.stun=p.stun-1
  elseif p.attack then
   p.tick=p.tick+1
   if p.tick>=p.attack.start+p.attack.active+p.attack.recovery then
    p.attack=nil p.tick=0
   end
  else
   local direction=(p.buttons[3] and 1 or 0)-(p.buttons[2] and 1 or 0)
   p.guard=direction==-p.face
   p.x=p.x+direction
   -- Evita atacar ao segurar combinacoes de navegacao.
   if not (p.buttons[4] and p.buttons[5]) and not (p.buttons[6] and p.buttons[7]) then
    for b=4,7 do
     if pressed(p,b) then
      p.attack=moves[b-3] p.tick=0 p.spent=false p.guard=false
      p.x=p.x+p.face*p.attack.advance
      break
     end
    end
   end
  end
 end
 constrain()
 -- Julgar os dois lados antes de alterar qualquer um: permite troca simultanea.
 local first=evaluate(DD.p[1],DD.p[2])
 local second=evaluate(DD.p[2],DD.p[1])
 for _,e in ipairs({first or false,second or false}) do
  if e then
   local a,b=DD.p[e.source],DD.p[e.target]
   a.spent=true a.points=a.points+e.points DD.event=e
   if e.result=="contact" then b.stun=10 end
   if e.points>0 then DD.pause=60 end
  end
 end
 local a,b=DD.p[1],DD.p[2]
 if a.points>=DD.pointsToWin or b.points>=DD.pointsToWin then
  DD.winner=a.points==b.points and "EMPATE" or (a.points>b.points and "P1" or "P2")
 end
end
local function avatar(p,y)
 local x=p.x local f=p.face local c=p.color
 rect(x-4,y-31,8,8,4) -- cabeca
 rect(x-6,y-23,12,15,12) -- kimono
 rect(x-6,y-13,12,3,c) -- faixa
 line(x-3,y-8,x-7,y,12) line(x+3,y-8,x+7,y,12)
 local extension=p.attack and (p.tick>=p.attack.start and p.tick<p.attack.start+p.attack.active) and p.attack.reach or 9
 line(x,y-18,x+f*extension,y-18,p.guard and 11 or c)
 line(x,y-20,x-f*7,y-14,12)
 if p.attack and p.attack.points==2 then line(x,y-6,x+f*extension,y-14,c) end
end
local labels={"U","D","L","R","A","B","X","Y"}
local function indicators(p,x,y)
 for b=0,7 do
  local px=x+(b%4)*25 local py=y+math.floor(b/4)*12
  rect(px,py,22,10,p.buttons[b] and p.color or 1)
  print(labels[b+1],px+8,py+2,12)
 end
end
local function diagnostic()
 cls(0)
 print("DESHI DOJO - TESTE P1/P2",8,5,12)
 print("P1",10,20,9) print("P2",128,20,3)
 for i,p in ipairs(DD.p) do
  p.x=clamp(p.x+(p.buttons[3] and 1 or 0)-(p.buttons[2] and 1 or 0),10,230)
  p.y=clamp(p.y+(p.buttons[1] and 1 or 0)-(p.buttons[0] and 1 or 0),85,113)
  indicators(p,i==1 and 10 or 128,32)
  avatar(p,p.y)
 end
 line(0,116,239,116,5)
 print("P1: SEGURE A+B 1s -> KUMITE",3,124,12)
end
local function arena()
 cls(0) rect(0,28,240,90,2) rect(0,118,240,18,5)
 line(10,88,230,88,1) rectb(16,35,208,45,4)
 print("DESHI DOJO / KUMITE EXPERIMENTAL",2,2,12)
 print("P1 "..DD.p[1].points,4,14,9)
 print("ATE 5 PONTOS",82,14,12)
 print("P2 "..DD.p[2].points,196,14,3)
 for _,p in ipairs(DD.p) do avatar(p,118) end
 if DD.event then
  local e=DD.event
  print(e.technique.." "..e.result.." +"..e.points,4,30,12)
  print("DIST "..e.distance.." PREC "..e.quality,4,39,12)
 end
 if DD.winner then
  rect(28,62,184,18,0) print(DD.winner.." / P1 X+Y REINICIA",32,68,12)
 end
 print("A OI  B GYAKU  X MAE  Y MAWASHI",2,122,12)
 print("P1 A+B: TELA / X+Y: REINICIAR",2,130,12)
end
function TIC()
 DD.frame=DD.frame+1 inputs()
 local p=DD.p[1]
 DD.hold=(p.buttons[4] and p.buttons[5]) and DD.hold+1 or 0
 DD.resetHold=(p.buttons[6] and p.buttons[7]) and DD.resetHold+1 or 0
 if DD.hold==60 then
  DD.mode=DD.mode=="diagnostic" and "fight" or "diagnostic"
  DD.reset()
 elseif DD.resetHold==60 then DD.reset() end
 if DD.mode=="diagnostic" then diagnostic() else fight() arena() end
end
