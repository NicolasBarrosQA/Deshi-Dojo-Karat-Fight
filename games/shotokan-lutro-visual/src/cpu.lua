-- Local opponent: observations in, ordinary controller buttons out.
-- No player mutations, input reading, health/damage bonuses or external services.
local techniques=require('techniques').techniques
local specials=require('techniques').specials
local CPU={profiles={
 easy={belt='VERMELHA',name='FACIL',color={198,66,60},reaction=22,think=14,attack_gap=50,guard=18,accuracy=45,combo=0,max_combo=1,jump=0,range=96},
 medium={belt='LARANJA',name='MEDIO',color={224,143,57},reaction=12,think=8,attack_gap=28,guard=36,accuracy=72,combo=40,max_combo=2,jump=4,range=94},
 hard={belt='PRETA',name='DIFICIL',color={43,46,51},reaction=6,think=4,attack_gap=14,guard=58,accuracy=92,combo=85,max_combo=3,jump=8,range=92}
}}
function CPU.new(level,seed)
 assert(CPU.profiles[level],'Unknown CPU level')
 return {level=level,rng=seed or 1080,clock=0,history={},input={},nextDecision=0,nextAttack=0,decisions=0,pulses=0,
  pressure=0,attackSerial=0,pressureUntil=0,guardUntil=0,stringAttacks=0,visibleGap=0}
end
local function chance(s,n)
 -- Floating arithmetic is deliberate: Fengari uses 32-bit integers; Lua 5.1 doubles.
 s.rng=(s.rng*48271.0)%2147483647.0
 return math.floor(s.rng/2147483647.0*100)<n
