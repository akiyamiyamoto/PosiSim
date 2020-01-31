       program readtest

       real*8 x(4)

       open(10,file="fc_magfld.bnn", form="unformatted", status="old")

       do 100 i=1, 10
         read(10) x

         print *,x(1), x(2), x(3), x(4)

100    continue

       close(10)
 
       end

