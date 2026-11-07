0x664a8: sub      sp, sp, #0x280                   
0x664ac: stp      x29, x30, [sp, #0x20]            
0x664b0: add      x29, sp, #0x20                   
0x664b4: stp      x19, x20, [sp, #0x30]            
0x664b8: stp      x21, x22, [sp, #0x40]            
0x664bc: mov      x20, x0                          
0x664c0: mov      x22, x1                          
0x664c4: stp      xzr, xzr, [sp, #0x180]           
0x664c8: add      x3, sp, #0x190                   
0x664cc: movi     v0.4s, #0                        
0x664d0: stp      q0, q0, [x3]                     
0x664d4: stp      q0, q0, [x3, #0x20]              
0x664d8: stp      q0, q0, [x3, #0x40]              
0x664dc: stp      q0, q0, [x3, #0x60]              
0x664e0: stp      q0, q0, [x3, #0x80]              
0x664e4: stp      q0, q0, [x3, #0xa0]              
0x664e8: stp      q0, q0, [x3, #0xc0]              
0x664ec: str      q0, [x3, #0xe0]                  
0x664f0: stp      xzr, xzr, [sp, #0x80]            
0x664f4: add      x3, sp, #0x90                    
0x664f8: stp      q0, q0, [x3]                     
0x664fc: stp      q0, q0, [x3, #0x20]              
0x66500: stp      q0, q0, [x3, #0x40]              
0x66504: stp      q0, q0, [x3, #0x60]              
0x66508: stp      q0, q0, [x3, #0x80]              
0x6650c: stp      q0, q0, [x3, #0xa0]              
0x66510: stp      q0, q0, [x3, #0xc0]              
0x66514: str      q0, [x3, #0xe0]                  
0x66518: adrp     x0, #0xbe000                     
0x6651c: ldrh     w0, [x0, #0xd10]                 
0x66520: strh     w0, [sp, #0x70]                  
0x66524: stur     xzr, [sp, #0x72]                 
0x66528: mov      x5, x2                           
0x6652c: adrp     x4, #0xbd000                     
0x66530: add      x4, x4, #0x598                   ; "/etc/ppp/options_%s"
0x66534: mov      x3, #0x100                       
0x66538: mov      w2, #1                           
0x6653c: mov      x1, x3                           
0x66540: add      x0, sp, #0x80                    ; "rnetGatewayDevice_X_TELEFONICA_Firewall_ConfigLoaderFunc"
0x66544: bl       #0x1f1b0                         ; <__snprintf_chk>
0x66548: add      x21, x20, #0x2c8                 ; "masq_keyword_filter"
0x6654c: adrp     x1, #0xbd000                     
0x66550: add      x1, x1, #0x5b0                   ; "Static"
0x66554: mov      x0, x21                          
0x66558: bl       #0x1e4a0                         ; <strcmp>
0x6655c: cbnz     w0, #0x66568                     
0x66560: ldrb     w0, [x20, #0x92]                 
0x66564: cbnz     w0, #0x667a8                     
0x66568: add      x6, sp, #0x80                    ; "rnetGatewayDevice_X_TELEFONICA_Firewall_ConfigLoaderFunc"
0x6656c: adrp     x5, #0xbd000                     
0x66570: add      x5, x5, #0x5e8                   ; "/etc/ppp/default_options"
0x66574: adrp     x4, #0xbd000                     
0x66578: add      x4, x4, #0x5d8                   ; "cp -rf %s %s"
0x6657c: mov      x3, #0x100                       
0x66580: mov      w2, #1                           
0x66584: mov      x1, x3                           
0x66588: add      x0, sp, #0x180                   ; "-D PREROUTING -p tcp ! -d %s --dport 53 -j DNAT --to %s:53"
0x6658c: bl       #0x1f1b0                         ; <__snprintf_chk>
0x66590: mov      w3, #0x2ae                       
0x66594: adrp     x2, #0xbe000                     
0x66598: add      x2, x2, #0xc88                   
0x6659c: add      x2, x2, #0x98                    ; "02%02x"
0x665a0: mov      w1, #0                           
0x665a4: add      x0, sp, #0x180                   ; " doesn't defined a DNSServers for it 
"
0x665a8: bl       #0x1c180                         ; <cccBeDoSystem>
0x665ac: adrp     x2, #0xe6000                     
0x665b0: ldr      x2, [x2, #0xf00]                 
0x665b4: ldr      w0, [x2]                         
0x665b8: tbz      w0, #5, #0x665d0                 
0x665bc: adrp     x0, #0xe6000                     
0x665c0: ldr      x0, [x0, #0xdf8]                 
0x665c4: ldr      w0, [x0]                         
0x665c8: cmp      w0, #6                           
0x665cc: b.hi     #0x667d4                         
0x665d0: adrp     x1, #0xb6000                     
0x665d4: add      x1, x1, #0xad8                   ; "a+"
0x665d8: add      x0, sp, #0x80                    ; "ate"
0x665dc: bl       #0x1d960                         ; <fopen>
0x665e0: mov      x19, x0                          
0x665e4: cbz      x0, #0x66800                     
0x665e8: adrp     x1, #0xbd000                     
0x665ec: add      x1, x1, #0x5b0                   ; "Static"
0x665f0: mov      x0, x21                          
0x665f4: bl       #0x1e4a0                         ; <strcmp>
0x665f8: cbnz     w0, #0x66604                     
0x665fc: ldrb     w0, [x20, #0x92]                 
0x66600: cbnz     w0, #0x6685c                     
0x66604: adrp     x0, #0xe6000                     
0x66608: ldr      x0, [x0, #0xf00]                 
0x6660c: ldr      w0, [x0]                         
0x66610: tbz      w0, #5, #0x66628                 
0x66614: adrp     x0, #0xe6000                     
0x66618: ldr      x0, [x0, #0xdf8]                 
0x6661c: ldr      w0, [x0]                         
0x66620: cmp      w0, #6                           
0x66624: b.hi     #0x66878                         
0x66628: add      x21, sp, #0x70                   
0x6662c: mov      w3, #0xa                         
0x66630: mov      x2, x21                          
0x66634: mov      x1, #0                           
0x66638: mov      x0, x22                          
0x6663c: bl       #0x1e810                         ; <libcccBeWan_getPPPPdUnitNum_wrapper>
0x66640: mov      x3, x21                          
0x66644: adrp     x2, #0xbd000                     
0x66648: add      x2, x2, #0x650                   ; "unit %s
"
0x6664c: mov      w1, #1                           
0x66650: mov      x0, x19                          
0x66654: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66658: add      x3, x20, #0x324                  ; "rectDNSTraffic"
0x6665c: adrp     x2, #0xbd000                     
0x66660: add      x2, x2, #0x660                   ; "user %s
"
0x66664: mov      w1, #1                           
0x66668: mov      x0, x19                          
0x6666c: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66670: add      x3, x20, #0x365                  ; "i >/dev/null 2>&1 &"
0x66674: adrp     x2, #0xbd000                     
0x66678: add      x2, x2, #0x670                   ; "password %s
"
0x6667c: mov      w1, #1                           
0x66680: mov      x0, x19                          
0x66684: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66688: add      x22, x20, #0x3e7                 
0x6668c: mov      x3, x22                          
0x66690: adrp     x2, #0xbd000                     
0x66694: add      x2, x2, #0x680                   ; "logfile /tmp/%sLog
"
0x66698: mov      w1, #1                           
0x6669c: mov      x0, x19                          
0x666a0: bl       #0x1d6b0                         ; <__fprintf_chk>
0x666a4: ldrh     w3, [x20, #0x18]                 
0x666a8: adrp     x2, #0xbd000                     
0x666ac: add      x2, x2, #0x698                   ; "mru %d
"
0x666b0: mov      w1, #1                           
0x666b4: mov      x0, x19                          
0x666b8: bl       #0x1d6b0                         ; <__fprintf_chk>
0x666bc: ldrh     w3, [x20, #0x1a]                 
0x666c0: adrp     x2, #0xbd000                     
0x666c4: add      x2, x2, #0x6a0                   ; "mtu %d
"
0x666c8: mov      w1, #1                           
0x666cc: mov      x0, x19                          
0x666d0: bl       #0x1d6b0                         ; <__fprintf_chk>
0x666d4: ldrh     w3, [x20, #0x20]                 
0x666d8: adrp     x2, #0xbd000                     
0x666dc: add      x2, x2, #0x6a8                   ; "lcp-echo-interval %d
"
0x666e0: mov      w1, #1                           
0x666e4: mov      x0, x19                          
0x666e8: bl       #0x1d6b0                         ; <__fprintf_chk>
0x666ec: ldrh     w3, [x20, #0x22]                 
0x666f0: adrp     x2, #0xbd000                     
0x666f4: add      x2, x2, #0x6c0                   ; "lcp-echo-failure %d
"
0x666f8: mov      w1, #1                           
0x666fc: mov      x0, x19                          
0x66700: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66704: add      x21, x20, #0x649                 ; "it:%d
"
0x66708: adrp     x1, #0xbd000                     
0x6670c: add      x1, x1, #0x6d8                   ; "PAP"
0x66710: mov      x0, x21                          
0x66714: bl       #0x1e4a0                         ; <strcmp>
0x66718: cbz      w0, #0x668a4                     
0x6671c: adrp     x1, #0xbd000                     
0x66720: add      x1, x1, #0x728                   ; "CHAP"
0x66724: mov      x0, x21                          
0x66728: bl       #0x1e4a0                         ; <strcmp>
0x6672c: cbz      w0, #0x669a8                     
0x66730: adrp     x1, #0xbd000                     
0x66734: add      x1, x1, #0x740                   ; "MS-CHAP"
0x66738: mov      x0, x21                          
0x6673c: bl       #0x1e4a0                         ; <strcmp>
0x66740: cbnz     w0, #0x66904                     
0x66744: mov      x3, x19                          
0x66748: mov      x2, #0xb                         
0x6674c: mov      x1, #1                           
0x66750: adrp     x0, #0xbd000                     
0x66754: add      x0, x0, #0x730                   ; "refuse-pap
"
0x66758: bl       #0x1ed70                         ; <fwrite>
0x6675c: mov      x3, x19                          
0x66760: mov      x2, #0xc                         
0x66764: mov      x1, #1                           
0x66768: adrp     x0, #0xbd000                     
0x6676c: add      x0, x0, #0x6e0                   ; "refuse-chap
"
0x66770: bl       #0x1ed70                         ; <fwrite>
0x66774: mov      x3, x19                          
0x66778: mov      x2, #0x11                        
0x6677c: mov      x1, #1                           
0x66780: adrp     x0, #0xbd000                     
0x66784: add      x0, x0, #0x700                   ; "refuse-mschap-v2
"
0x66788: bl       #0x1ed70                         ; <fwrite>
0x6678c: mov      x3, x19                          
0x66790: mov      x2, #0xb                         
0x66794: mov      x1, #1                           
0x66798: adrp     x0, #0xbd000                     
0x6679c: add      x0, x0, #0x718                   ; "refuse-eap
"
0x667a0: bl       #0x1ed70                         ; <fwrite>
0x667a4: b        #0x66904                         
0x667a8: add      x6, sp, #0x80                    ; "rnetGatewayDevice_X_TELEFONICA_Firewall_ConfigLoaderFunc"
0x667ac: adrp     x5, #0xbd000                     
0x667b0: add      x5, x5, #0x5b8                   ; "/etc/ppp/_options_static"
0x667b4: adrp     x4, #0xbd000                     
0x667b8: add      x4, x4, #0x5d8                   ; "cp -rf %s %s"
0x667bc: mov      x3, #0x100                       
0x667c0: mov      w2, #1                           
0x667c4: mov      x1, x3                           
0x667c8: add      x0, sp, #0x180                   ; "-D PREROUTING -p tcp ! -d %s --dport 53 -j DNAT --to %s:53"
0x667cc: bl       #0x1f1b0                         ; <__snprintf_chk>
0x667d0: b        #0x66590                         
0x667d4: add      x5, sp, #0x180                   ; "-D PREROUTING -p tcp ! -d %s --dport 53 -j DNAT --to %s:53"
0x667d8: mov      w4, #0x2af                       
0x667dc: adrp     x3, #0xbe000                     
0x667e0: add      x3, x3, #0xc88                   
0x667e4: add      x3, x3, #0x98                    ; "02%02x"
0x667e8: adrp     x2, #0xbd000                     
0x667ec: add      x2, x2, #0x608                   ; "%s@%d: %s"
0x667f0: mov      w1, #1                           
0x667f4: mov      w0, #7                           
0x667f8: bl       #0x1cc50                         ; <__syslog_chk>
0x667fc: b        #0x665d0                         
0x66800: adrp     x0, #0xe6000                     
0x66804: ldr      x0, [x0, #0xf00]                 
0x66808: ldr      w0, [x0]                         
0x6680c: tbz      w0, #5, #0x66b50                 
0x66810: adrp     x0, #0xe6000                     
0x66814: ldr      x0, [x0, #0xdf8]                 
0x66818: ldr      w0, [x0]                         
0x6681c: cmp      w0, #2                           
0x66820: b.hi     #0x6682c                         
0x66824: mov      w0, #-1                          
0x66828: b        #0x66994                         
0x6682c: add      x5, sp, #0x80                    
0x66830: mov      w4, #0x2b4                       
0x66834: adrp     x3, #0xbe000                     
0x66838: add      x3, x3, #0xc88                   
0x6683c: add      x3, x3, #0x98                    ; "02%02x"
0x66840: adrp     x2, #0xbd000                     
0x66844: add      x2, x2, #0x618                   ; "%s@%d: fopen(%s) == NULL
"
0x66848: mov      w1, #1                           
0x6684c: mov      w0, #3                           
0x66850: bl       #0x1cc50                         ; <__syslog_chk>
0x66854: mov      w0, #-1                          
0x66858: b        #0x66994                         
0x6685c: add      x3, x20, #0x92                   ; "X_TELEFONICA_Firewall_ConfigLoaderFunc"
0x66860: adrp     x2, #0xbd000                     
0x66864: add      x2, x2, #0x638                   ; "%s:
"
0x66868: mov      w1, #1                           
0x6686c: mov      x0, x19                          
0x66870: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66874: b        #0x66604                         
0x66878: mov      w5, #0                           
0x6687c: mov      w4, #0x2c1                       
0x66880: adrp     x3, #0xbe000                     
0x66884: add      x3, x3, #0xc88                   
0x66888: add      x3, x3, #0x98                    ; "02%02x"
0x6688c: adrp     x2, #0xbd000                     
0x66890: add      x2, x2, #0x640                   ; "%s@%d: unit:%d
"
0x66894: mov      w1, #1                           
0x66898: mov      w0, #7                           
0x6689c: bl       #0x1cc50                         ; <__syslog_chk>
0x668a0: b        #0x66628                         
0x668a4: mov      x3, x19                          
0x668a8: mov      x2, #0xc                         
0x668ac: mov      x1, #1                           
0x668b0: adrp     x0, #0xbd000                     
0x668b4: add      x0, x0, #0x6e0                   ; "refuse-chap
"
0x668b8: bl       #0x1ed70                         ; <fwrite>
0x668bc: mov      x3, x19                          
0x668c0: mov      x2, #0xe                         
0x668c4: mov      x1, #1                           
0x668c8: adrp     x0, #0xbd000                     
0x668cc: add      x0, x0, #0x6f0                   ; "refuse-mschap
"
0x668d0: bl       #0x1ed70                         ; <fwrite>
0x668d4: mov      x3, x19                          
0x668d8: mov      x2, #0x11                        
0x668dc: mov      x1, #1                           
0x668e0: adrp     x0, #0xbd000                     
0x668e4: add      x0, x0, #0x700                   ; "refuse-mschap-v2
"
0x668e8: bl       #0x1ed70                         ; <fwrite>
0x668ec: mov      x3, x19                          
0x668f0: mov      x2, #0xb                         
0x668f4: mov      x1, #1                           
0x668f8: adrp     x0, #0xbd000                     
0x668fc: add      x0, x0, #0x718                   ; "refuse-eap
"
0x66900: bl       #0x1ed70                         ; <fwrite>
0x66904: add      x21, x20, #0x633                 
0x66908: adrp     x1, #0xbd000                     
0x6690c: add      x1, x1, #0x748                   ; "OnDemand"
0x66910: mov      x0, x21                          
0x66914: bl       #0x1e4a0                         ; <strcmp>
0x66918: cbz      w0, #0x66a0c                     
0x6691c: adrp     x1, #0xbd000                     
0x66920: add      x1, x1, #0x7b0                   ; "AlwaysOn"
0x66924: mov      x0, x21                          
0x66928: bl       #0x1e4a0                         ; <strcmp>
0x6692c: cbnz     w0, #0x66968                     
0x66930: ldrb     w0, [x20, #0x43]                 
0x66934: cbnz     w0, #0x66adc                     
0x66938: mov      x3, x19                          
0x6693c: mov      x2, #8                           
0x66940: mov      x1, #1                           
0x66944: adrp     x0, #0xbd000                     
0x66948: add      x0, x0, #0x7e8                   ; "persist
"
0x6694c: bl       #0x1ed70                         ; <fwrite>
0x66950: mov      x3, x19                          
0x66954: mov      x2, #8                           
0x66958: mov      x1, #1                           
0x6695c: adrp     x0, #0xbd000                     
0x66960: add      x0, x0, #0x7f8                   ; "passive
"
0x66964: bl       #0x1ed70                         ; <fwrite>
0x66968: ldrb     w0, [x20, #0x532]                
0x6696c: cbnz     w0, #0x66b34                     
0x66970: mov      x3, x22                          
0x66974: adrp     x2, #0xbd000                     
0x66978: add      x2, x2, #0x820                   ; "linkname %s
"
0x6697c: mov      w1, #1                           
0x66980: mov      x0, x19                          
0x66984: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66988: mov      x0, x19                          
0x6698c: bl       #0x1e250                         ; <fclose>
0x66990: mov      w0, #0                           
0x66994: ldp      x19, x20, [sp, #0x30]            
0x66998: ldp      x21, x22, [sp, #0x40]            
0x6699c: ldp      x29, x30, [sp, #0x20]            
0x669a0: add      sp, sp, #0x280                   ; "ULL or invaild
"
0x669a4: ret                                       
0x669a8: mov      x3, x19                          
0x669ac: mov      x2, #0xb                         
0x669b0: mov      x1, #1                           
0x669b4: adrp     x0, #0xbd000                     
0x669b8: add      x0, x0, #0x730                   ; "refuse-pap
"
0x669bc: bl       #0x1ed70                         ; <fwrite>
0x669c0: mov      x3, x19                          
0x669c4: mov      x2, #0xe                         
0x669c8: mov      x1, #1                           
0x669cc: adrp     x0, #0xbd000                     
0x669d0: add      x0, x0, #0x6f0                   ; "refuse-mschap
"
0x669d4: bl       #0x1ed70                         ; <fwrite>
0x669d8: mov      x3, x19                          
0x669dc: mov      x2, #0x11                        
0x669e0: mov      x1, #1                           
0x669e4: adrp     x0, #0xbd000                     
0x669e8: add      x0, x0, #0x700                   ; "refuse-mschap-v2
"
0x669ec: bl       #0x1ed70                         ; <fwrite>
0x669f0: mov      x3, x19                          
0x669f4: mov      x2, #0xb                         
0x669f8: mov      x1, #1                           
0x669fc: adrp     x0, #0xbd000                     
0x66a00: add      x0, x0, #0x718                   ; "refuse-eap
"
0x66a04: bl       #0x1ed70                         ; <fwrite>
0x66a08: b        #0x66904                         
0x66a0c: stp      x23, x24, [sp, #0x50]            
0x66a10: stp      x25, x26, [sp, #0x60]            
0x66a14: mov      x3, x19                          
0x66a18: mov      x2, #7                           
0x66a1c: mov      x1, #1                           
0x66a20: adrp     x0, #0xbd000                     
0x66a24: add      x0, x0, #0x758                   ; "demand
"
0x66a28: bl       #0x1ed70                         ; <fwrite>
0x66a2c: ldr      w3, [x20, #8]                    
0x66a30: cbnz     w3, #0x66ac4                     
0x66a34: mov      x3, x19                          
0x66a38: mov      x2, #0x14                        
0x66a3c: mov      x1, #1                           
0x66a40: adrp     x0, #0xbd000                     
0x66a44: add      x0, x0, #0x770                   ; "ipv6cp-accept-local
"
0x66a48: bl       #0x1ed70                         ; <fwrite>
0x66a4c: bl       #0x1be50                         ; <random>
0x66a50: mov      x24, x0                          
0x66a54: bl       #0x1be50                         ; <random>
0x66a58: mov      x25, x0                          
0x66a5c: bl       #0x1be50                         ; <random>
0x66a60: mov      x26, x0                          
0x66a64: bl       #0x1be50                         ; <random>
0x66a68: mov      x21, x0                          
0x66a6c: bl       #0x1be50                         ; <random>
0x66a70: mov      x23, x0                          
0x66a74: bl       #0x1be50                         ; <random>
0x66a78: and      w0, w0, #0xffff                  
0x66a7c: str      w0, [sp, #0x10]                  
0x66a80: and      w23, w23, #0xffff                
0x66a84: str      w23, [sp, #8]                    
0x66a88: and      w21, w21, #0xffff                
0x66a8c: str      w21, [sp]                        
0x66a90: mov      w7, #0                           
0x66a94: and      w6, w26, #0xffff                 
0x66a98: and      w5, w25, #0xffff                 
0x66a9c: and      w4, w24, #0xffff                 
0x66aa0: mov      w3, #0                           
0x66aa4: adrp     x2, #0xbd000                     
0x66aa8: add      x2, x2, #0x788                   ; "ipv6 ::%x:%x:%x:%x,::%x:%x:%x:%x 
"
0x66aac: mov      w1, #1                           
0x66ab0: mov      x0, x19                          
0x66ab4: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66ab8: ldp      x23, x24, [sp, #0x50]            
0x66abc: ldp      x25, x26, [sp, #0x60]            
0x66ac0: b        #0x66968                         
0x66ac4: adrp     x2, #0xbd000                     
0x66ac8: add      x2, x2, #0x760                   ; "idle %u
"
0x66acc: mov      w1, #1                           
0x66ad0: mov      x0, x19                          
0x66ad4: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66ad8: b        #0x66a34                         
0x66adc: mov      x3, x19                          
0x66ae0: mov      x2, #6                           
0x66ae4: mov      x1, #1                           
0x66ae8: adrp     x0, #0xbd000                     
0x66aec: add      x0, x0, #0x7c0                   ; "+ipv6
"
0x66af0: bl       #0x1ed70                         ; <fwrite>
0x66af4: mov      x3, x19                          
0x66af8: mov      x2, #0x16                        
0x66afc: mov      x1, #1                           
0x66b00: adrp     x0, #0xbd000                     
0x66b04: add      x0, x0, #0x7c8                   ; "ipv6cp-use-persistent
"
0x66b08: bl       #0x1ed70                         ; <fwrite>
0x66b0c: ldrb     w0, [x20, #0x42]                 
0x66b10: cmp      w0, #2                           
0x66b14: b.ne     #0x66938                         
0x66b18: mov      x3, x19                          
0x66b1c: mov      x2, #5                           
0x66b20: mov      x1, #1                           
0x66b24: adrp     x0, #0xbd000                     
0x66b28: add      x0, x0, #0x7e0                   ; "noip
"
0x66b2c: bl       #0x1ed70                         ; <fwrite>
0x66b30: b        #0x66938                         
0x66b34: add      x3, x20, #0x532                  
0x66b38: adrp     x2, #0xbd000                     
0x66b3c: add      x2, x2, #0x808                   ; "pppoe_srv_name %s"
0x66b40: mov      w1, #1                           
0x66b44: mov      x0, x19                          
0x66b48: bl       #0x1d6b0                         ; <__fprintf_chk>
0x66b4c: b        #0x66970                         
0x66b50: mov      w0, #-1                          
0x66b54: b        #0x66994                         
0x66b58: stp      x29, x30, [sp, #-0xe0]!          
0x66b5c: mov      x29, sp                          
0x66b60: stp      x19, x20, [sp, #0x10]            
0x66b64: stp      x21, x22, [sp, #0x20]            
0x66b68: stp      x23, x24, [sp, #0x30]            
0x66b6c: stp      x25, x26, [sp, #0x40]            
0x66b70: stp      x27, x28, [sp, #0x50]            
0x66b74: mov      x24, x0                          
0x66b78: mov      x23, x2                          
0x66b7c: stp      xzr, xzr, [sp, #0xc8]            
0x66b80: str      wzr, [sp, #0xd8]                 
0x66b84: stp      xzr, xzr, [sp, #0x80]            
0x66b88: add      x0, sp, #0x90                    ; "e_X_TELEFONICA_Firewall_ConfigLoaderFunc"
0x66b8c: movi     v0.4s, #0                        
0x66b90: stp      q0, q0, [x0]                     
0x66b94: str      q0, [x0, #0x20]                  
0x66b98: strb     wzr, [x0, #0x30]                 
0x66b9c: lsr      x28, x1, #0x38                   
0x66ba0: ubfx     x27, x1, #0x30, #8               
0x66ba4: ubfx     x22, x1, #0x28, #8               
0x66ba8: mov      x25, #0                          
0x66bac: str      wzr, [sp, #0x74]                 
0x66bb0: mov      w21, #1                          
0x66bb4: adrp     x0, #0xbd000                     
0x66bb8: add      x0, x0, #0x578                   ; "%d,%d,%d,%d"
0x66bbc: str      x0, [sp, #0x68]                  
0x66bc0: adrp     x0, #0xe6000                     
0x66bc4: ldr      x26, [x0, #0xf00]                
0x66bc8: adrp     x0, #0xbe000                     
0x66bcc: add      x0, x0, #0xc88                   
0x66bd0: add      x0, x0, #0xb0                    ; "null 2>&1 &"
0x66bd4: str      x0, [sp, #0x78]                  
0x66bd8: b        #0x66d30                         
0x66bdc: mov      w0, #0xeb                        
0x66be0: bl       #0x1e7c0                         ; <cccRdmProtoFullPathByOID>
0x66be4: mov      x7, x0                           
0x66be8: mov      x6, x20                          
0x66bec: mov      w5, #0xeb                        
0x66bf0: mov      w4, #0x32f                       
0x66bf4: ldr      x3, [sp, #0x78]                  
0x66bf8: adrp     x2, #0xa7000                     
0x66bfc: add      x2, x2, #0xc8                    ; "%s@%d: get OID=%d, IA=%llx, %s
"
0x66c00: mov      w1, #1                           
0x66c04: mov      w0, #7                           
0x66c08: bl       #0x1cc50                         ; <__syslog_chk>
0x66c0c: b        #0x66d80                         
0x66c10: mov      x2, x20                          
0x66c14: mov      w1, #0xeb                        
0x66c18: mov      x0, x24                          
0x66c1c: bl       #0x1c7b0                         ; <cccRdmAddObjectWithAssignIA>
0x66c20: mov      x19, x0                          
0x66c24: b        #0x66d8c                         
0x66c28: add      x1, x19, #0x22                   ; "stering config object...
"
0x66c2c: stp      xzr, xzr, [x1]                   
0x66c30: strb     wzr, [x19, #0x32]                
0x66c34: adrp     x0, #0xaa000                     
0x66c38: add      x0, x0, #0x2d0                   ; "0.0.0.0"
0x66c3c: ldr      w2, [x0]                         
0x66c40: stur     w2, [x19, #0x22]                 
0x66c44: ldur     w0, [x0, #3]                     
0x66c48: stur     w0, [x19, #0x25]                 
0x66c4c: mov      x25, x19                         
0x66c50: b        #0x66d24                         
0x66c54: add      x3, x19, #0x22                   ; "
"
0x66c58: adrp     x2, #0xc1000                     
0x66c5c: add      x2, x2, #0x1f0                   ; "%s"
0x66c60: mov      x1, #0x14                        
0x66c64: add      x0, sp, #0xc8                    ; "odify Username.
"
0x66c68: bl       #0x1c470                         ; <snprintf>
0x66c6c: b        #0x66df8                         
0x66c70: add      x0, x19, #1                      ; "d Account.
"
0x66c74: stp      xzr, xzr, [x0]                   
0x66c78: stp      xzr, xzr, [x0, #0x10]            
0x66c7c: strb     wzr, [x19, #0x21]                
0x66c80: adrp     x1, #0xbd000                     
0x66c84: add      x1, x1, #0x590                   ; "FromISP"
0x66c88: ldr      w2, [x1]                         
0x66c8c: stur     w2, [x19, #1]                    
0x66c90: ldur     w1, [x1, #3]                     
0x66c94: str      w1, [x19, #4]                    
0x66c98: add      x1, x19, #0x22                   ; "DoSAction"
0x66c9c: stp      xzr, xzr, [x1]                   
0x66ca0: strb     wzr, [x19, #0x32]                
0x66ca4: adrp     x0, #0xaa000                     
0x66ca8: add      x0, x0, #0x2d0                   ; "0.0.0.0"
0x66cac: ldr      w2, [x0]                         
0x66cb0: stur     w2, [x19, #0x22]                 
0x66cb4: ldur     w0, [x0, #3]                     
0x66cb8: stur     w0, [x19, #0x25]                 
0x66cbc: mov      x25, x19                         
0x66cc0: b        #0x66d24                         
0x66cc4: add      x0, x25, #1                      ; "imeout
"
0x66cc8: stp      xzr, xzr, [x0]                   
0x66ccc: stp      xzr, xzr, [x0, #0x10]            
0x66cd0: strb     wzr, [x25, #0x21]                
0x66cd4: mov      w0, #0x6f4e                      
0x66cd8: movk     w0, #0x656e, lsl #16             
0x66cdc: stur     w0, [x25, #1]                    
0x66ce0: add      x0, x25, #0x22                   ; "
"
0x66ce4: stp      xzr, xzr, [x0]                   
0x66ce8: strb     wzr, [x25, #0x32]                
0x66cec: cbz      x19, #0x66d24                    
0x66cf0: adrp     x0, #0xe6000                     
0x66cf4: ldr      x0, [x0, #0xf00]                 
0x66cf8: ldr      w0, [x0]                         
0x66cfc: tbz      w0, #5, #0x66d14                 
0x66d00: adrp     x0, #0xe6000                     
0x66d04: ldr      x0, [x0, #0xdf8]                 
0x66d08: ldr      w0, [x0]                         
0x66d0c: cmp      w0, #6                           
0x66d10: b.hi     #0x66e20                         
0x66d14: mov      x2, x20                          
0x66d18: mov      w1, #0xeb                        
0x66d1c: mov      x0, x24                          
0x66d20: bl       #0x1e7e0                         ; <cccRdmDelObjectByOID>
0x66d24: add      w21, w21, #1                     
0x66d28: cmp      w21, #4                          
0x66d2c: b.eq     #0x66e54                         
0x66d30: mov      w4, w21                          
0x66d34: mov      w3, w22                          
0x66d38: mov      w2, w27                          
0x66d3c: mov      w1, w28                          
0x66d40: ldr      x0, [sp, #0x68]                  
0x66d44: bl       #0x1dce0                         ; <rdmConstructIAValue>
0x66d48: mov      x20, x0                          
0x66d4c: mov      w3, #1                           
0x66d50: mov      x2, x0                           
0x66d54: mov      w1, #0xeb                        
0x66d58: mov      x0, x24                          
0x66d5c: bl       #0x1de40                         ; <cccRdmGetObjectByOID>
0x66d60: mov      x19, x0                          
0x66d64: ldr      w0, [x26]                        
0x66d68: tbz      w0, #5, #0x66d80                 
0x66d6c: adrp     x0, #0xe6000                     
0x66d70: ldr      x0, [x0, #0xdf8]                 
0x66d74: ldr      w0, [x0]                         
0x66d78: cmp      w0, #6                           
0x66d7c: b.hi     #0x66bdc                         
0x66d80: ldrb     w0, [x23, #0x32]                 
0x66d84: cbz      w0, #0x66cc4                     
0x66d88: cbz      x19, #0x66c10                    
0x66d8c: ldrb     w0, [x23, #0x33]                 
0x66d90: cbnz     w0, #0x66c70                     
0x66d94: add      x20, x19, #1                     
0x66d98: adrp     x1, #0xbd000                     
0x66d9c: add      x1, x1, #0x590                   ; "FromISP"
0x66da0: mov      x0, x20                          
0x66da4: bl       #0x1e4a0                         ; <strcmp>