-- Capability probe only; the Shotokan game has not been migrated.
local image,x={},{42,280}
function lutro.load()
 image=lutro.graphics.newImage('colors.png')
end
function lutro.update(dt)
 for p=1,2 do
  if lutro.joystick.isDown(p,7) then x[p]=x[p]-1 end
  if lutro.joystick.isDown(p,8) then x[p]=x[p]+1 end
 end
end
function lutro.draw()
 lutro.graphics.setColor(255,255,255)
 lutro.graphics.draw(image,20,52)
 for p=1,2 do
  lutro.graphics.setColor(p==1 and 235 or 65,p==1 and 65 or 155,p==1 and 80 or 220)
  lutro.graphics.rectangle('fill',x[p],164,8,14)
  for b=1,14 do
   if lutro.joystick.isDown(p,b) then lutro.graphics.rectangle('fill',16+b*22,185+(p-1)*15,12,8) end
  end
 end
end
