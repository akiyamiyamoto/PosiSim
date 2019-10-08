subroutine write(unit, evtid, pdgid, x, p)
  integer, intent(in) :: evtid, pdgid, unit
  real*8 , intent(in) :: x(4), p(4)
 
  write(unit) evtid, pdgid, x, p

end subroutine write

subroutine open(unit, outfile)
  integer, intent(in) :: unit
  character(*), intent(in) :: outfile

  open(unit, file=outfile, form="unformatted", status='replace')
  print *,'A file, ', outfile,' was opened.'

end subroutine open

subroutine close(unit)
  integer, intent(in) :: unit
  close(unit)
  print *,'File was cloased.'
end subroutine close
