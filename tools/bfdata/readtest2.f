
       program readtest2

       real*8 x(6)

       open(10,file="fc_magfld.dat", form="formatted", status="old")

       do 100 i=1, 10
         read(10,*) x

         print *,x(1), x(2), x(4), x(6)

100    continue

       close(10)
 
       end

