* **** 
* Run scenario, 
* Format of IRRPROFIle
*  what(1,3,5) = length of newly defined irradiation interval in sec
*  what(2,4,6) = beam intensity, partiles/sec
*                0 means no beam in this period
* ****
* 
* Definition of irradiation pattern for 1312 bunches per pulse
* ..+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
*      1C = 6.24153E18 electrons
*     2.4 nC/bunch
*   1312 (2625) bunches/pulse
*      5 pulse/sec
*   6.24153E18*2.4E-9*1312*5 ==> 9.8266E13 e-/sec
*      or 2625 bunches/pulse ==> 1.966E14 e-/sec
*
*   5000 hours/year operation ( ~208 days/year )
*   ===> 5000*3600=18000000 sec
*
*   1312 bunches/pulse
** IRRPROFI   18000000.  0.9827E14 
*   2625 bunches/pulse
*
IRRPROFI   18000000.  1.968E14  
*
