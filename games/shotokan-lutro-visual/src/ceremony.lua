-- Presentation owns no combat clock, collision or damage state.
local config=require('techniques').presentation
local Characters=require('characters')
local C={}
function C.finish(scene)
 if scene.intro and scene.intro.origins then
  for i,p in ipairs(scene.players) do p.x=scene.intro.origins[i] end
 end
 scene.intro=nil
 for _,p in ipairs(scene.players) do p.ceremonyPose=nil;p.pose=1;p.phase='KAMAE' end
end
function C.start(scene,skip)
 C.finish(scene)
 if skip or scene.practice or scene.demo then return end
 scene.intro={age=0,total=config.intro_ticks,label='REI',origins={scene.players[1].x,scene.players[2].x}}
 for _,p in ipairs(scene.players) do p.ceremonyPose={group='ceremony',frame=1};p.phase='REI' end
end
local function chooseTouch(scene)
 local intro=scene.intro;local a,b=scene.players[1],scene.players[2]
 local first,second=Characters.animation(a,'hand_touch'),Characters.animation(b,'hand_touch')
 local best,one,two=math.huge,nil,nil
 for _,x in ipairs(first.touch) do for _,y in ipairs(second.touch) do
  local vertical=math.max(x.top,y.top)-math.min(x.bottom,y.bottom)
  local score=math.max(0,vertical)*100+math.abs((x.top+x.bottom)-(y.top+y.bottom))
  if score<best then best=score;one=x;two=y end
 end end
 intro.hands={one,two};intro.touchGap=math.max(one.top,two.top)-math.min(one.bottom,two.bottom)
 local middle=(intro.origins[1]+intro.origins[2])/2
 intro.targets={middle-(one.x-112),middle+(two.x-111)}
end
local function handGreeting(scene)
 local intro=scene.intro;local t=config.touch;local age=intro.age
 local a,b=scene.players[1].character,scene.players[2].character
 local pair=(a.visual or a.body)..'|'..(b.visual or b.body)
 if not intro.targets or intro.pair~=pair then chooseTouch(scene);intro.pair=pair end
 intro.label='TOQUEM AS MAOS'
 local progress=math.max(0,math.min(1,(age-t.approach_from)/(t.approach_to-t.approach_from)))
 local frame=2+(math.floor((age-t.approach_from)/9)%2)
 if age>=t.approach_to then frame=4 end
 if age>=t.extend_to and age<t.hold_to then frame=0 end
 if age>=t.hold_to then frame=8 end
 if age>=t.retract_to then
  progress=1-math.max(0,math.min(1,(age-t.retract_to)/(t.return_to-t.retract_to)))
  frame=2+(math.floor((age-t.retract_to)/9)%2)
 end
 for i,p in ipairs(scene.players) do
  p.x=intro.origins[i]+(intro.targets[i]-intro.origins[i])*progress
  p.ceremonyPose={group='hand_touch',frame=frame==0 and intro.hands[i].frame or frame}
  p.phase='SAUDACAO'
 end
end
function C.update(scene)
 if not scene.intro then return false end
 if scene.practice or scene.demo then C.finish(scene);return false end
 local intro=scene.intro;intro.age=intro.age+1
 if intro.age>=intro.total then
  C.finish(scene);scene.message='HAJIME!!!';scene.messageTicks=45
  return true
 end
 if intro.age>=config.touch.approach_from and intro.age<config.touch.return_to then
  handGreeting(scene);return true
 end
 if intro.age>=config.touch.return_to then
  for i,p in ipairs(scene.players) do p.x=intro.origins[i] end
 end
 for _,step in ipairs(config.steps) do
  if intro.age<step.until_tick then
   intro.label=step.label
   for _,p in ipairs(scene.players) do p.ceremonyPose={group='ceremony',frame=step.frame};p.phase=step.label end
   break
  end
 end
 return true
end
return C
