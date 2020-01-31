subroutine write(unit, x)
  integer, intent(in) :: unit
  real*8 , intent(in) :: x(4)
 
  write(unit) x

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
