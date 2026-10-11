-- Local opponent: observations in, ordinary controller buttons out.
-- No player mutations, input reading, health/damage bonuses or external services.
local techniques=require('techniques').techniques
local CPU={profiles={
 easy={belt='VERMELHA',name='FACIL',color={198,66,60},reaction=22,think=14,attack_gap=50,guard=18,accuracy=45,combo=0,max_combo=1,jump=0,range=96},
 medium={belt='LARANJA',name='MEDIO',color={224,143,57},reaction=12,think=8,attack_gap=28,guard=36,accuracy=72,combo=40,max_combo=2,jump=4,range=94},
 hard={belt='PRETA',name='DIFICIL',color={43,46,51},reaction=6,think=4,attack_gap=14,guard=58,accuracy=92,combo=85,max_combo=3,jump=8,range=92}
}}
function CPU.new(level,seed)
 assert(CPU.profiles[level],'Unknown CPU level')
 return {level=level,rng=seed or 1080,clock=0,history={},input={},nextDecision=0,nextAttack=0,decisions=0,pulses=0}
end
local function chance(s,n)
 -- Floating arithmetic is deliberate: Fengari uses 32-bit integers; Lua 5.1 doubles.
 s.rng=(s.rng*48271.0)%2147483647.0
 return math.floor(s.rng/2147483647.0*100)<n
end
local function observe(p)
 local t=p.action and techniques[p.action.id]
 return {x=p.x,height=p.height,air=p.air,phase=p.phase,kind=t and t.kind,zone=t and t.zone,id=p.action and p.action.id}
end
local function direction(c,face,forward) c[(forward and face or -face)==1 and 'right' or 'left']=true end
local function attack(s,kind,face,modifier)
 local c={[kind]=true}
 if modifier=='up' or modifier=='down' then c[modifier]=true
 elseif modifier=='forward' or modifier=='back' then direction(c,face,modifier=='forward') end
 s.input=c s.release=true s.pulses=s.pulses+1
 s.nextAttack=s.clock+CPU.profiles[s.level].attack_gap
 return c
end
local function guard(s,profile,face,zone)
 if not chance(s,profile.accuracy) then zone=zone=='chudan' and 'jodan' or 'chudan' end
 local c={y=true}
 if zone=='jodan' then c.up=true
 elseif zone=='gedan' then c.down=true
 else direction(c,face,chance(s,70)) end
 s.input=c return c
end
function CPU.update(s,self,opponent,frozen)
 if frozen then return s.input end
 local profile=CPU.profiles[s.level]
 s.clock=s.clock+1
 local size=profile.reaction+1
 s.history[(s.clock-1)%size+1]=observe(opponent)
 local seen=s.clock>profile.reaction and s.history[(s.clock-profile.reaction-1)%size+1]
 -- Every action pulse has a release tick, so held buttons cannot create repeats.
 if s.release then s.release=false s.input={} return s.input end
 if not seen then s.input={} return s.input end
 local distance=math.abs(seen.x-self.x)
 local own=self.action and techniques[self.action.id]
 if self.stun>0 or self.landing>0 then s.input={} return s.input end
 if self.blockstun>0 then return s.input end
 if self.air then
  if not self.airUsed and not own and self.height>=20 and distance<128 then
   return attack(s,chance(s,65) and 'a' or 'b',self.face)
  end
  s.input={} return s.input
 end
 if own and own.kind=='attack' then
  -- Own recovery is known. Opponent information still comes from the delayed view.
  if self.action.age>own.windup+own.active and self.chain<profile.max_combo and
     not self.queued and s.comboTried~=self.executed then
   s.comboTried=self.executed
   if distance<116 and chance(s,profile.combo) then
    if self.action.id=='kizami' or own.button=='kick' then return attack(s,'b',self.face)
    else return attack(s,'a',self.face,distance>98 and 'forward' or nil) end
   end
  end
  s.input={} return s.input
 end
 if s.clock<s.nextDecision then return s.input end
 s.nextDecision=s.clock+profile.think s.decisions=s.decisions+1
 -- Watching the visible technique, never the human's keys or queued action.
 local threat=seen.kind=='attack' and seen.phase~='RECOLHE' and distance<130
 if threat and chance(s,profile.guard) then
  local zone=seen.height>16 and 'jodan' or seen.zone or 'chudan'
  return guard(s,profile,self.face,zone)
 end
 if distance>profile.range+3 then
  if profile.jump>0 and distance<136 and chance(s,profile.jump) then
   local c={up=true};direction(c,self.face,true);s.input=c return c
  end
  local c={};direction(c,self.face,true);s.input=c return c
 end
 if self.cooldown>0 then s.input={} return s.input end
 -- Anticipatory guard matters: fast punches cannot be reacted to after contact.
 if self.counter==0 and chance(s,math.floor(profile.guard*.75)) then
  return guard(s,profile,self.face,seen.zone or 'chudan')
 end
 if (s.clock>=s.nextAttack or self.counter>0) and (self.counter>0 or chance(s,s.level=='easy' and 55 or 82)) then
  if seen.kind=='defense' and s.level~='easy' and chance(s,profile.accuracy) then
   if seen.zone=='jodan' then return attack(s,'a',self.face)
   elseif chance(s,50) then return attack(s,'b',self.face,'up')
   else return attack(s,'a',self.face,'down') end
  end
  if s.level=='easy' then return attack(s,chance(s,60) and 'b' or 'a',self.face) end
  if chance(s,38) then return attack(s,'b',self.face) end
  if chance(s,34) then return attack(s,'b',self.face,chance(s,50) and 'up' or 'down') end
  return attack(s,'a',self.face,chance(s,45) and 'forward' or nil)
 end
 if chance(s,profile.guard) then return guard(s,profile,self.face,seen.zone or 'chudan') end
 -- Occasional backward spacing leaves an opening rather than an endless block.
 local c={}
 if s.level~='easy' and distance<91 and chance(s,24) then direction(c,self.face,false) end
 s.input=c return c
end
return CPU
