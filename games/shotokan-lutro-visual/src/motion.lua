-- Lua 5.1, chronological joystick transitions; no button or fighter mutation.
local M={patterns={hcf={4,1,2,3,6},hcb={6,3,2,1,4},z={6,2,3},qcf={2,3,6},qcb={2,1,4}}}
function M.new(config) return {history={},tick=0,face=nil,consumed=0,config=config or {}} end
function M.direction(c,face)
 local x=(c.right and 1 or 0)-(c.left and 1 or 0)
 local y=(c.down and 1 or 0)-(c.up and 1 or 0)
 x=x*face
 return y==1 and (x==1 and 3 or x==-1 and 1 or 2) or y==-1 and (x==1 and 9 or x==-1 and 7 or 8) or (x==1 and 6 or x==-1 and 4 or 5)
end
function M.update(s,c,face)
 s.tick=s.tick+1
 if s.face and s.face~=face then s.history={} s.consumed=s.tick end
 s.face=face
 local d=M.direction(c,face);local h=s.history
 if #h==0 or h[#h].direction~=d then h[#h+1]={direction=d,tick=s.tick} end
 local window=s.config.window or 22
 while #h>0 and s.tick-h[1].tick>window do table.remove(h,1) end
 return d
end
function M.matches(s,name)
 local pattern=M.patterns[name];local h=s.history;local j=#h
 if not pattern or j==0 then return false end
 if h[j].direction==5 then j=j-1 end
 if j==0 or s.tick-h[j].tick>(s.config.button_grace or 4) then return false end
 local last=h[j].tick;local gap=s.config.max_gap or 10
 for k=#pattern,1,-1 do
  local expected=pattern[k]
  if s.config.four_way and (expected==1 or expected==3) and (j==0 or h[j].direction~=expected) then
   -- Optional missing diagonal only between its two required cardinals.
   -- Z still needs a distinct final forward transition after down.
   if name=='z' and k==3 then expected=6 else expected=nil end
  end
  if expected then
   if j==0 or h[j].direction~=expected or last-h[j].tick>gap then return false end
   last=h[j].tick;j=j-1
  end
 end
 return last>s.consumed and s.tick-last<=(s.config.window or 22)
end
function M.command(s,button)
 local commands=button=='kick' and {{'hcf','ura_mawashi'},{'hcb','ushiro'},{'z','nidan'},{'qcf','ashi_barai'}} or button=='punch' and {{'z','renzoku'}} or button=='defense' and {{'qcb','tai_sabaki'}} or {}
 for _,v in ipairs(commands) do if M.matches(s,v[1]) then s.consumed=s.tick;return v[2] end end
end
return M
