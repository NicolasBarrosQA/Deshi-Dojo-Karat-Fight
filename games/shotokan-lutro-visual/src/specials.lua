-- Special choreography uses its own action clock; damage still needs contact.
local catalog=require('techniques')
local Motion=require('motion')
local S={}
local rules=catalog.special_rules
local function ready(p)
 return not p.knockdown and not p.special and not p.air and p.stun==0 and p.blockstun==0 and p.landing==0 and p.cooldown==0 and (not p.action or catalog.techniques[p.action.id].kind=='defense')
end
function S.init(p) p.motion=Motion.new(rules.motion);p.combatState='standing' end
function S.start(p,id)
 local t=catalog.specials[id]
 if not t or not ready(p) then return false end
 p.action=nil;p.queued=nil;p.guard=false;p.chain=0;p.chainTime=0;p.low=false
 p.special={id=id,age=0,hits={},face=p.face};p.executed=p.executed+1;p.lastTechnique=id
 p.combatState='attacking';p.phase='PREPARA';p.specialPose={group=t.group,frame=1}
 return true
end
function S.request(scene,i,c,old)
 local p,target=scene.players[i],scene.players[3-i]
 Motion.update(p.motion,c,p.face)
 local button=c.a and not old.a and 'kick' or c.b and not old.b and 'punch' or c.y and not old.y and 'defense'
 if p.knockdown then p.queued=nil;p.pendingSpecial=nil;return true end
 if button then p.pendingSpecial=nil end
 if p.pendingSpecial and scene.freeze==0 then
  p.pendingSpecial.ttl=p.pendingSpecial.ttl-1
  if p.pendingSpecial.ttl<0 then p.pendingSpecial=nil
  elseif ready(p) then local id=p.pendingSpecial.id;p.pendingSpecial=nil;S.start(p,id);return true end
 end
 if scene.freeze==0 and c.y and not old.y and c.down and p.finishPermission and target.knockdown and target.combatState=='down' and target.knockdown.owner==i and not target.knockdown.used and math.abs(target.x-p.x)<=rules.finish_range and (target.x-p.x)*p.face>0 and ready(p) then
  if S.start(p,'ashi_finish') then
   p.finishPermission=nil;target.knockdown.used=true;target.knockdown.finisher=i
   target.combatState='receiving_finish';target.phase='CONTATO CONTROLADO';p.special.target=3-i
   return true
  end
 end
 if scene.freeze==0 and p.special and p.special.id=='tai_sabaki' and c.b and not old.b and p.special.age>=catalog.specials.tai_sabaki.counter_from and p.special.age<=catalog.specials.tai_sabaki.counter_to then
  p.special=nil;p.specialPose=nil;p.cooldown=0;S.start(p,'tai_counter');return true
 end
 if button and not p.air then
  local id=Motion.command(p.motion,button)
  if id then
   if ready(p) and scene.freeze==0 then S.start(p,id)
   else p.pendingSpecial={id=id,ttl=catalog.combo.buffer_ticks} end
   return true
  end
 end
 return p.special~=nil
end
local function frame(t,age)
 local elapsed=0
 for i,d in ipairs(t.durations) do elapsed=elapsed+d;if age<=elapsed then return i end end
 return #t.durations
end
local function ground(p) p.air=false;p.height=0;p.vy=0;p.jumpVX=0;p.knockVX=0;p.stun=0;p.blockstun=0;p.action=nil;p.queued=nil end
function S.fall(scene,target,owner)
 ground(target);target.special=nil;target.pendingSpecial=nil;target.specialPose={group='knockdown',frame=1};target.guard=false;target.low=false
 target.knockdown={owner=owner,age=0,used=false,restX=math.max(rules.ground_visual_radius,math.min(384-rules.ground_visual_radius,target.x))};target.combatState='off_balance';target.phase='DESEQUILIBRIO'
 scene.players[owner].finishPermission=true
