-- Presentation owns no combat clock, collision or damage state.
local config=require('techniques').presentation
local C={}
function C.finish(scene)
 scene.intro=nil
 for _,p in ipairs(scene.players) do p.ceremonyPose=nil;p.pose=1;p.phase='KAMAE' end
end
function C.start(scene,skip)
 C.finish(scene)
 if skip or scene.practice or scene.demo then return end
 scene.intro={age=0,total=config.intro_ticks,label='REI'}
 for _,p in ipairs(scene.players) do p.ceremonyPose={group='ceremony',frame=1};p.phase='REI' end
end
function C.update(scene)
 if not scene.intro then return false end
 if scene.practice or scene.demo then C.finish(scene);return false end
 local intro=scene.intro;intro.age=intro.age+1
 if intro.age>=intro.total then
  C.finish(scene);scene.message='HAJIME!';scene.messageTicks=45
  return true
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
