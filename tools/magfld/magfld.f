*$ CREATE MAGFLD.FOR
*COPY MAGFLD
*
*===magfld=============================================================*
*
      SUBROUTINE MAGFLD ( X, Y, Z, BTX, BTY, BTZ, B, NREG, IDISC )

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1988-2010      by Alberto Fasso` & Alfredo Ferrari *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     Created  in     1988         by    Alberto Fasso`                *
*                                                                      *
*                                                                      *
*     Last change on 06-Nov-10     by    Alfredo Ferrari               *
*                                                                      *
*     Input variables:                                                 *
*            x,y,z = current position ( cm )                           *
*            nreg  = current region                                    *
*     Output variables:                                                *
*            btx,bty,btz = cosines of the magn. field vector           *
*            B = magnetic field intensity (Tesla)                      *
*            idisc = set to 1 if the particle has to be discarded      *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(CMEMFL)'
      INCLUDE '(CSMCRY)'
*
*  +-------------------------------------------------------------------*
*  variables defined by A.M.
      LOGICAL LFIRST
      SAVE LFIRST
      DATA LFIRST / .TRUE. /
*
      CHARACTER*128 bdatadir, bfilename
      CHARACTER*256 bfilepath
*
      REAL*8   zrange(2), rmax
      REAL*8   zstep, zfdmap, zfcreal, zmap
      integer*4 numdata, numdummy 

*     zdata, rmax is cm unit.
*      data zrange/  -2.0D0, 30.0D0 /
      data zrange/  -2.0D0, 1050.0D0 /
      data rmax/ 10.0D0 /
*      data rmax/ 3.0D0 /
      data zstep/0.05d0/
*     Z of FC in the field map (cm)
      data zfcmap/  0.5d0 /
*     z of FC front surcace ( cm ) of this simulation
      data zfcmc /0.2d0/
      
      real*8 znow
      integer l_dir, l_name
      parameter ( maxdata = 30000 )
      real*8 bdata(4,maxdata), readbuf(6)
      integer*4 iread/99/

      common/bfielddata/ numdata, numdummy, bdata
      save /bfielddata/
*
* First call to this routine. Initialize data
*
      
      if ( lfirst ) then 
         bdatadir ="/home/ilc/miyamoto/fluka/tools/bfdata"
         bfilename="fc_magfld.dat"
         l_dir = len_trim(bdatadir)
         l_name = len_trim(bfilename)
         write(bfilepath, '(a,''/'',a)') bdatadir(1:l_dir), 
     >                                   bfilename(1:l_name)
         print *,'Reading input bfield data from ',
     >           bfilepath(1:len_trim(bfilepath))
         OPEN(IREAD, FILE=bfilepath, FORM="FORMATTED", 
     >        STATUS='OLD', ERR=3100 )
         GOTO 3200
3100     CONTINUE
         print *,'Error to open file, ',
     >           bfilepath(1:len_trim(bfilepath))
         print *,'Job is terminated.'
         STOP
C
3200     CONTINUE

         numdata = 0
         znow = 0.0 
         do while ( znow .lt. zrange(2) )          
            read( iread, *, end=3400, err=3500) readbuf
            znow = readbuf(1)/10.0
            if ( znow.ge.zrange(1).and.znow.le.zrange(2) ) then 
               numdata = numdata+1
               bdata(1,numdata) = znow
               bdata(2,numdata) = readbuf(2)
               bdata(3,numdata) = readbuf(4)
               bdata(4,numdata) = readbuf(6)
            endif                             
         end do
         close(iread)
         print *,'MAGFLD read data from ', 
     >            bfilepath(1:len_trim(bfilepath))
         print *,' Z from ',zrange(1),' cm to ',zrange(2),
     >           ' cm ',numdata,' data ' 
         LFIRST=.FALSE.
         goto 3900
* ===================== read error ===================================*
3500     continue
         print *,'Error: Read error while reading mag field data.'
         close(iread)
         stop
3400     continue
         print *,'Error: reached end of file before reading ',
     >           ' last mag. field. Something is wrong.'
         close(iread)
         stop

3900     continue
      end if
* ===================== Normal step to calculate bfield===============*

*
*  +-------------------------------------------------------------------*
*  |  Earth geomagnetic field:
c      IF ( LGMFLD ) THEN
c         CALL GEOFLD ( X, Y, Z, BTX, BTY, BTZ, B, NREG, IDISC )
c         RETURN
c      END IF
*  |
*  +-------------------------------------------------------------------*
      IDISC = 0

* 2 Tesla uniform field along +z:
c      BTX   = UMGFLD
c      BTY   = VMGFLD
c      BTZ   = WMGFLD
c      B     = BIFUNI
      BTX   = 0.0d0
      BTY   = 0.0d0
      BTZ   = 1.0d0
      B     = 0.0d0
      zmap = z - zfcmc + zfcmap 
      rnow = sqrt( x*x + y*y )
      if ( zmap.le. zrange(1) .or. zmap .ge. zrange(2) .or. 
     >   rnow .gt.rmax ) then 
         return
      endif
*
* FC reagion: provide FC mag field.
*
      ip = ( zmap  - zrange(1) ) / zstep + 1
      
*      print *,' z=',z,' zmap=',zmap,' ip=',ip,' zrange=',zrange,
*     >  ' rnow=',rnow,' x,y=',x,y
*      print *,' ip points b data at z=',(bdata(k, ip),k=1,4)

      zscale = ( zmap - bdata(1,ip) ) / zstep
      bz0 = bdata(2, ip) + ( bdata(2,ip+1)-bdata(2,ip) ) * zscale
      bz1 = bdata(3, ip) + ( bdata(3,ip+1)-bdata(3,ip) ) * zscale
      bz2 = bdata(4, ip) + ( bdata(4,ip+1)-bdata(4,ip) ) * zscale
      
      br = ( -0.5d0*rnow*1.0d-2*bz1 )
      bz = ( bz0 - 0.25d0*rnow*rnow*1.0d-4*bz2 )
      if ( rnow .gt. 0.0d0 ) then 
        bx = br * x / rnow
        by = br * y / rnow
      endif


      B = sqrt( br*br + bz*bz )
      BTZ = bz/B
      BTX = bx/B
      btysq = 1.0D0 - btz*btz - btx*btx
      if ( btysq .ge. 0.0d0 ) then 
         bty = sqrt(btysq)
      else
         bty = 0.0d0
      endif
*      print *,'x,y,z=',x,y,z,'rnow=',rnow,' br, bz=',br,bz,
*     >     'btx,bty,btz=',btx,bty,btz,' b=',B 
  
      RETURN

*=== End of subroutine Magfld =========================================*
      END

