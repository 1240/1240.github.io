function FindProxyForURL(url, host)
 {
 if (isResolvable("192.168.68.65"))
 return "PROXY 192.168.68.65:8888";
 else if (isResolvable("192.168.68.66"))
 return "PROXY 192.168.68.66:8888";
 else
 return "DIRECT";
 }
