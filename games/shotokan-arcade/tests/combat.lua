local output=print
local keys={}
function btn(id) return keys[id] or false end
for _,name in ipairs({'cls','rect','rectb','line','print','spr','memcpy','sfx'}) do _G[name]=function() end end
dofile(arg[1])
local passed=0
local function start() G.startFight() G.intro=0 end
local function test(name,fn)
 keys={} G.inputs={{held={},previous={}},{held={},previous={}}}
 G.selections={1,2} G.ready={false,false} G.hold=0 G.frame=0 G.duration=3600 start()
 fn() passed=passed+1 output('PASS '..name)
end
local function step(n,buttons)
 keys={} for _,b in ipairs(buttons or {}) do keys[b]=true end
 for _=1,n do TIC() end
end
local function close(distance) G.p[1].x=100 G.p[2].x=100+distance end
test('titulo, selecao, confirmacao dos dois e combate',function()
 G.mode='title' step(1,{4}) assert(G.mode=='select') step(1)
 step(1,{4}) assert(G.ready[1] and not G.ready[2]) step(1,{12}) assert(G.mode=='fight')
end)
test('escolhas independentes e cancelamento',function()
 G.select() step(1,{10}) assert(G.selections[1]==1 and G.selections[2]==1)
 step(1,{12}) assert(G.ready[2]) step(1,{13}) assert(not G.ready[2])
end)
test('diagnostico separado e retorno ao titulo',function()
 G.mode='title' step(1,{5}) assert(G.mode=='diagnostic')
 step(60,{4,5}) assert(G.mode=='title')
end)
test('movimento simultaneo e limites de arena',function()
 step(20,{3,10}) assert(G.p[1].x>58 and G.p[2].x<182)
 step(1000,{3,10}) assert(G.p[2].x-G.p[1].x>=24)
 step(1000,{2,11}) assert(G.p[1].x==20 and G.p[2].x==220)
end)
test('postura e deslocamento tem quadros distintos',function()
 step(1) assert(G.p[1].pose=='idle0') step(24) assert(G.p[1].pose=='idle2')
 step(1,{3}) assert(G.p[1].pose:sub(1,4)=='step')
end)
test('quatro tecnicas, preparacao e fase ativa sincronizada',function()
 for b=4,7 do
  start() local m=G.moves[b-3]
  step(1,{b}) assert(G.p[1].pose==m.prep and not G.hit(G.p[1]))
  step(m.start-1) assert(not G.hit(G.p[1]))
  step(1) assert(G.p[1].pose==m.pose and G.hit(G.p[1]))
  step(m.active) assert(G.p[1].pose==m.retract and not G.hit(G.p[1]))
 end
end)
test('recuperacao impede novo golpe',function()
 step(1,{5}) step(2) step(1,{6}) assert(G.p[1].attack==G.moves[2])
end)
test('socos e chutes pontuam para os dois lados',function()
 for side=1,2 do
  for b=4,7 do
   start() close(b<6 and 32 or 40)
   step(1,{(side-1)*8+b}) step(G.moves[b-3].start)
   assert(G.event.source==side and G.event.technique==G.moves[b-3].name)
   assert(G.p[side].score==G.moves[b-3].points)
  end
 end
end)
test('erro de distancia nao gera ponto ou contato',function()
 step(1,{6}) step(50) assert(G.p[1].score==0 and not G.event)
end)
test('defesa reage sem conceder ponto',function()
 close(26) step(1,{5,11}) step(7,{11})
 assert(G.event.result=='blocked' and G.event.points==0 and G.p[1].score==0)
end)
test('contato unico, reacao e recuperacao durante pausa',function()
 close(32) step(1,{5}) step(7)
 assert(G.p[2].pose=='react') local score=G.p[1].score
 step(23) assert(not G.hit(G.p[1]) and G.p[1].score==score)
 step(50) assert(G.p[1].score==score and G.p[1].x==58)
end)
test('pontuacao simultanea e simetria',function()
 close(32) step(1,{5,13}) step(7)
 assert(G.p[1].score==1 and G.p[2].score==1)
end)
test('temporizador usa ticks ativos e pausa em contato',function()
 local t=G.clock step(60) assert(G.clock==t-60)
 close(32) step(1,{5}) step(7) local stopped=G.clock
 step(20) assert(G.clock==stopped)
end)
test('fim por tempo e escolha de revanche',function()
 G.clock=1 G.p[2].score=2 step(1) assert(G.mode=='result' and G.result.winner==2)
 step(24) step(1,{4}) assert(G.mode=='fight' and G.clock==3600 and G.p[2].score==0)
end)
test('fim por pontuacao e voltar a selecao',function()
 close(32) G.p[1].score=4 step(1,{5}) step(7)
 assert(G.mode=='result' and G.result.winner==1)
 step(24) step(1,{3}) step(1,{4}) assert(G.mode=='select')
end)
test('empate ao fim do tempo',function()
 G.clock=1 step(1) assert(G.result.winner==0)
end)
test('arbitragem ajustavel por qualidade e resultado',function()
 assert(G.judge({quality=39,result='contact'},G.moves[1])==0)
 assert(G.judge({quality=100,result='blocked'},G.moves[1])==0)
 assert(G.judge({quality=100,result='contact'},G.moves[3])==2)
end)
test('colisores espelhados e altura de tecnicas',function()
 for _,m in ipairs(G.moves) do
  G.p[1].attack=m G.p[2].attack=m G.p[1].tick=m.start G.p[2].tick=m.start
  local a,b=G.hit(G.p[1]),G.hit(G.p[2])
  assert(a.y==b.y and a.w==b.w and a.x-G.p[1].x==G.p[2].x-b.x-b.w)
 end
 assert(G.moves[3].box.y~=G.moves[4].box.y)
end)
test('partida longa nao sai do dominio valido',function()
 math.randomseed(2006)
 for t=1,6000 do
  local k={}
  for side=0,1 do
   if math.random(3)==1 then k[#k+1]=side*8+math.random(2,7) end
  end
  step(1,k)
  assert(G.clock>=0 and G.clock<=G.duration)
  for _,p in ipairs(G.p) do assert(p.x>=20 and p.x<=220 and p.score>=0 and ART[G.characters[p.character].id][p.pose]) end
  if G.mode=='result' then step(24) step(1,{4}) end
 end
end)
test('introducao preserva tempo e ignora ataque antes do hajime',function()
 G.startFight() local clock=G.clock
 step(35,{4,12}) assert(G.clock==clock and not G.p[1].attack and G.intro==1)
 step(1) assert(G.intro==0 and G.clock==clock)
 step(1,{5}) assert(G.p[1].attack==G.moves[2] and G.clock==clock-1)
end)
test('cada tecnica percorre antecipacao, extensao e recolhimento proprios',function()
 for b=4,7 do
  start() step(1,{b}) local m=G.p[1].attack local poses={}
  for t=0,m.start+m.active+m.recovery do poses[G.p[1].pose]=true step(1) end
  assert(poses[m.prep] and poses[m.mid] and poses[m.pose] and poses[m.retract] and poses.recover)
  assert(m.prep~=m.mid and m.retract~='recover')
 end
end)
test('oi-zuki distribui avanco durante preparacao',function()
 local x=G.p[1].x step(1,{4}) assert(G.p[1].x==x)
 step(4) assert(G.p[1].x>x and G.p[1].x<x+4)
 step(5) assert(math.abs(G.p[1].x-x-4)<.001)
end)
test('hurtbox acompanha tronco e recolhimento do chute',function()
 local p=G.p[1] local idle=G.hurt(p)
 step(1,{7}) local prep=G.hurt(p)
 assert(prep.x~=idle.x and prep.h<46)
 step(16) local active=G.hurt(p)
 assert(active.x~=prep.x and active.y>=0 and active.y+active.h<=122)
end)
test('defesa tem reacao distinta e janela de contra-ataque',function()
 close(26) step(1,{5,11}) step(7,{11})
 assert(G.event.result=='blocked' and G.p[2].pose=='block0' and G.freeze==3)
 step(9) assert(G.p[1].attack and G.p[2].stun==0)
 step(1,{13}) assert(G.p[2].attack==G.moves[2])
end)
test('golpe errado permite contra-ataque na recuperacao',function()
 step(1,{6}) step(19) close(32)
 step(1,{13}) step(7)
 assert(G.event and G.event.source==2 and G.event.counter and G.p[2].score==1)
end)
test('buffer aceita uma entrada recente no fim da recuperacao',function()
 step(1,{5}) local m=G.moves[2]
 step(m.start+m.active+m.recovery-3)
 step(1,{6}) assert(G.p[1].buffer and G.p[1].buffer.move==3)
 step(4) assert(G.p[1].attack==G.moves[3])
end)
test('spam e botao mantido nao encadeiam ataques',function()
 step(1,{5}) step(100,{5}) assert(not G.p[1].attack and not G.p[1].buffer)
 step(1) step(1,{6}) step(1,{4}) assert(not G.p[1].buffer)
end)
test('oi-zuki que vence nao confirma revanche no mesmo comando',function()
 close(32) G.p[1].score=4 step(1,{4}) step(9,{4})
 assert(G.mode=='result' and G.result.winner==1)
 step(40,{4}) assert(G.mode=='result' and G.p[1].score==5)
 step(1) step(1,{4}) assert(G.mode=='fight' and G.p[1].score==0)
end)
output('TOTAL '..passed..' testes passaram')
