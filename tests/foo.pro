pro foo, arg=arg
  IF KEYWORD_SET(arg) THEN BEGIN
     print,"True"
  ENDIF ELSE BEGIN
     print, "False"
  ENDELSE
end
