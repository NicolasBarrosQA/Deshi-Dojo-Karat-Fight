-- No tint, shader, canvas or modern scale: original historical image/quad API only.
local data=require('character_data')
local C={data=data,selected={'demo-adult','demo-adult'},overrides={},cache={},quads={},retained={},retainedBytes=0,nativeBudget=128*1024*1024}
local g=lutro.graphics
local function animations(d) return d.visual and data.special_profiles[d.visual] or data.specials[d.body] or {} end
function C.definition(port)
 local result={}
 for k,v in pairs(data.students[C.selected[port]]) do result[k]=v end
 for k,v in pairs(C.overrides[port] or {}) do result[k]=v end
 return result
end
function C.student(port,id)
 assert(data.students[id],'Unknown student')
 local old,override=C.selected[port],C.overrides[port]
 C.selected[port]=id C.overrides[port]={}
 local ok,result=pcall(C.select,port,data.students[id])
 if not ok then C.selected[port]=old C.overrides[port]=override error(result) end
 return result
end
function C.select(port,definition)
 assert(port==1 or port==2,'Invalid player')
 local d=C.definition(port)
 if definition.body and definition.body~=d.body then d.visual=false d.face='default' d.hair='default' d.identity='default' end
 if definition.identity and definition.identity~=d.identity then d.visual=false end
 if (definition.face and definition.face~=d.face) or (definition.hair and definition.hair~=d.hair) then d.visual=false end
 for k,v in pairs(definition) do d[k]=v end
 assert(data.bodies[d.body],'Unknown body')
 assert(data.belts[d.belt],'Unknown belt')
 assert(data.bodies[d.body].parts.face[d.face],'Unknown face')
 assert(data.bodies[d.body].parts.hair[d.hair],'Unknown hair')
 local previous=C.overrides[port]
 C.overrides[port]=d
 local ok,reason=pcall(C.prepare)
 if not ok then C.overrides[port]=previous error(reason) end
 return d
end
function C.prepare()
 local needed,quads,spec={}, {}, {}
 for port=1,2 do
  local d=C.definition(port);local b=data.bodies[d.body]
  local profile=d.visual and data.visual_profiles[d.visual]
  if profile then b=profile end
  if profile and profile.portrait then spec[profile.portrait]=profile.portrait_bytes or 5120 end
  -- Native special sheets load on first use; browser preloads the selected pair.
  for _,animation in pairs(lutro.browser and animations(d) or {}) do
   for _,part in ipairs({animation.body,animation.belts[d.belt]}) do
    quads[part.right]=C.quads[part.right] or {}
    for i,f in ipairs(part.frames) do quads[part.right][i]=quads[part.right][i] or g.newQuad(f.sx,f.sy,f.w,f.h,part.width,part.height) end
    for _,side in ipairs({'right','left'}) do spec[part[side]]=part.decoded_bytes/2 end
   end
  end
  for _,layer in ipairs(profile and {'body','belt'} or {'body','belt','face','hair','foreground'}) do
   local variant=layer=='belt' and d.belt or layer=='face' and d.face or layer=='hair' and d.hair or 'default'
   local part=profile and layer=='body' and b.parts.body or b.parts[layer][variant]
   quads[part.right]=C.quads[part.right] or {}
   for i,f in ipairs(part.frames) do
    quads[part.right][i]=quads[part.right][i] or g.newQuad(f.sx,f.sy,f.w,f.h,part.width,part.height)
   end
   for _,side in ipairs({'right','left'}) do
    local name=part[side]
    spec[name]=part.decoded_bytes/2
   end
  end
 end
 -- Historical image.c l_gc is a no-op: retain visited native surfaces to avoid
 -- leaking another allocation on every re-selection. Never eagerly decode all.
 if not lutro.browser then
  local extra=0 for name,bytes in pairs(spec) do if not C.retained[name] then extra=extra+bytes end end
  assert(C.retainedBytes+extra<=C.nativeBudget,'Limite de assets: reinicie o cartucho antes de trocar para mais alunos')
 end
 for name,bytes in pairs(spec) do
  needed[name]=C.cache[name] or C.retained[name] or g.newImage('assets/'..name..'.png')
  if not lutro.browser and not C.retained[name] then C.retained[name]=needed[name] C.retainedBytes=C.retainedBytes+bytes end
 end
 C.cache=needed C.quads=quads -- release unselected surfaces; deduplicate shared parts
 -- Fengari delegates lifetime to JavaScript and does not implement lua_gc.
 -- Native userdata collection does not free historical pixel buffers.
 pcall(collectgarbage,'collect')
end
function C.prepareAnimation(p,a)
 for _,part in ipairs({a.body,a.belts[p.character.belt]}) do
  C.quads[part.right]=C.quads[part.right] or {}
  for i,f in ipairs(part.frames) do C.quads[part.right][i]=C.quads[part.right][i] or g.newQuad(f.sx,f.sy,f.w,f.h,part.width,part.height) end
  for _,side in ipairs({'right','left'}) do
   local name=part[side]
   if not C.cache[name] then
    if not lutro.browser and not C.retained[name] then assert(C.retainedBytes+part.decoded_bytes/2<=C.nativeBudget,'Limite de assets: reinicie o cartucho antes de trocar para mais alunos') end
    C.cache[name]=C.retained[name] or g.newImage('assets/'..name..'.png')
    if not lutro.browser and not C.retained[name] then C.retained[name]=C.cache[name];C.retainedBytes=C.retainedBytes+part.decoded_bytes/2 end
   end
  end
 end
end
function C.bounds(p)
 if p.ceremonyPose then local a=animations(p.character)[p.ceremonyPose.group];if a then return a.bounds[p.ceremonyPose.frame] end end
 if p.specialPose then local a=animations(p.character)[p.specialPose.group];if a then return a.bounds[p.specialPose.frame] end end
 local b=p.character.visual and data.visual_profiles[p.character.visual] or data.bodies[p.character.body]
 return b.bounds[p.pose]
end
function C.draw(p,x,y)
 local pose=p.ceremonyPose or p.specialPose
 if pose then
  local a=animations(p.character)[pose.group]
  if a then
   C.prepareAnimation(p,a)
   local side=p.face==1 and 'right' or 'left'
   for _,part in ipairs({a.body,a.belts[p.character.belt]}) do
    local f=part.frames[pose.frame];local offset=p.face==1 and f.x or 224-f.x-f.w
    g.draw(C.cache[part[side]],C.quads[part.right][pose.frame],x+offset,y+f.y)
   end
   return
  end
 end
 local b=data.bodies[p.character.body];local side=p.face==1 and 'right' or 'left'
 local profile=p.character.visual and data.visual_profiles[p.character.visual]
 if profile then b=profile end
 for _,layer in ipairs(profile and {'body','belt'} or {'body','belt','face','hair','foreground'}) do
  local variant=layer=='belt' and p.character.belt or layer=='face' and p.character.face or layer=='hair' and p.character.hair or 'default'
  local part=profile and layer=='body' and b.parts.body or b.parts[layer][variant];local f=part.frames[p.pose]
  local q=C.quads[part.right][p.pose]
  local offset=p.face==1 and f.x or 224-f.x-f.w
  g.draw(C.cache[part[side]],q,x+offset,y+f.y)
 end
end
function C.portrait(port,x,y)
 local d=C.definition(port);local profile=d.visual and data.visual_profiles[d.visual]
 if profile and C.cache[profile.portrait] then
  C.portraitQuad=C.portraitQuad or g.newQuad(0,0,32,40,32,40)
  g.draw(C.cache[profile.portrait],C.portraitQuad,x,y)
 end
end
return C