end
local function observe(p)
 local t=p.action and techniques[p.action.id] or p.special and specials[p.special.id]
 return {x=p.x,height=p.height,air=p.air,phase=p.phase,state=p.combatState,kind=t and t.kind,zone=t and t.zone,id=p.action and p.action.id or p.special and p.special.id}
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
 -- Recognize repetition from delayed, visible starts, never the human's keys.
 if seen then
  s.visibleGap=seen.kind=='attack' and 0 or s.visibleGap+1
  if s.visibleGap>=8 then s.stringAttacks=0 end
  local starts=seen.kind=='attack' and (seen.id~=s.seenId or
   seen.phase=='PREPARA' and s.seenPhase~='PREPARA')
  if starts then
   s.attackSerial=s.attackSerial+1
   s.stringAttacks=s.stringAttacks+1
   s.pressure=seen.zone==s.pressureZone and s.clock<s.pressureUntil and math.min(3,s.pressure+1) or 1
   s.pressureZone=seen.height>16 and 'jodan' or seen.zone
   s.pressureUntil=s.clock+90
  end
  s.seenId=seen.id s.seenPhase=seen.phase
 end
 -- Every action pulse has a release tick, so held buttons cannot create repeats.
 if s.release then s.release=false s.input={} return s.input end
 if not seen then s.input={} return s.input end
 local distance=math.abs(seen.x-self.x)
 local own=self.action and techniques[self.action.id]
 if self.special and self.special.id=='tai_sabaki' and self.special.age>=24 and self.special.age<=36 and distance<110 and s.taiTried~=self.executed then
  s.taiTried=self.executed;if chance(s,profile.accuracy) then return attack(s,'b',self.face) end
 end
 if self.knockdown or self.special then s.plan=nil;s.input={};return s.input end
 if s.plan then
  if self.stun>0 or self.blockstun>0 or self.cooldown>0 then s.plan=nil;s.input={};return s.input end
  if seen.kind=='attack' and seen.phase~='RECOLHE' and distance<125 then s.plan=nil;return guard(s,profile,self.face,seen.zone or 'chudan') end
  local item=s.plan[s.planIndex];s.planTick=s.planTick+1
  local c={};for _,d in ipairs(item.directions) do if d=='down' then c.down=true else direction(c,self.face,d=='forward') end end
  if item.button then c[item.button]=true end
  if s.planTick>=2 then s.planTick=0;s.planIndex=s.planIndex+1;if s.planIndex>#s.plan then s.plan=nil;s.release=true end end
  s.input=c;return c
 end
 if self.finishPermission and seen.state=='down' and distance<=114 and self.cooldown==0 and self.stun==0 and self.blockstun==0 and (not own or own.kind=='defense') then
  if s.finishTried~=self.executed then
   s.finishTried=self.executed
   if chance(s,s.level=='easy' and 30 or s.level=='medium' and 65 or 85) then return attack(s,'y',self.face,'down') end
  end
 end
 if seen.state=='down' or seen.state=='falling' or seen.state=='receiving_finish' then s.input={};return s.input end
 if self.stun>0 then
  -- A person can hold defense while being hit. Do the same, once per observed
  -- attack; the shared combat still waits for stun and defense preparation.
  if s.recoveryDecision~=s.attackSerial and s.clock>=s.nextDecision then
   s.recoveryDecision=s.attackSerial s.nextDecision=s.clock+profile.think
   s.decisions=s.decisions+1
   local anticipation=profile.guard+math.max(0,s.pressure-1)*(s.level=='easy' and 8 or 15)
   if distance<130 and s.pressureZone and chance(s,anticipation) then
    s.guardUntil=s.clock+self.stun+profile.think+5
    return guard(s,profile,self.face,s.pressureZone)
   end
  end
  if not s.input.y then s.input={} end
  return s.input
 end
 if self.landing>0 then s.input={} return s.input end
 if self.blockstun>0 then return s.input end
 if self.air then
  if not self.airUsed and not own and self.height>=20 and distance<128 then
   return attack(s,chance(s,65) and 'a' or 'b',self.face)
  end
  s.input={} return s.input
 end
 if own and own.kind=='attack' then
  -- Own recovery is known. Opponent information still comes from the delayed view.
  if self.action.spent and self.action.age>own.windup+own.active and self.chain<profile.max_combo and
     not self.queued and s.comboTried~=self.executed then
   s.comboTried=self.executed
   if distance<116 and chance(s,profile.combo) then
    if self.action.id=='kizami' then return attack(s,'b',self.face,distance>94 and 'forward' or nil)
    elseif own.button=='kick' or distance>98 then return attack(s,'b',self.face)
    else return attack(s,'a',self.face) end
   end
  end
  s.input={} return s.input
 end
 -- Punish an observed completed string, rather than always volunteering a slow
 -- kick into the next jab. The observation delay and ordinary startup remain.
 local opening=s.stringAttacks>=3 and (seen.kind~='attack' or seen.phase=='RECOLHE')
 if opening and distance<116 and self.cooldown==0 and s.openingTried~=s.attackSerial and s.clock>=s.nextDecision then
  s.openingTried=s.attackSerial s.nextDecision=s.clock+profile.think s.decisions=s.decisions+1
  if chance(s,profile.accuracy) then return attack(s,'b',self.face) end
 end
 if s.input.y and s.clock<s.guardUntil and self.counter==0 then return s.input end
 if s.clock<s.nextDecision then return s.input end
 s.nextDecision=s.clock+profile.think s.decisions=s.decisions+1
 if self.counter>0 then return attack(s,'b',self.face) end
 -- Watching the visible technique, never the human's keys or queued action.
 local threat=seen.kind=='attack' and seen.phase~='RECOLHE' and distance<130
 if threat and s.pressure<2 and s.stringAttacks<2 and self.cooldown==0 and seen.zone~='gedan' and s.level~='easy' and chance(s,s.level=='hard' and 12 or 5) then
  s.plan={{directions={'down'}},{directions={'down','back'}},{directions={'back'},button='y'}};s.planIndex=1;s.planTick=0;s.input={};return s.input
 end
 if threat and chance(s,profile.guard) then
  local zone=seen.height>16 and 'jodan' or seen.zone or 'chudan'
  return guard(s,profile,self.face,zone)
 end
 if self.cooldown>0 then
  -- Recovery locks attacks, not defense. Cover the opponent's buffered answer
  -- instead of standing idle after our own combination. One attempt per string.
  if s.input.y then return s.input end
  if s.coverTried~=self.executed then
   s.coverTried=self.executed
   local anticipation=profile.guard+math.max(0,s.pressure-1)*(s.level=='easy' and 8 or 15)
   if distance<130 and chance(s,anticipation) then
    return guard(s,profile,self.face,s.pressureZone or seen.zone or 'chudan')
   end
  end
  s.input={} return s.input
 end
 if distance>profile.range+3 then
  if profile.jump>0 and distance<136 and chance(s,profile.jump) then
   local c={up=true};direction(c,self.face,true);s.input=c return c
  end
  local c={};direction(c,self.face,true);s.input=c return c
 end
 -- Anticipatory guard matters: fast punches cannot be reacted to after contact.
 if self.counter==0 and chance(s,math.floor(profile.guard*.75)) then
  return guard(s,profile,self.face,seen.zone or 'chudan')
 end
 if (s.clock>=s.nextAttack or self.counter>0) and (self.counter>0 or chance(s,s.level=='easy' and 55 or 82)) then
  if self.counter==0 and s.pressure<2 and s.stringAttacks<2 and seen.kind~='attack' and not seen.air and chance(s,s.level=='easy' and 7 or s.level=='medium' and 22 or 38) then
   local options={{'down'},{'down','forward'},{'forward'}};local button='a'
   if s.level~='easy' and chance(s,45) then
    if chance(s,40) then options={{'back'},{'back','down'},{'down'},{'down','forward'},{'forward'}}
    elseif chance(s,45) then options={{'forward'},{'forward','down'},{'down'},{'down','back'},{'back'}}
    else options={{'forward'},{'down'},{'down','forward'}};button=chance(s,50) and 'a' or 'b' end
   end
   s.plan={};for _,dirs in ipairs(options) do s.plan[#s.plan+1]={directions=dirs} end
   s.plan[#s.plan].button=button;s.planIndex=1;s.planTick=0;s.input={};s.nextAttack=s.clock+profile.attack_gap;s.pulses=s.pulses+1;return s.input
  end
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
