#code part

def code1(twodimarr):
  pack = ''
  for k in twodimarr:
    part = ', '.join(map(str,k))
    if pack == '':
      pack = part
    else:
      pack = pack + '; ' + part
  return pack


#decode part

def cooler_float(x):
  if x=='':
    return None
  else:
    return float(x)

def decode1(pack):
  if pack == '':
    return []
  twodimarr = pack.split('; ')
  for i in range((len(twodimarr))):
    twodimarr[i] = twodimarr[i].split(', ')
    twodimarr[i] = list(map(float, twodimarr[i]))
  return twodimarr