end
function S.update(scene,i,move)
 local p=scene.players[i]
 if p.knockdown then
  ground(p);local k=p.knockdown;k.age=k.age+1
  if p.combatState=='receiving_finish' then
   p.specialPose={group='knockdown',frame=k.contact and 6 or 5};return true
  end
  if k.rising then
   k.rising=k.rising+1;p.combatState=k.rising>rules.rise_ticks and 'recovering_guard' or 'getting_up';p.phase='LEVANTAR'
   p.specialPose={group='knockdown',frame=k.rising<9 and 7 or k.rising<18 and 8 or 9}
   if k.rising>=rules.rise_ticks+rules.guard_recovery then p.knockdown=nil;p.specialPose=nil;p.pose=1;p.combatState='standing';p.phase='KAMAE';p.cooldown=rules.guard_recovery end
  elseif k.age<=rules.fall_ticks then
   move(p,(k.restX-p.x)/(rules.fall_ticks-k.age+1))
   p.combatState=k.age<=rules.balance_ticks and 'off_balance' or 'falling';p.phase=k.age<=rules.balance_ticks and 'DESEQUILIBRIO' or 'CAINDO'
   p.specialPose={group='knockdown',frame=math.min(5,1+math.floor((k.age-1)*5/rules.fall_ticks))}
   if k.age==rules.fall_ticks then scene.dust={x=p.x,age=0};if scene.sound then scene.sound('ground') end end
  else
   p.combatState='down';p.phase='CAIDO';p.specialPose={group='knockdown',frame=5}
   if k.age>=rules.fall_ticks+rules.finish_window then k.rising=0;scene.players[k.owner].finishPermission=nil end
  end
  return true
 end
 local a=p.special
 if not a then p.specialPose=nil;p.combatState=p.stun>0 and 'off_balance' or p.action and (p.guard and 'defending' or 'attacking') or p.cooldown>0 and 'recovering_guard' or 'standing';return false end
 local t=catalog.specials[a.id];a.age=a.age+1
 p.specialPose={group=t.group,frame=frame(t,a.age)};p.phase=a.age<=t.windup and 'PREPARA' or a.age<=t.active_end and 'GOLPE' or 'RECOLHE'
 if t.step and a.age<=t.windup then move(p,p.face*t.step/t.windup) end
 if a.id=='nidan' then p.height=a.age>=t.takeoff and a.age<=t.landing and math.sin((a.age-t.takeoff)/(t.landing-t.takeoff)*math.pi)*t.jump_height or 0 end
 if a.age>=t.total then
  if a.target then local target=scene.players[a.target];if target.knockdown and target.knockdown.finisher==i then target.knockdown.rising=0;target.combatState='getting_up' end end
  p.special=nil;p.specialPose=nil;p.height=0;p.phase='KAMAE';p.combatState='recovering_guard';p.cooldown=t.recovery_lock
 end
 return true
end
function S.evading(p,zone)
 local a=p.special;local t=a and catalog.specials[a.id]
 return a and a.id=='tai_sabaki' and a.age>=t.evade_from and a.age<=t.evade_to and zone~='gedan' or false
end
function S.contacts(scene,defended)
 local pending={}
 for i,p in ipairs(scene.players) do
  local a=p.special;local t=a and catalog.specials[a.id];local target=scene.players[3-i]
  if a and t.kind=='attack' then
   for n,h in ipairs(t.contacts) do
    local valid=a.id=='ashi_finish' and target.combatState=='receiving_finish' and target.knockdown and target.knockdown.finisher==i or a.id~='ashi_finish' and not target.knockdown
    if valid and not a.hits[n] and a.age>=h.first and a.age<=h.last and not (a.id=='ashi_barai' and (target.air or target.height>0)) and not S.evading(target,t.zone) then
     local dx=(target.x-p.x)*p.face
     -- Each contact has authored reach/height, tested against the actual body band.
     local band=scene.zoneBox(target,t.zone)
     local y=h.y-(a.id=='nidan' and p.height or 0)
     local overlap=y<band.y+band.h and y+h.height>band.y
     if dx>=h.near and dx<=h.far and (a.id=='ashi_finish' or overlap) then
      local blocked,parry,defense,reason=defended(target,t.zone)
      if a.id=='ashi_finish' then blocked=false;parry=false;reason='finalizacao autorizada' end
      local visual=t.visual_contact and t.visual_contact[p.character.body]
      pending[#pending+1]={player=i,technique=a.id,zone=t.zone,damage=h.damage,blocked=blocked,parry=parry,defense=defense,defenseReason=reason,contact=n,tick=scene.tick,distance=math.abs(dx),contactX=visual and p.x+p.face*visual.x or (p.x+target.x)/2,contactY=visual and visual.y or y+h.height/2,quality='arcade'}
     end
    end
   end
  end
 end
 for _,e in ipairs(pending) do
  local p,target=scene.players[e.player],scene.players[3-e.player];local a=p.special
  if a then
   a.hits[e.contact]=true;p.contacts=p.contacts+1
   if e.blocked then
    target.blocks=target.blocks+1;target.blockstun=catalog.arcade.blockstun
    if e.parry then target.parries=target.parries+1;target.counter=16 end
    scene.message=string.upper(e.defense or 'GUARDA')..' / '..catalog.specials[e.technique].label..' DEFENDIDO'
   else
    p.points=p.points+1
    if not scene.practice and not scene.demo then target.energy=math.max(0,target.energy-e.damage) end
    if e.technique=='ashi_barai' then S.fall(scene,target,e.player);scene.message='ASHI-BARAI / BAIXO + DEFESA PARA FINALIZAR';if scene.sound then scene.sound('sweep') end
    elseif e.technique=='ashi_finish' then target.knockdown.contact=true;scene.message='ASHI-BARAI FINISH!';scene.finishEmphasis=18;if scene.sound then scene.sound('finish') end
    else
     if target.special and target.special.id=='nidan' then target.height=0 end
     target.special=nil;target.specialPose=nil;target.action=nil;target.queued=nil;target.stun=catalog.arcade.hitstun;target.reaction=e.zone=='jodan' and 86 or 85;target.phase='IMPACTO';target.guard=false
     scene.message=catalog.specials[e.technique].label
    end
   end
   scene.messageTicks=65;scene.flash=e.blocked and 4 or 6;scene.freeze=math.max(scene.freeze,e.technique=='ashi_finish' and rules.finish_hitstop or e.blocked and catalog.arcade.blockstop or catalog.arcade.hitstop)
   scene.impact={x=e.contactX,y=e.contactY,blocked=e.blocked};scene.lastContact=e
   if scene.onContact then scene.onContact(e) end
  end
 end
end
return S
