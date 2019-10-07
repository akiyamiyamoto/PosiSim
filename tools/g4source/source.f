*
*************************************************************************
*
      INTEGER*4 FUNCTION IDPDG2FLUKA(IDPDG)
*
*     returns Fluka particle code from PDG particle code
*
      IMPLICIT NONE
      INTEGER*4  IDPDG, NUMDAT
      PARAMETER ( NUMDAT = 14 )      
      INTEGER*4 PDGIDS(NUMDAT)
      INTEGER*4 I, K
      INTEGER*4 PDGIDS2(2, 2)

      DATA PDGIDS/ 2212, -2212, 11, -11, 12, -12, 22, 
     >             2112, -2112, -13, 13, 130, 211, -211/
      DATA (PDGIDS2(K,1), K=1, 2)/14, 27/
      DATA (PDGIDS2(K,2), K=1, 2)/-14, 28/

      DO 100 I=1, NUMDAT
         IF ( PDGIDS(I).EQ.IDPDG) THEN 
            IDPDG2FLUKA = I
            RETURN 
         ENDIF
100   CONTINUE
C
      DO 200 I=1, 2
         IF( PDGIDS2(1, I) .EQ. IDPDG) THEN 
            IDPDG2FLUKA = PDGIDS2(2,I)
            RETURN 
         ENDIF
200   CONTINUE
C
      PRINT *,'Error in PDG2FLUKA : PDGID=',IDPDG,
     > ' is not found in the table. ',
     > ' Treat this as Muon_Neutrino(ID=27)'
      IDPDG2FLUKA = 14
      RETURN

      END

*
*************************************************************************
*
*
* Read Geant4 data to simulate background to accelerating cavity
*
*
* ===== source ========================================================*
*
      SUBROUTINE SOURCE ( NOMORE )

*      IMPLICIT NONE

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'

*                                                                      *
*       Output variables:                                              *
*                                                                      *
*              Nomore = if > 0 the run will be terminated              *
*                                                                      *
*----------------------------------------------------------------------*

      INCLUDE '(BEAMCM)'
      INCLUDE '(FHEAVY)'
      INCLUDE '(FLKSTK)'
      INCLUDE '(IOIOCM)'
      INCLUDE '(LTCLCM)'
      INCLUDE '(PAPROP)'
      INCLUDE '(SOURCM)'
      INCLUDE '(SUMCOU)'
*
      LOGICAL LFIRST, LEOF
*
      SAVE LFIRST
      DATA LFIRST / .TRUE. /
*
* If reached EOF of input file
      SAVE LEOF
      DATA LEOF /.FALSE./
*
      INTEGER*4 IREAD/99/
      CHARACTER*240 INFILE
      SAVE NTOTREAD
      INTEGER*4 NTOTREAD
      DATA NTOTREAD/0/
* Number of particles for one event
      INTEGER*4 NPEVNT/1/
* Read-in data buffer
      INTEGER*4 IDEVT, IDPDG
      REAL*4    XREAD(0:3), PREAD(0:3)
      INTEGER*4 I
* Variable for initialization.
      CHARACTER*128 SDATADIR, fpref, filedata
      character*240 filepath
*======================================================================*
*                                                                      *
*                 BASIC VERSION                                        *
*                                                                      *
*======================================================================*
      NOMORE = 0
*  +-------------------------------------------------------------------*
*  |  First call initializations:
      IF ( LFIRST ) THEN
*  |  *** The following 3 cards are mandatory ***
         TKESUM = ZERZER
         LFIRST = .FALSE.
         LUSSRC = .TRUE.
