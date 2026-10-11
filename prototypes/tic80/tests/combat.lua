-- Testa a logica real do cartucho com entradas e desenho isolados.
local luaPrint=print
local buttons={}
function btn(id) return buttons[id] or false end
for _,name in ipairs({'cls','rect','rectb','line','print'}) do _G[name]=function() end end
dofile(arg[1])
local count=0
local function test(name,fn)
 buttons={} DD.mode='fight' DD.reset() DD.hold=0 DD.resetHold=0
 fn() count=count+1 luaPrint('PASS '..name)
end
local function step(n,keys)
 buttons={} for _,key in ipairs(keys or {}) do buttons[key]=true end
 for i=1,n do TIC() end
end
local function close(distance) DD.p[1].x=100 DD.p[2].x=100+distance end
test('P1 e P2 independentes na tela diagnostica',function()
 DD.mode='diagnostic' step(10,{3,8})
 assert(DD.p[1].x==78 and DD.p[2].x==172 and DD.p[2].y==95)
end)
test('oito indicadores por porta',function()
 DD.mode='diagnostic' step(1,{0,1,2,3,4,5,6,7})
 for b=0,7 do assert(DD.p[1].buttons[b] and not DD.p[2].buttons[b]) end
end)
test('troca de tela e sem repeticao ao segurar',function()
 DD.mode='diagnostic' step(60,{4,5}) assert(DD.mode=='fight')
 step(60,{4,5}) assert(DD.mode=='fight')
 step(1) step(60,{4,5}) assert(DD.mode=='diagnostic')
end)
test('corpos nao atravessam e arena limita',function()
 close(18) step(1000,{3,10})
 assert(DD.p[2].x-DD.p[1].x>=18)
 step(1000,{2,11}) assert(DD.p[1].x==12 and DD.p[2].x==228)
end)
test('soco pontua sem barra de vida',function()
 close(30) step(1,{5}) step(6)
 assert(DD.p[1].points==1 and DD.event.technique=='GYAKU-ZUKI')
 assert(DD.event.target==2 and DD.event.quality>=35)
end)
test('somente fase ativa causa contato',function()
 close(30) step(1,{5}) step(5) assert(DD.event==nil)
 step(1) assert(DD.event.result=='contact')
end)
test('ataque fora do alcance nao pontua',function()
 step(1,{5}) step(40) assert(DD.p[1].points==0 and DD.event==nil)
end)
test('defesa nao pontua',function()
 close(23) step(1,{5,11}) step(6,{11})
 assert(DD.event.result=='blocked' and DD.p[1].points==0)
end)
test('contato unico por ataque',function()
 close(30) step(1,{5}) step(7) local score=DD.p[1].points
 step(20) assert(DD.p[1].points==score)
end)
test('todos os quatro golpes funcionam para P2',function()
 for b=4,7 do
  DD.reset() close(30) step(1,{8+b}) step(DD.moves[b-3].start)
  assert(DD.event.source==2 and DD.event.technique==DD.moves[b-3].name)
  assert(DD.p[2].points==DD.moves[b-3].points)
 end
end)
test('troca simultanea nao privilegia P1',function()
 close(30) step(1,{5,13}) step(6)
 assert(DD.p[1].points==1 and DD.p[2].points==1)
end)
test('recuperacao impede encadear novo ataque',function()
 step(1,{5}) step(2) step(1,{6})
 assert(DD.p[1].attack.name=='GYAKU-ZUKI')
end)
test('julgamento substituivel considera qualidade',function()
 assert(DD.judge({result='contact',quality=34},DD.moves[1])==0)
 assert(DD.judge({result='blocked',quality=100},DD.moves[1])==0)
 assert(DD.judge({result='contact',quality=100},DD.moves[3])==2)
end)
test('vitoria e reinicio por combinacao',function()
 close(30) DD.p[1].points=4 step(1,{5}) step(6)
 assert(DD.winner=='P1') step(60,{6,7})
 assert(DD.winner==nil and DD.p[1].points==0)
end)
luaPrint('TOTAL '..count..' testes passaram')
