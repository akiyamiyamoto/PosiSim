
      program magtest

      implicit real*8 (A-H,O-Z)

      character*32 filename(5)
      data filename/'data/bfdata-r00.dat', 'data/bfdata-r10.dat',
     >              'data/bfdata-r20.dat',
     >              'data/bfdata-r30.dat', 'data/bfdata-r40.dat'/

*     x,y,z in cm unit, b in tesla
      x=0.0d0
      y=0.0d0
      do 200 ix = 1, 5
        x = 1.0 *(ix-1)
        open(10,file=filename(ix),form='formatted',status='unknown')
        do 100 i=0, 500
          z = -2.0 + 0.1*i
*          x=1.0d0
*          z=0.2d0
          call magfld(x,y,z,btx, bty, btz, b, nreg, idisc )

*        print *,"magtest=",x,y,z,btx*b, bty*b, btz*b
          write(10,*) z,btx*b,b*bty,b*btz,b


100     continue
        close(10)
200   continue
      stop
      end