*  |  *** User initialization ***
*    WHASOU(1) : Filee sequence number. =0 for file without serial number
*    WHASOU(2) : Number of particles to read per event
*    WHASOU(3) : Debug print out freequency. negative for no output.
         IWHASOU1 = int(WHASOU(1))
         IWHASOU2 = int(WHASOU(2))
         IWHASOU3 = int(WHASOU(3))         
         NTOTREAD = 0
         call get_environment_variable("FLUKA_DATA_DIR", value=SDATADIR)
         l_flukadir = len_trim(SDATADIR)
         l_SDUSOU = len_trim(SDUSOU)
         if ( l_SDUSOU .EQ. 0 ) THEN 
            fpref = "g4data"
         else
            fpref = SDUSOU
         endif   
         if ( IWHASOU1.EQ. 0 ) THEN 
            write(filedata,'(A,''.dat'')') fpref(1:len_trim(fpref))
         ELSE
            write(filedata,'(A,''.'',I0.1,''.dat'')') 
     >           fpref(1:len_trim(fpref)), IWHASOU1
         endif

         if ( l_flukadir .EQ. 0 ) then 
            filepath = filedata
         else
            write(filepath,'(a,''/'',a)')SDATADIR(1:l_flukadir),filedata
         endif
            
         print *,' IWHASOU1=',IWHASOU1
         print *,' IWHASOU2=',IWHASOU2
         print *,' IWHASOU3=',IWHASOU3
         print *,' SDATADIR=',SDATADIR
         print *,' SDUSOU=',SDUSOU

         INFILE=filepath
         print *,'Reading input data from ',
     >           filepath(1:len_trim(filepath))
         OPEN(IREAD,FILE=INFILE,FORM='UNFORMATTED',STATUS='OLD',
     >   ERR=3100)
         GOTO 3200
3100     CONTINUE
         print *,'Error to open file. Execution will be terminated.'
         STOP

3200     CONTINUE


      END IF
*  |
*  +-------------------------------------------------------------------*
*======================================================================*
*  +-------------------------------------------------------------------*
*  Push one source particle to the stack. Note that you could as well
*  push many but this way we reserve a maximum amount of space in the
*  stack for the secondaries to be generated
*  Npflka is the stack counter: of course any time source is called it
*  must be =0
      if ( NPFLKA.NE.0 ) THEN 
         print *,' In Source, NPFLKA=',NPFLKA,' is not 0'
         NPFLKA = 0
      ENDIF

      IF( LEOF ) THEN 
         PRINT *,'In Source, has reached EOF already.'
         print *,'NTOTREAD=',NTOTREAD
         print *,'WEIPRI  =', WEIPRI
         NOMORE = 2
         RETURN 
      ENDIF         
*======================================================================*
*  Read one particle from the file.  
*======================================================================*


      DO 4000 KREAD = 1, MAX(1, IWHASOU2)

      READ(IREAD, END=2000, ERR=2100) IDEVT, IDPDG, XREAD, PREAD
      NTOTREAD = NTOTREAD+1
      GOTO 1000
*
2000  CONTINUE
      LEOF = .TRUE.
      PRINT *,'In Source, READ END OF FILE of input', INFILE
      print *,'Total number of read particles is ',NTOTREAD
      print *,'Total weight of the primaries is ', WEIPRI
      NOMORE = 1
      RETURN 

2100  CONTINUE
      PRINT *,'In Source, ERROR to read from ',INFILE
      NOMORE = 10
      RETURN
*

1000  CONTINUE

      do_print = 0
      if ( IWHASOU3 .GT.0 .AND. mod(NTOTREAD, IWHASOU3) .EQ. 0 ) THEN 
         do_print=1

         print *,'Debug .. KREAD=',KREAD,' NTOTREAD=',NTOTREAD,
     >  ' Evt=',IDEVT,
     >  ' PDG=',IDPDG,' X=',XREAD,
     >  ' P=',PREAD
      ENDIF
*
* Convert unit.
*  Fluka: cm, GeV, s or nsec   Fukuda's Geant4: mm, MeV, nsec
      DO 3000 I=0, 3
         PREAD(I)=PREAD(I)*0.001
         XREAD(I)=XREAD(I)*0.1
3000  CONTINUE
      NPFLKA = NPFLKA + 1
*  Wt is the weight of the particle
* WEIPRI is the total weight of the primaries
      WTFLK  (NPFLKA) = ONEONE
      WEIPRI = WEIPRI + WTFLK (NPFLKA)
*  Particle type (1=proton.....). Ijbeam is the type set by the BEAM
*  card
*  +-------------------------------------------------------------------*
*
* Generate particle as normal hadron
*
*  |  Normal hadron:
      IF( IJBEAM .NE. -2 ) THEN 
         IONID = IDPDG2FLUKA(IDPDG)
         ILOFLK (NPFLKA) = IONID
*  |  Flag this is prompt radiation
         LRADDC (NPFLKA) = .FALSE.
*  |  Group number for "low" energy neutrons, set to 0 anyway
         IGROUP (NPFLKA) = 0
*
      ELSE
         print *,'In source, IJBEAM=-2. May be wrong BEAM card'
         STOP
      END IF
