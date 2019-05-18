#code part

def code(twodimarr):
  pack = ''
  for k in twodimarr:
    part = ', '.join(map(str,k))
    if pack == '':
      pack = part
    else:
      pack = pack + '; ' + part
  return pack


#decode part

def decode(pack):
  twodimarr = pack.split('; ')
  for i in range((len(twodimarr))):
    twodimarr[i] = twodimarr[i].split(', ')
    twodimarr[i] = list(map(float, twodimarr[i]))
  return twodimarr


