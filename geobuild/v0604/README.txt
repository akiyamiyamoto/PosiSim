* Update history of geobuild

**v0604 (20190606)
- with respect to v0602,
-- Solenoid thickness: 24cm --> 34cm 
   Previous value was an error ( Not consistent with Fukuda san )
-- Water/Cupper ration of Holocon.
   8mm phi vs 13.5x13.5mm^2 
   ==> 8mm phi vs (13.5+0.3*2)^2mm^2
   福田さんの計算では、Cu の周りに0.3mm の余裕を持たせているから
　よって、
   Water/Cupper ratio = 0.253
   solenoid_cooling_pipe_thickness = solenoid_thickness(34)*0.253=8.6

-- Target to FC gap
   0.1 cm --> 0.5cm ( 森川さんと同じ値)

-- 外側のコンクリートトンネルの外側に10cm 厚の水の層を入れて、activity を見る
　 rmax=810cm.
   Now rbound3 is the outer most boundary

-- Resnuclei 
--- Fix a bug in order, RF5cp, RF5solc, RF6cp, RF6solc
--- Added RockW for Resnuclei data
--- rmax and NbinR for dose-eq plot was changed from 800 to 810cm  
--- plot range and num bins for plots, 90, 91, 92 were adjusted.