*  |
*  +-------------------------------------------------------------------*
*  From this point .....
*  Particle generation (1 for primaries)
      LOFLK  (NPFLKA) = 1
*  User dependent flag:
      LOUSE  (NPFLKA) = 0
*  No channeling:
      LCHFLK (NPFLKA) = .FALSE.
      DCHFLK (NPFLKA) = ZERZER
*  User dependent spare variables:
      DO 100 ISPR = 1, MKBMX1
         SPAREK (ISPR,NPFLKA) = ZERZER
 100  CONTINUE
*  User dependent spare flags:
      DO 200 ISPR = 1, MKBMX2
         ISPARK (ISPR,NPFLKA) = 0
 200  CONTINUE
*  Save the track number of the stack particle:
      ISPARK (MKBMX2,NPFLKA) = NPFLKA
      NPARMA = NPARMA + 1
      NUMPAR (NPFLKA) = NPARMA
      NEVENT (NPFLKA) = 0
      DFNEAR (NPFLKA) = +ZERZER
*  ... to this point: don't change anything
*  Particle age (s)
      AGESTK (NPFLKA) = +ZERZER
      AKNSHR (NPFLKA) = -TWOTWO
*  Kinetic energy of the particle (GeV)
*       TKEFLK (NPFLKA) = SQRT ( PBEAM**2 + AM (IONID)**2 ) - AM (IONID)
      TKEFLK (NPFLKA) = PREAD(0)
*  Particle momentum
      PMOFLK (NPFLKA) = SQRT(PREAD(1)**2 + PREAD(2)**2 + PREAD(3)**2)
*     PMOFLK (NPFLKA) = SQRT ( TKEFLK (NPFLKA) * ( TKEFLK (NPFLKA)
*    &                       + TWOTWO * AM (IONID) ) )
*  Cosines (tx,ty,tz)
      TXFLK  (NPFLKA) = PREAD(1)/PMOFLK(NPFLKA)
      TYFLK  (NPFLKA) = PREAD(2)/PMOFLK(NPFLKA)
      TZFLK  (NPFLKA) = PREAD(3)/PMOFLK(NPFLKA)
*     TZFLK  (NPFLKA) = SQRT ( ONEONE - TXFLK (NPFLKA)**2
*    &                       - TYFLK (NPFLKA)**2 )
*  Polarization cosines:
      TXPOL  (NPFLKA) = -TWOTWO
      TYPOL  (NPFLKA) = +ZERZER
      TZPOL  (NPFLKA) = +ZERZER
*  Particle coordinates
      XFLK   (NPFLKA) = XREAD(1)
      YFLK   (NPFLKA) = XREAD(2)
      ZFLK   (NPFLKA) = XREAD(3)
*  Calculate the total kinetic energy of the primaries: don't change
      IF ( ILOFLK (NPFLKA) .EQ. -2 .OR. ILOFLK (NPFLKA) .GT. 100000 )
     &   THEN
         TKESUM = TKESUM + TKEFLK (NPFLKA) * WTFLK (NPFLKA)
      ELSE IF ( ILOFLK (NPFLKA) .NE. 0 ) THEN
         TKESUM = TKESUM + ( TKEFLK (NPFLKA) + AMDISC (ILOFLK(NPFLKA)) )
     &          * WTFLK (NPFLKA)
      ELSE
         TKESUM = TKESUM + TKEFLK (NPFLKA) * WTFLK (NPFLKA)
      END IF
      RADDLY (NPFLKA) = ZERZER
*  Here we ask for the region number of the hitting point.
*     NREG (NPFLKA) = ...
*  The following line makes the starting region search much more
*  robust if particles are starting very close to a boundary:
      CALL GEOCRS ( TXFLK (NPFLKA), TYFLK (NPFLKA), TZFLK (NPFLKA) )
      CALL GEOREG ( XFLK  (NPFLKA), YFLK  (NPFLKA), ZFLK  (NPFLKA),
     &              NRGFLK(NPFLKA), IDISC )
*  Do not change these cards:
      CALL GEOHSM ( NHSPNT (NPFLKA), 1, -11, MLATTC )
      NLATTC (NPFLKA) = MLATTC
      CMPATH (NPFLKA) = ZERZER

4000  CONTINUE
      CALL SOEVSV
      RETURN
*=== End of subroutine Source =========================================*
      END

