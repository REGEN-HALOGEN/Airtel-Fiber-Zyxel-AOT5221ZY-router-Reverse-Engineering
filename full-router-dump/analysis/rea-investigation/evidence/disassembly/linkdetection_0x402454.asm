0x402454:  sub      sp, sp, #0x360                   
0x402458:  stp      x29, x30, [sp]                   
0x40245c:  mov      x29, sp                          
0x402460:  str      x0, [sp, #0x18]                  
0x402464:  str      xzr, [sp, #0x348]                
0x402468:  str      xzr, [sp, #0x340]                
0x40246c:  str      xzr, [sp, #0x358]                
0x402470:  str      wzr, [sp, #0x33c]                
0x402474:  mov      w0, #1                           
0x402478:  strb     w0, [sp, #0x327]                 
0x40247c:  strb     wzr, [sp, #0x326]                
0x402480:  strh     wzr, [sp, #0x324]                
0x402484:  add      x0, sp, #0x200                   
0x402488:  stp      xzr, xzr, [x0, #0x20]            
0x40248c:  add      x0, sp, #0x230                   
0x402490:  movi     v0.4s, #0                        
0x402494:  stp      q0, q0, [x0]                     
0x402498:  stp      q0, q0, [x0, #0x20]              
0x40249c:  stp      q0, q0, [x0, #0x40]              
0x4024a0:  stp      q0, q0, [x0, #0x60]              
0x4024a4:  stp      q0, q0, [x0, #0x80]              
0x4024a8:  stp      q0, q0, [x0, #0xa0]              
0x4024ac:  stp      q0, q0, [x0, #0xc0]              
0x4024b0:  str      q0, [x0, #0xe0]                  
0x4024b4:  stp      xzr, xzr, [sp, #0x120]           
0x4024b8:  add      x0, sp, #0x130                   
0x4024bc:  movi     v0.4s, #0                        
0x4024c0:  stp      q0, q0, [x0]                     
0x4024c4:  stp      q0, q0, [x0, #0x20]              
0x4024c8:  stp      q0, q0, [x0, #0x40]              
0x4024cc:  stp      q0, q0, [x0, #0x60]              
0x4024d0:  stp      q0, q0, [x0, #0x80]              
0x4024d4:  stp      q0, q0, [x0, #0xa0]              
0x4024d8:  stp      q0, q0, [x0, #0xc0]              
0x4024dc:  str      q0, [x0, #0xe0]                  
0x4024e0:  str      xzr, [sp, #0x330]                
0x4024e4:  mov      w0, #-1                          
0x4024e8:  str      w0, [sp, #0x354]                 
0x4024ec:  stp      xzr, xzr, [sp, #0x20]            
0x4024f0:  add      x0, sp, #0x30                    
0x4024f4:  movi     v0.4s, #0                        
0x4024f8:  stp      q0, q0, [x0]                     
0x4024fc:  stp      q0, q0, [x0, #0x20]              
0x402500:  stp      q0, q0, [x0, #0x40]              
0x402504:  stp      q0, q0, [x0, #0x60]              
0x402508:  stp      q0, q0, [x0, #0x80]              
0x40250c:  stp      q0, q0, [x0, #0xa0]              
0x402510:  stp      q0, q0, [x0, #0xc0]              
0x402514:  str      q0, [x0, #0xe0]                  
0x402518:  str      xzr, [sp, #0x328]                
0x40251c:  ldr      x0, [sp, #0x18]                  
0x402520:  cmp      x0, #0                           
0x402524:  b.ne     #0x402530                        
0x402528:  mov      w0, #-1                          
0x40252c:  b        #0x40352c                        
0x402530:  adrp     x0, #0x403000                    
0x402534:  add      x1, x0, #0x960                   ; "config.xml"
0x402538:  adrp     x0, #0x403000                    
0x40253c:  add      x0, x0, #0x970                   ; "config.rdm"
0x402540:  bl       #0x401380                        ; <rdmInit>
0x402544:  str      x0, [sp, #0x348]                 
0x402548:  ldr      x0, [sp, #0x348]                 
0x40254c:  cmp      x0, #0                           
0x402550:  b.ne     #0x4025a0                        
0x402554:  adrp     x0, #0x414000                    
0x402558:  ldr      x0, [x0, #0xfc8]                 
0x40255c:  ldr      w0, [x0]                         
0x402560:  and      w0, w0, #0x20                    
0x402564:  cmp      w0, #0                           
0x402568:  b.eq     #0x402598                        
0x40256c:  adrp     x0, #0x414000                    
0x402570:  ldr      x0, [x0, #0xfd8]                 
0x402574:  ldr      w0, [x0]                         
0x402578:  cmp      w0, #2                           
0x40257c:  b.ls     #0x402598                        
0x402580:  adrp     x0, #0x404000                    
0x402584:  add      x2, x0, #0x68                    ; "linkdetect_switch_WanMode"
0x402588:  adrp     x0, #0x403000                    
0x40258c:  add      x1, x0, #0x980                   ; "%s(): RDMInit Fail!
"
0x402590:  mov      w0, #3                           
0x402594:  bl       #0x4011d0                        ; <syslog>
0x402598:  mov      w0, #-1                          
0x40259c:  b        #0x40352c                        
0x4025a0:  adrp     x0, #0x403000                    
0x4025a4:  add      x0, x0, #0x998                   ; "linkdetection_rtk"
0x4025a8:  bl       #0x4011a0                        ; <cmsgInit>
0x4025ac:  adrp     x0, #0x403000                    
0x4025b0:  add      x0, x0, #0x9b0                   ; "ccc_das"
0x4025b4:  bl       #0x4013c0                        ; <cmsgGetModuleIdByName>
0x4025b8:  str      w0, [sp, #0x33c]                 
0x4025bc:  adrp     x0, #0x403000                    
0x4025c0:  add      x1, x0, #0x9b8                   ; "GPON"
0x4025c4:  ldr      x0, [sp, #0x18]                  
0x4025c8:  bl       #0x401300                        ; <strcmp>
0x4025cc:  cmp      w0, #0                           
0x4025d0:  b.ne     #0x402b04                        
0x4025d4:  bl       #0x4012d0                        ; <cmsgCreateRequest>
0x4025d8:  str      x0, [sp, #0x340]                 
0x4025dc:  ldr      x0, [sp, #0x340]                 
0x4025e0:  cmp      x0, #0                           
0x4025e4:  b.eq     #0x402ad4                        
0x4025e8:  add      x3, sp, #0x120                   
0x4025ec:  adrp     x0, #0x403000                    
0x4025f0:  add      x2, x0, #0x9c0                   ; "InternetGatewayDevice.X_5067F0_Ext.WANSwitch"
0x4025f4:  mov      x1, #0x100                       
0x4025f8:  mov      x0, x3                           
0x4025fc:  bl       #0x401210                        ; <snprintf>
0x402600:  ldr      x0, [sp, #0x348]                 
0x402604:  ldr      w0, [x0]                         
0x402608:  mov      w1, w0                           
0x40260c:  add      x0, sp, #0x120                   
0x402610:  mov      w2, w1                           
0x402614:  mov      x1, x0                           
0x402618:  ldr      x0, [sp, #0x340]                 
0x40261c:  bl       #0x401350                        ; <cmsgRequestSel>
0x402620:  add      x3, sp, #0x220                   
0x402624:  adrp     x0, #0x403000                    
0x402628:  add      x2, x0, #0x9b8                   ; "GPON"
0x40262c:  mov      x1, #0x100                       
0x402630:  mov      x0, x3                           
0x402634:  bl       #0x401210                        ; <snprintf>
0x402638:  add      x0, sp, #0x220                   
0x40263c:  mov      x3, x0                           
0x402640:  mov      w2, #-0x40000000                 
0x402644:  adrp     x0, #0x403000                    
0x402648:  add      x1, x0, #0x9f0                   ; "WANMode"
0x40264c:  ldr      x0, [sp, #0x340]                 
0x402650:  bl       #0x401330                        ; <cmsgRequestSet>
0x402654:  add      x0, sp, #0x326                   
0x402658:  mov      x3, x0                           
0x40265c:  mov      w2, #1                           
0x402660:  movk     w2, #0x2000, lsl #16             
0x402664:  adrp     x0, #0x403000                    
0x402668:  add      x1, x0, #0x9f8                   ; "WanAutoDetect"
0x40266c:  ldr      x0, [sp, #0x340]                 
0x402670:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402674:  add      x3, sp, #0x120                   
0x402678:  adrp     x0, #0x403000                    
0x40267c:  add      x2, x0, #0xa08                   ; "InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig"
0x402680:  mov      x1, #0x100                       
0x402684:  mov      x0, x3                           
0x402688:  bl       #0x401210                        ; <snprintf>
0x40268c:  ldr      x0, [sp, #0x348]                 
0x402690:  ldr      w0, [x0]                         
0x402694:  mov      w1, w0                           
0x402698:  add      x0, sp, #0x120                   
0x40269c:  mov      w2, w1                           
0x4026a0:  mov      x1, x0                           
0x4026a4:  ldr      x0, [sp, #0x340]                 
0x4026a8:  bl       #0x401350                        ; <cmsgRequestSel>
0x4026ac:  add      x0, sp, #0x327                   
0x4026b0:  mov      x3, x0                           
0x4026b4:  mov      w2, #1                           
0x4026b8:  movk     w2, #0x2000, lsl #16             
0x4026bc:  adrp     x0, #0x403000                    
0x4026c0:  add      x1, x0, #0xa48                   ; "Enable"
0x4026c4:  ldr      x0, [sp, #0x340]                 
0x4026c8:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4026cc:  add      x3, sp, #0x120                   
0x4026d0:  adrp     x0, #0x403000                    
0x4026d4:  add      x2, x0, #0xa50                   ; "InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig"
0x4026d8:  mov      x1, #0x100                       
0x4026dc:  mov      x0, x3                           
0x4026e0:  bl       #0x401210                        ; <snprintf>
0x4026e4:  ldr      x0, [sp, #0x348]                 
0x4026e8:  ldr      w0, [x0]                         
0x4026ec:  mov      w1, w0                           
0x4026f0:  add      x0, sp, #0x120                   
0x4026f4:  mov      w2, w1                           
0x4026f8:  mov      x1, x0                           
0x4026fc:  ldr      x0, [sp, #0x340]                 
0x402700:  bl       #0x401350                        ; <cmsgRequestSel>
0x402704:  add      x0, sp, #0x326                   
0x402708:  mov      x3, x0                           
0x40270c:  mov      w2, #1                           
0x402710:  movk     w2, #0x2000, lsl #16             
0x402714:  adrp     x0, #0x403000                    
0x402718:  add      x1, x0, #0xa48                   ; "Enable"
0x40271c:  ldr      x0, [sp, #0x340]                 
0x402720:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402724:  add      x3, sp, #0x120                   
0x402728:  adrp     x0, #0x403000                    
0x40272c:  add      x2, x0, #0xa90                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1"
0x402730:  mov      x1, #0x100                       
0x402734:  mov      x0, x3                           
0x402738:  bl       #0x401210                        ; <snprintf>
0x40273c:  ldr      x0, [sp, #0x348]                 
0x402740:  ldr      w0, [x0]                         
0x402744:  mov      w1, w0                           
0x402748:  add      x0, sp, #0x120                   
0x40274c:  mov      w2, w1                           
0x402750:  mov      x1, x0                           
0x402754:  ldr      x0, [sp, #0x340]                 
0x402758:  bl       #0x401350                        ; <cmsgRequestSel>
0x40275c:  add      x0, sp, #0x327                   
0x402760:  mov      x3, x0                           
0x402764:  mov      w2, #1                           
0x402768:  movk     w2, #0x2000, lsl #16             
0x40276c:  adrp     x0, #0x403000                    
0x402770:  add      x1, x0, #0xa48                   ; "Enable"
0x402774:  ldr      x0, [sp, #0x340]                 
0x402778:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x40277c:  add      x3, sp, #0x120                   
0x402780:  adrp     x0, #0x403000                    
0x402784:  add      x2, x0, #0xae0                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1"
0x402788:  mov      x1, #0x100                       
0x40278c:  mov      x0, x3                           
0x402790:  bl       #0x401210                        ; <snprintf>
0x402794:  ldr      x0, [sp, #0x348]                 
0x402798:  ldr      w0, [x0]                         
0x40279c:  mov      w1, w0                           
0x4027a0:  add      x0, sp, #0x120                   
0x4027a4:  mov      w2, w1                           
0x4027a8:  mov      x1, x0                           
0x4027ac:  ldr      x0, [sp, #0x340]                 
0x4027b0:  bl       #0x401350                        ; <cmsgRequestSel>
0x4027b4:  add      x0, sp, #0x327                   
0x4027b8:  mov      x3, x0                           
0x4027bc:  mov      w2, #1                           
0x4027c0:  movk     w2, #0x2000, lsl #16             
0x4027c4:  adrp     x0, #0x403000                    
0x4027c8:  add      x1, x0, #0xa48                   ; "Enable"
0x4027cc:  ldr      x0, [sp, #0x340]                 
0x4027d0:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4027d4:  add      x3, sp, #0x120                   
0x4027d8:  adrp     x0, #0x403000                    
0x4027dc:  add      x2, x0, #0xb30                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1"
0x4027e0:  mov      x1, #0x100                       
0x4027e4:  mov      x0, x3                           
0x4027e8:  bl       #0x401210                        ; <snprintf>
0x4027ec:  ldr      x0, [sp, #0x348]                 
0x4027f0:  ldr      w0, [x0]                         
0x4027f4:  mov      w1, w0                           
0x4027f8:  add      x0, sp, #0x120                   
0x4027fc:  mov      w2, w1                           
0x402800:  mov      x1, x0                           
0x402804:  ldr      x0, [sp, #0x340]                 
0x402808:  bl       #0x401350                        ; <cmsgRequestSel>
0x40280c:  add      x0, sp, #0x326                   
0x402810:  mov      x3, x0                           
0x402814:  mov      w2, #1                           
0x402818:  movk     w2, #0x2000, lsl #16             
0x40281c:  adrp     x0, #0x403000                    
0x402820:  add      x1, x0, #0xa48                   ; "Enable"
0x402824:  ldr      x0, [sp, #0x340]                 
0x402828:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x40282c:  add      x3, sp, #0x120                   
0x402830:  adrp     x0, #0x403000                    
0x402834:  add      x2, x0, #0xb80                   ; "InternetGatewayDevice.LANDevice.1.X_5067F0_IPv6LANHostConfigManagement.NDPPD"
0x402838:  mov      x1, #0x100                       
0x40283c:  mov      x0, x3                           
0x402840:  bl       #0x401210                        ; <snprintf>
0x402844:  ldr      x0, [sp, #0x348]                 
0x402848:  ldr      w0, [x0]                         
0x40284c:  mov      w1, w0                           
0x402850:  add      x0, sp, #0x120                   
0x402854:  mov      w2, w1                           
0x402858:  mov      x1, x0                           
0x40285c:  ldr      x0, [sp, #0x340]                 
0x402860:  bl       #0x401350                        ; <cmsgRequestSel>
0x402864:  add      x0, sp, #0x326                   
0x402868:  mov      x3, x0                           
0x40286c:  mov      w2, #1                           
0x402870:  movk     w2, #0x2000, lsl #16             
0x402874:  adrp     x0, #0x403000                    
0x402878:  add      x1, x0, #0xbd0                   ; "Enabled"
0x40287c:  ldr      x0, [sp, #0x340]                 
0x402880:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402884:  add      x3, sp, #0x120                   
0x402888:  adrp     x0, #0x403000                    
0x40288c:  add      x2, x0, #0xbd8                   ; "InternetGatewayDevice.LANDevice.1.X_5067F0_IPv6LANHostConfigManagement.IPv6PDWanConnection"
0x402890:  mov      x1, #0x100                       
0x402894:  mov      x0, x3                           
0x402898:  bl       #0x401210                        ; <snprintf>
0x40289c:  ldr      x0, [sp, #0x348]                 
0x4028a0:  ldr      w0, [x0]                         
0x4028a4:  mov      w1, w0                           
0x4028a8:  add      x0, sp, #0x120                   
0x4028ac:  mov      w2, w1                           
0x4028b0:  mov      x1, x0                           
0x4028b4:  ldr      x0, [sp, #0x340]                 
0x4028b8:  bl       #0x401350                        ; <cmsgRequestSel>
0x4028bc:  add      x3, sp, #0x220                   
0x4028c0:  adrp     x0, #0x403000                    
0x4028c4:  add      x2, x0, #0xa90                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1"
0x4028c8:  mov      x1, #0x100                       
0x4028cc:  mov      x0, x3                           
0x4028d0:  bl       #0x401210                        ; <snprintf>
0x4028d4:  add      x0, sp, #0x220                   
0x4028d8:  mov      x3, x0                           
0x4028dc:  mov      w2, #-0x40000000                 
0x4028e0:  adrp     x0, #0x403000                    
0x4028e4:  add      x1, x0, #0xc38                   ; "Interface"
0x4028e8:  ldr      x0, [sp, #0x340]                 
0x4028ec:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4028f0:  add      x3, sp, #0x120                   
0x4028f4:  adrp     x0, #0x403000                    
0x4028f8:  add      x2, x0, #0xc48                   ; "InternetGatewayDevice.Layer3Forwarding"
0x4028fc:  mov      x1, #0x100                       
0x402900:  mov      x0, x3                           
0x402904:  bl       #0x401210                        ; <snprintf>
0x402908:  ldr      x0, [sp, #0x348]                 
0x40290c:  ldr      w0, [x0]                         
0x402910:  mov      w1, w0                           
0x402914:  add      x0, sp, #0x120                   
0x402918:  mov      w2, w1                           
0x40291c:  mov      x1, x0                           
0x402920:  ldr      x0, [sp, #0x340]                 
0x402924:  bl       #0x401350                        ; <cmsgRequestSel>
0x402928:  add      x3, sp, #0x220                   
0x40292c:  adrp     x0, #0x403000                    
0x402930:  add      x2, x0, #0xa90                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1"
0x402934:  mov      x1, #0x100                       
0x402938:  mov      x0, x3                           
0x40293c:  bl       #0x401210                        ; <snprintf>
0x402940:  add      x0, sp, #0x220                   
0x402944:  mov      x3, x0                           
0x402948:  mov      w2, #-0x40000000                 
0x40294c:  adrp     x0, #0x403000                    
0x402950:  add      x1, x0, #0xc70                   ; "DefaultConnectionService"
0x402954:  ldr      x0, [sp, #0x340]                 
0x402958:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x40295c:  add      x3, sp, #0x120                   
0x402960:  adrp     x0, #0x403000                    
0x402964:  add      x2, x0, #0xc90                   ; "InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding"
0x402968:  mov      x1, #0x100                       
0x40296c:  mov      x0, x3                           
0x402970:  bl       #0x401210                        ; <snprintf>
0x402974:  ldr      x0, [sp, #0x348]                 
0x402978:  ldr      w0, [x0]                         
0x40297c:  mov      w1, w0                           
0x402980:  add      x0, sp, #0x120                   
0x402984:  mov      w2, w1                           
0x402988:  mov      x1, x0                           
0x40298c:  ldr      x0, [sp, #0x340]                 
0x402990:  bl       #0x401350                        ; <cmsgRequestSel>
0x402994:  add      x3, sp, #0x220                   
0x402998:  adrp     x0, #0x403000                    
0x40299c:  add      x2, x0, #0xa90                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1"
0x4029a0:  mov      x1, #0x100                       
0x4029a4:  mov      x0, x3                           
0x4029a8:  bl       #0x401210                        ; <snprintf>
0x4029ac:  add      x0, sp, #0x220                   
0x4029b0:  mov      x3, x0                           
0x4029b4:  mov      w2, #-0x40000000                 
0x4029b8:  adrp     x0, #0x403000                    
0x4029bc:  add      x1, x0, #0xc70                   ; "DefaultConnectionService"
0x4029c0:  ldr      x0, [sp, #0x340]                 
0x4029c4:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4029c8:  add      x3, sp, #0x120                   
0x4029cc:  adrp     x0, #0x403000                    
0x4029d0:  add      x2, x0, #0xcc8                   ; "InternetGatewayDevice.ManagementServer"
0x4029d4:  mov      x1, #0x100                       
0x4029d8:  mov      x0, x3                           
0x4029dc:  bl       #0x401210                        ; <snprintf>
0x4029e0:  ldr      x0, [sp, #0x348]                 
0x4029e4:  ldr      w0, [x0]                         
0x4029e8:  mov      w1, w0                           
0x4029ec:  add      x0, sp, #0x120                   
0x4029f0:  mov      w2, w1                           
0x4029f4:  mov      x1, x0                           
0x4029f8:  ldr      x0, [sp, #0x340]                 
0x4029fc:  bl       #0x401350                        ; <cmsgRequestSel>
0x402a00:  add      x3, sp, #0x220                   
0x402a04:  adrp     x0, #0x403000                    
0x402a08:  add      x2, x0, #0xcf0                   ; "http://tms.airtelbroadband.in:8103"
0x402a0c:  mov      x1, #0x100                       
0x402a10:  mov      x0, x3                           
0x402a14:  bl       #0x401210                        ; <snprintf>
0x402a18:  add      x0, sp, #0x220                   
0x402a1c:  mov      x3, x0                           
0x402a20:  mov      w2, #-0x40000000                 
0x402a24:  adrp     x0, #0x403000                    
0x402a28:  add      x1, x0, #0xd18                   ; "URL"
0x402a2c:  ldr      x0, [sp, #0x340]                 
0x402a30:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402a34:  add      x0, sp, #0x326                   
0x402a38:  mov      x3, x0                           
0x402a3c:  mov      w2, #1                           
0x402a40:  movk     w2, #0x2000, lsl #16             
0x402a44:  adrp     x0, #0x403000                    
0x402a48:  add      x1, x0, #0xd20                   ; "X_5067F0_OverIPv6"
0x402a4c:  ldr      x0, [sp, #0x340]                 
0x402a50:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402a54:  add      x3, sp, #0x120                   
0x402a58:  adrp     x0, #0x403000                    
0x402a5c:  add      x2, x0, #0xd38                   ; "InternetGatewayDevice.X_5067F0_DeviceRecognition"
0x402a60:  mov      x1, #0x100                       
0x402a64:  mov      x0, x3                           
0x402a68:  bl       #0x401210                        ; <snprintf>
0x402a6c:  ldr      x0, [sp, #0x348]                 
0x402a70:  ldr      w0, [x0]                         
0x402a74:  mov      w1, w0                           
0x402a78:  add      x0, sp, #0x120                   
0x402a7c:  mov      w2, w1                           
0x402a80:  mov      x1, x0                           
0x402a84:  ldr      x0, [sp, #0x340]                 
0x402a88:  bl       #0x401350                        ; <cmsgRequestSel>
0x402a8c:  add      x0, sp, #0x326                   
0x402a90:  mov      x3, x0                           
0x402a94:  mov      w2, #1                           
0x402a98:  movk     w2, #0x2000, lsl #16             
0x402a9c:  adrp     x0, #0x403000                    
0x402aa0:  add      x1, x0, #0xa48                   ; "Enable"
0x402aa4:  ldr      x0, [sp, #0x340]                 
0x402aa8:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402aac:  ldr      x0, [sp, #0x348]                 
0x402ab0:  ldr      w0, [x0]                         
0x402ab4:  mov      w1, w0                           
0x402ab8:  ldr      x0, [sp, #0x340]                 
0x402abc:  bl       #0x401320                        ; <cmsgRequestSave>
0x402ac0:  mov      x2, #0xea60                      
0x402ac4:  ldr      w1, [sp, #0x33c]                 
0x402ac8:  ldr      x0, [sp, #0x340]                 
0x402acc:  bl       #0x401270                        ; <cmsgSendRecv>
0x402ad0:  str      x0, [sp, #0x358]                 
0x402ad4:  ldr      x0, [sp, #0x340]                 
0x402ad8:  cmp      x0, #0                           
0x402adc:  b.eq     #0x402ae8                        
0x402ae0:  ldr      x0, [sp, #0x340]                 
0x402ae4:  bl       #0x401470                        ; <cmsgFree>
0x402ae8:  ldr      x0, [sp, #0x358]                 
0x402aec:  cmp      x0, #0                           
0x402af0:  b.eq     #0x402afc                        
0x402af4:  ldr      x0, [sp, #0x358]                 
0x402af8:  bl       #0x401470                        ; <cmsgFree>
0x402afc:  str      wzr, [sp, #0x354]                
0x402b00:  b        #0x403508                        
0x402b04:  adrp     x0, #0x403000                    
0x402b08:  add      x1, x0, #0xd70                   ; "ETHER"
0x402b0c:  ldr      x0, [sp, #0x18]                  
0x402b10:  bl       #0x401300                        ; <strcmp>
0x402b14:  cmp      w0, #0                           
0x402b18:  b.ne     #0x403430                        
0x402b1c:  add      x3, sp, #0x120                   
0x402b20:  adrp     x0, #0x403000                    
0x402b24:  add      x2, x0, #0xb30                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1"
0x402b28:  mov      x1, #0x100                       
0x402b2c:  mov      x0, x3                           
0x402b30:  bl       #0x401210                        ; <snprintf>
0x402b34:  add      x0, sp, #0x120                   
0x402b38:  mov      w2, #1                           
0x402b3c:  mov      x1, x0                           
0x402b40:  ldr      x0, [sp, #0x348]                 
0x402b44:  bl       #0x401310                        ; <rdmGetObjectByName>
0x402b48:  str      x0, [sp, #0x328]                 
0x402b4c:  ldr      x0, [sp, #0x328]                 
0x402b50:  cmp      x0, #0                           
0x402b54:  b.ne     #0x402f10                        
0x402b58:  bl       #0x4012d0                        ; <cmsgCreateRequest>
0x402b5c:  str      x0, [sp, #0x340]                 
0x402b60:  ldr      x0, [sp, #0x340]                 
0x402b64:  cmp      x0, #0                           
0x402b68:  b.eq     #0x402ee0                        
0x402b6c:  ldr      x0, [sp, #0x348]                 
0x402b70:  ldr      w0, [x0]                         
0x402b74:  mov      w1, w0                           
0x402b78:  add      x0, sp, #0x120                   
0x402b7c:  mov      w2, w1                           
0x402b80:  mov      x1, x0                           
0x402b84:  ldr      x0, [sp, #0x340]                 
0x402b88:  bl       #0x401350                        ; <cmsgRequestSel>
0x402b8c:  mov      w1, #1                           
0x402b90:  ldr      x0, [sp, #0x340]                 
0x402b94:  bl       #0x4012f0                        ; <cmsgRequestSetIndexedObj>
0x402b98:  add      x0, sp, #0x326                   
0x402b9c:  mov      x3, x0                           
0x402ba0:  mov      w2, #1                           
0x402ba4:  movk     w2, #0x2000, lsl #16             
0x402ba8:  adrp     x0, #0x403000                    
0x402bac:  add      x1, x0, #0xa48                   ; "Enable"
0x402bb0:  ldr      x0, [sp, #0x340]                 
0x402bb4:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402bb8:  add      x3, sp, #0x220                   
0x402bbc:  adrp     x0, #0x403000                    
0x402bc0:  add      x2, x0, #0xd78                   ; "nas0_notag"
0x402bc4:  mov      x1, #0x100                       
0x402bc8:  mov      x0, x3                           
0x402bcc:  bl       #0x401210                        ; <snprintf>
0x402bd0:  add      x0, sp, #0x220                   
0x402bd4:  mov      x3, x0                           
0x402bd8:  mov      w2, #-0x40000000                 
0x402bdc:  adrp     x0, #0x403000                    
0x402be0:  add      x1, x0, #0xd88                   ; "X_5067F0_InterfaceName"
0x402be4:  ldr      x0, [sp, #0x340]                 
0x402be8:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402bec:  add      x3, sp, #0x220                   
0x402bf0:  adrp     x0, #0x403000                    
0x402bf4:  add      x2, x0, #0xda0                   ; "0.0.0.0"
0x402bf8:  mov      x1, #0x100                       
0x402bfc:  mov      x0, x3                           
0x402c00:  bl       #0x401210                        ; <snprintf>
0x402c04:  add      x0, sp, #0x220                   
0x402c08:  mov      x3, x0                           
0x402c0c:  mov      w2, #-0x40000000                 
0x402c10:  adrp     x0, #0x403000                    
0x402c14:  add      x1, x0, #0xda8                   ; "DefaultGateway"
0x402c18:  ldr      x0, [sp, #0x340]                 
0x402c1c:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402c20:  add      x3, sp, #0x220                   
0x402c24:  adrp     x0, #0x403000                    
0x402c28:  add      x2, x0, #0xdb8                   ; "TR069"
0x402c2c:  mov      x1, #0x100                       
0x402c30:  mov      x0, x3                           
0x402c34:  bl       #0x401210                        ; <snprintf>
0x402c38:  add      x0, sp, #0x220                   
0x402c3c:  mov      x3, x0                           
0x402c40:  mov      w2, #-0x40000000                 
0x402c44:  adrp     x0, #0x403000                    
0x402c48:  add      x1, x0, #0xdc0                   ; "X_5067F0_SERVICELIST"
0x402c4c:  ldr      x0, [sp, #0x340]                 
0x402c50:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402c54:  add      x3, sp, #0x220                   
0x402c58:  adrp     x0, #0x403000                    
0x402c5c:  add      x2, x0, #0xda0                   ; "0.0.0.0"
0x402c60:  mov      x1, #0x100                       
0x402c64:  mov      x0, x3                           
0x402c68:  bl       #0x401210                        ; <snprintf>
0x402c6c:  add      x0, sp, #0x220                   
0x402c70:  mov      x3, x0                           
0x402c74:  mov      w2, #-0x40000000                 
0x402c78:  adrp     x0, #0x403000                    
0x402c7c:  add      x1, x0, #0xdd8                   ; "SubnetMask"
0x402c80:  ldr      x0, [sp, #0x340]                 
0x402c84:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402c88:  add      x3, sp, #0x220                   
0x402c8c:  adrp     x0, #0x403000                    
0x402c90:  add      x2, x0, #0xda0                   ; "0.0.0.0"
0x402c94:  mov      x1, #0x100                       
0x402c98:  mov      x0, x3                           
0x402c9c:  bl       #0x401210                        ; <snprintf>
0x402ca0:  add      x0, sp, #0x220                   
0x402ca4:  mov      x3, x0                           
0x402ca8:  mov      w2, #-0x40000000                 
0x402cac:  adrp     x0, #0x403000                    
0x402cb0:  add      x1, x0, #0xde8                   ; "ExternalIPAddress"
0x402cb4:  ldr      x0, [sp, #0x340]                 
0x402cb8:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402cbc:  add      x3, sp, #0x220                   
0x402cc0:  adrp     x0, #0x403000                    
0x402cc4:  add      x2, x0, #0xe00                   ; "Eth_Internet"
0x402cc8:  mov      x1, #0x100                       
0x402ccc:  mov      x0, x3                           
0x402cd0:  bl       #0x401210                        ; <snprintf>
0x402cd4:  add      x0, sp, #0x220                   
0x402cd8:  mov      x3, x0                           
0x402cdc:  mov      w2, #-0x40000000                 
0x402ce0:  adrp     x0, #0x403000                    
0x402ce4:  add      x1, x0, #0xe10                   ; "Name"
0x402ce8:  ldr      x0, [sp, #0x340]                 
0x402cec:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402cf0:  add      x3, sp, #0x220                   
0x402cf4:  adrp     x0, #0x403000                    
0x402cf8:  add      x2, x0, #0xe18                   ; "N/A"
0x402cfc:  mov      x1, #0x100                       
0x402d00:  mov      x0, x3                           
0x402d04:  bl       #0x401210                        ; <snprintf>
0x402d08:  add      x0, sp, #0x220                   
0x402d0c:  mov      x3, x0                           
0x402d10:  mov      w2, #-0x40000000                 
0x402d14:  adrp     x0, #0x403000                    
0x402d18:  add      x1, x0, #0xe20                   ; "X_5067F0_RIPVersion"
0x402d1c:  ldr      x0, [sp, #0x340]                 
0x402d20:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402d24:  add      x0, sp, #0x326                   
0x402d28:  mov      x3, x0                           
0x402d2c:  mov      w2, #1                           
0x402d30:  adrp     x0, #0x403000                    
0x402d34:  add      x1, x0, #0xe38                   ; "X_5067F0_ExternalIPv6AddressPrefixLength"
0x402d38:  ldr      x0, [sp, #0x340]                 
0x402d3c:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402d40:  add      x0, sp, #0x327                   
0x402d44:  mov      x3, x0                           
0x402d48:  mov      w2, #1                           
0x402d4c:  movk     w2, #0x2000, lsl #16             
0x402d50:  adrp     x0, #0x403000                    
0x402d54:  add      x1, x0, #0xe68                   ; "X_5067F0_IPv6Enabled"
0x402d58:  ldr      x0, [sp, #0x340]                 
0x402d5c:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402d60:  add      x0, sp, #0x327                   
0x402d64:  mov      x3, x0                           
0x402d68:  mov      w2, #1                           
0x402d6c:  adrp     x0, #0x403000                    
0x402d70:  add      x1, x0, #0xe80                   ; "X_5067F0_DualStack"
0x402d74:  ldr      x0, [sp, #0x340]                 
0x402d78:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402d7c:  add      x0, sp, #0x326                   
0x402d80:  mov      x3, x0                           
0x402d84:  mov      w2, #1                           
0x402d88:  movk     w2, #0x2000, lsl #16             
0x402d8c:  adrp     x0, #0x403000                    
0x402d90:  add      x1, x0, #0xe98                   ; "X_5067F0_Enable_VLANID"
0x402d94:  ldr      x0, [sp, #0x340]                 
0x402d98:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402d9c:  add      x0, sp, #0x326                   
0x402da0:  mov      x3, x0                           
0x402da4:  mov      w2, #1                           
0x402da8:  movk     w2, #0x2000, lsl #16             
0x402dac:  adrp     x0, #0x403000                    
0x402db0:  add      x1, x0, #0xeb0                   ; "X_5067F0_IGMPEnabled"
0x402db4:  ldr      x0, [sp, #0x340]                 
0x402db8:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402dbc:  strh     wzr, [sp, #0x324]                
0x402dc0:  add      x0, sp, #0x324                   
0x402dc4:  mov      x3, x0                           
0x402dc8:  mov      w2, #2                           
0x402dcc:  adrp     x0, #0x403000                    
0x402dd0:  add      x1, x0, #0xec8                   ; "X_5067F0_VLANID"
0x402dd4:  ldr      x0, [sp, #0x340]                 
0x402dd8:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x402ddc:  add      x3, sp, #0x120                   
0x402de0:  adrp     x0, #0x403000                    
0x402de4:  add      x2, x0, #0xed8                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1.X_5067F0_DNS.1"
0x402de8:  mov      x1, #0x100                       
0x402dec:  mov      x0, x3                           
0x402df0:  bl       #0x401210                        ; <snprintf>
0x402df4:  ldr      x0, [sp, #0x348]                 
0x402df8:  ldr      w0, [x0]                         
0x402dfc:  mov      w1, w0                           
0x402e00:  add      x0, sp, #0x120                   
0x402e04:  mov      w2, w1                           
0x402e08:  mov      x1, x0                           
0x402e0c:  ldr      x0, [sp, #0x340]                 
0x402e10:  bl       #0x401350                        ; <cmsgRequestSel>
0x402e14:  mov      w1, #1                           
0x402e18:  ldr      x0, [sp, #0x340]                 
0x402e1c:  bl       #0x4012f0                        ; <cmsgRequestSetIndexedObj>
0x402e20:  add      x3, sp, #0x120                   
0x402e24:  adrp     x0, #0x403000                    
0x402e28:  add      x2, x0, #0xf38                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1.X_5067F0_DNS.2"
0x402e2c:  mov      x1, #0x100                       
0x402e30:  mov      x0, x3                           
0x402e34:  bl       #0x401210                        ; <snprintf>
0x402e38:  ldr      x0, [sp, #0x348]                 
0x402e3c:  ldr      w0, [x0]                         
0x402e40:  mov      w1, w0                           
0x402e44:  add      x0, sp, #0x120                   
0x402e48:  mov      w2, w1                           
0x402e4c:  mov      x1, x0                           
0x402e50:  ldr      x0, [sp, #0x340]                 
0x402e54:  bl       #0x401350                        ; <cmsgRequestSel>
0x402e58:  mov      w1, #1                           
0x402e5c:  ldr      x0, [sp, #0x340]                 
0x402e60:  bl       #0x4012f0                        ; <cmsgRequestSetIndexedObj>
0x402e64:  add      x3, sp, #0x120                   
0x402e68:  adrp     x0, #0x403000                    
0x402e6c:  add      x2, x0, #0xf98                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1.X_5067F0_DNS.3"
0x402e70:  mov      x1, #0x100                       
0x402e74:  mov      x0, x3                           
0x402e78:  bl       #0x401210                        ; <snprintf>
0x402e7c:  ldr      x0, [sp, #0x348]                 
0x402e80:  ldr      w0, [x0]                         
0x402e84:  mov      w1, w0                           
0x402e88:  add      x0, sp, #0x120                   
0x402e8c:  mov      w2, w1                           
0x402e90:  mov      x1, x0                           
0x402e94:  ldr      x0, [sp, #0x340]                 
0x402e98:  bl       #0x401350                        ; <cmsgRequestSel>
0x402e9c:  mov      w1, #1                           
0x402ea0:  ldr      x0, [sp, #0x340]                 
0x402ea4:  bl       #0x4012f0                        ; <cmsgRequestSetIndexedObj>
0x402ea8:  ldr      x0, [sp, #0x348]                 
0x402eac:  ldr      w0, [x0]                         
0x402eb0:  mov      w1, w0                           
0x402eb4:  ldr      x0, [sp, #0x340]                 
0x402eb8:  bl       #0x401320                        ; <cmsgRequestSave>
0x402ebc:  mov      x2, #0xea60                      
0x402ec0:  ldr      w1, [sp, #0x33c]                 
0x402ec4:  ldr      x0, [sp, #0x340]                 
0x402ec8:  bl       #0x401270                        ; <cmsgSendRecv>
0x402ecc:  str      x0, [sp, #0x358]                 
0x402ed0:  adrp     x0, #0x415000                    
0x402ed4:  add      x0, x0, #0x1b0                   
0x402ed8:  mov      w1, #1                           
0x402edc:  str      w1, [x0]                         
0x402ee0:  ldr      x0, [sp, #0x340]                 
0x402ee4:  cmp      x0, #0                           
0x402ee8:  b.eq     #0x402ef4                        
0x402eec:  ldr      x0, [sp, #0x340]                 
0x402ef0:  bl       #0x401470                        ; <cmsgFree>
0x402ef4:  ldr      x0, [sp, #0x358]                 
0x402ef8:  cmp      x0, #0                           
0x402efc:  b.eq     #0x402f08                        
0x402f00:  ldr      x0, [sp, #0x358]                 
0x402f04:  bl       #0x401470                        ; <cmsgFree>
0x402f08:  mov      w0, #1                           
0x402f0c:  str      w0, [sp, #0x354]                 
0x402f10:  mov      w1, #0                           
0x402f14:  adrp     x0, #0x403000                    
0x402f18:  add      x0, x0, #0xff8                   ; "/tmp/ADD_WAN_update_181DM_done"
0x402f1c:  bl       #0x4012e0                        ; <access>
0x402f20:  cmp      w0, #0                           
0x402f24:  b.eq     #0x402f50                        
0x402f28:  adrp     x0, #0x415000                    
0x402f2c:  add      x0, x0, #0x1b4                   
0x402f30:  ldr      w0, [x0]                         
0x402f34:  cmp      w0, #9                           
0x402f38:  b.gt     #0x402f50                        
0x402f3c:  adrp     x0, #0x415000                    
0x402f40:  add      x0, x0, #0x1b0                   
0x402f44:  ldr      w0, [x0]                         
0x402f48:  cmp      w0, #0                           
0x402f4c:  b.ne     #0x403408                        
0x402f50:  bl       #0x4012d0                        ; <cmsgCreateRequest>
0x402f54:  str      x0, [sp, #0x340]                 
0x402f58:  ldr      x0, [sp, #0x340]                 
0x402f5c:  cmp      x0, #0                           
0x402f60:  b.eq     #0x4033d8                        
0x402f64:  add      x3, sp, #0x120                   
0x402f68:  adrp     x0, #0x403000                    
0x402f6c:  add      x2, x0, #0x9c0                   ; "InternetGatewayDevice.X_5067F0_Ext.WANSwitch"
0x402f70:  mov      x1, #0x100                       
0x402f74:  mov      x0, x3                           
0x402f78:  bl       #0x401210                        ; <snprintf>
0x402f7c:  ldr      x0, [sp, #0x348]                 
0x402f80:  ldr      w0, [x0]                         
0x402f84:  mov      w1, w0                           
0x402f88:  add      x0, sp, #0x120                   
0x402f8c:  mov      w2, w1                           
0x402f90:  mov      x1, x0                           
0x402f94:  ldr      x0, [sp, #0x340]                 
0x402f98:  bl       #0x401350                        ; <cmsgRequestSel>
0x402f9c:  add      x3, sp, #0x220                   
0x402fa0:  adrp     x0, #0x403000                    
0x402fa4:  add      x2, x0, #0xd70                   ; "ETHER"
0x402fa8:  mov      x1, #0x100                       
0x402fac:  mov      x0, x3                           
0x402fb0:  bl       #0x401210                        ; <snprintf>
0x402fb4:  add      x0, sp, #0x220                   
0x402fb8:  mov      x3, x0                           
0x402fbc:  mov      w2, #-0x40000000                 
0x402fc0:  adrp     x0, #0x403000                    
0x402fc4:  add      x1, x0, #0x9f0                   ; "WANMode"
0x402fc8:  ldr      x0, [sp, #0x340]                 
0x402fcc:  bl       #0x401330                        ; <cmsgRequestSet>
0x402fd0:  add      x3, sp, #0x120                   
0x402fd4:  adrp     x0, #0x403000                    
0x402fd8:  add      x2, x0, #0xa08                   ; "InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig"
0x402fdc:  mov      x1, #0x100                       
0x402fe0:  mov      x0, x3                           
0x402fe4:  bl       #0x401210                        ; <snprintf>
0x402fe8:  ldr      x0, [sp, #0x348]                 
0x402fec:  ldr      w0, [x0]                         
0x402ff0:  mov      w1, w0                           
0x402ff4:  add      x0, sp, #0x120                   
0x402ff8:  mov      w2, w1                           
0x402ffc:  mov      x1, x0                           
0x403000:  ldr      x0, [sp, #0x340]                 
0x403004:  bl       #0x401350                        ; <cmsgRequestSel>
0x403008:  add      x0, sp, #0x326                   
0x40300c:  mov      x3, x0                           
0x403010:  mov      w2, #1                           
0x403014:  movk     w2, #0x2000, lsl #16             
0x403018:  adrp     x0, #0x403000                    
0x40301c:  add      x1, x0, #0xa48                   ; "Enable"
0x403020:  ldr      x0, [sp, #0x340]                 
0x403024:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x403028:  add      x3, sp, #0x120                   
0x40302c:  adrp     x0, #0x403000                    
0x403030:  add      x2, x0, #0xa50                   ; "InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig"
0x403034:  mov      x1, #0x100                       
0x403038:  mov      x0, x3                           
0x40303c:  bl       #0x401210                        ; <snprintf>
0x403040:  ldr      x0, [sp, #0x348]                 
0x403044:  ldr      w0, [x0]                         
0x403048:  mov      w1, w0                           
0x40304c:  add      x0, sp, #0x120                   
0x403050:  mov      w2, w1                           
0x403054:  mov      x1, x0                           
0x403058:  ldr      x0, [sp, #0x340]                 
0x40305c:  bl       #0x401350                        ; <cmsgRequestSel>
0x403060:  add      x0, sp, #0x327                   
0x403064:  mov      x3, x0                           
0x403068:  mov      w2, #1                           
0x40306c:  movk     w2, #0x2000, lsl #16             
0x403070:  adrp     x0, #0x403000                    
0x403074:  add      x1, x0, #0xa48                   ; "Enable"
0x403078:  ldr      x0, [sp, #0x340]                 
0x40307c:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x403080:  add      x3, sp, #0x120                   
0x403084:  adrp     x0, #0x403000                    
0x403088:  add      x2, x0, #0xa90                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1"
0x40308c:  mov      x1, #0x100                       
0x403090:  mov      x0, x3                           
0x403094:  bl       #0x401210                        ; <snprintf>
0x403098:  ldr      x0, [sp, #0x348]                 
0x40309c:  ldr      w0, [x0]                         
0x4030a0:  mov      w1, w0                           
0x4030a4:  add      x0, sp, #0x120                   
0x4030a8:  mov      w2, w1                           
0x4030ac:  mov      x1, x0                           
0x4030b0:  ldr      x0, [sp, #0x340]                 
0x4030b4:  bl       #0x401350                        ; <cmsgRequestSel>
0x4030b8:  add      x0, sp, #0x326                   
0x4030bc:  mov      x3, x0                           
0x4030c0:  mov      w2, #1                           
0x4030c4:  movk     w2, #0x2000, lsl #16             
0x4030c8:  adrp     x0, #0x403000                    
0x4030cc:  add      x1, x0, #0xa48                   ; "Enable"
0x4030d0:  ldr      x0, [sp, #0x340]                 
0x4030d4:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4030d8:  add      x3, sp, #0x120                   
0x4030dc:  adrp     x0, #0x403000                    
0x4030e0:  add      x2, x0, #0xae0                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1"
0x4030e4:  mov      x1, #0x100                       
0x4030e8:  mov      x0, x3                           
0x4030ec:  bl       #0x401210                        ; <snprintf>
0x4030f0:  ldr      x0, [sp, #0x348]                 
0x4030f4:  ldr      w0, [x0]                         
0x4030f8:  mov      w1, w0                           
0x4030fc:  add      x0, sp, #0x120                   
0x403100:  mov      w2, w1                           
0x403104:  mov      x1, x0                           
0x403108:  ldr      x0, [sp, #0x340]                 
0x40310c:  bl       #0x401350                        ; <cmsgRequestSel>
0x403110:  add      x0, sp, #0x326                   
0x403114:  mov      x3, x0                           
0x403118:  mov      w2, #1                           
0x40311c:  movk     w2, #0x2000, lsl #16             
0x403120:  adrp     x0, #0x403000                    
0x403124:  add      x1, x0, #0xa48                   ; "Enable"
0x403128:  ldr      x0, [sp, #0x340]                 
0x40312c:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x403130:  add      x3, sp, #0x120                   
0x403134:  adrp     x0, #0x403000                    
0x403138:  add      x2, x0, #0xb30                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1"
0x40313c:  mov      x1, #0x100                       
0x403140:  mov      x0, x3                           
0x403144:  bl       #0x401210                        ; <snprintf>
0x403148:  ldr      x0, [sp, #0x348]                 
0x40314c:  ldr      w0, [x0]                         
0x403150:  mov      w1, w0                           
0x403154:  add      x0, sp, #0x120                   
0x403158:  mov      w2, w1                           
0x40315c:  mov      x1, x0                           
0x403160:  ldr      x0, [sp, #0x340]                 
0x403164:  bl       #0x401350                        ; <cmsgRequestSel>
0x403168:  add      x0, sp, #0x327                   
0x40316c:  mov      x3, x0                           
0x403170:  mov      w2, #1                           
0x403174:  movk     w2, #0x2000, lsl #16             
0x403178:  adrp     x0, #0x403000                    
0x40317c:  add      x1, x0, #0xa48                   ; "Enable"
0x403180:  ldr      x0, [sp, #0x340]                 
0x403184:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x403188:  add      x3, sp, #0x120                   
0x40318c:  adrp     x0, #0x403000                    
0x403190:  add      x2, x0, #0xb80                   ; "InternetGatewayDevice.LANDevice.1.X_5067F0_IPv6LANHostConfigManagement.NDPPD"
0x403194:  mov      x1, #0x100                       
0x403198:  mov      x0, x3                           
0x40319c:  bl       #0x401210                        ; <snprintf>
0x4031a0:  ldr      x0, [sp, #0x348]                 
0x4031a4:  ldr      w0, [x0]                         
0x4031a8:  mov      w1, w0                           
0x4031ac:  add      x0, sp, #0x120                   
0x4031b0:  mov      w2, w1                           
0x4031b4:  mov      x1, x0                           
0x4031b8:  ldr      x0, [sp, #0x340]                 
0x4031bc:  bl       #0x401350                        ; <cmsgRequestSel>
0x4031c0:  add      x0, sp, #0x327                   
0x4031c4:  mov      x3, x0                           
0x4031c8:  mov      w2, #1                           
0x4031cc:  movk     w2, #0x2000, lsl #16             
0x4031d0:  adrp     x0, #0x403000                    
0x4031d4:  add      x1, x0, #0xbd0                   ; "Enabled"
0x4031d8:  ldr      x0, [sp, #0x340]                 
0x4031dc:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4031e0:  add      x3, sp, #0x120                   
0x4031e4:  adrp     x0, #0x403000                    
0x4031e8:  add      x2, x0, #0xbd8                   ; "InternetGatewayDevice.LANDevice.1.X_5067F0_IPv6LANHostConfigManagement.IPv6PDWanConnection"
0x4031ec:  mov      x1, #0x100                       
0x4031f0:  mov      x0, x3                           
0x4031f4:  bl       #0x401210                        ; <snprintf>
0x4031f8:  ldr      x0, [sp, #0x348]                 
0x4031fc:  ldr      w0, [x0]                         
0x403200:  mov      w1, w0                           
0x403204:  add      x0, sp, #0x120                   
0x403208:  mov      w2, w1                           
0x40320c:  mov      x1, x0                           
0x403210:  ldr      x0, [sp, #0x340]                 
0x403214:  bl       #0x401350                        ; <cmsgRequestSel>
0x403218:  add      x3, sp, #0x220                   
0x40321c:  adrp     x0, #0x403000                    
0x403220:  add      x2, x0, #0xb30                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1"
0x403224:  mov      x1, #0x100                       
0x403228:  mov      x0, x3                           
0x40322c:  bl       #0x401210                        ; <snprintf>
0x403230:  add      x0, sp, #0x220                   
0x403234:  mov      x3, x0                           
0x403238:  mov      w2, #-0x40000000                 
0x40323c:  adrp     x0, #0x403000                    
0x403240:  add      x1, x0, #0xc38                   ; "Interface"
0x403244:  ldr      x0, [sp, #0x340]                 
0x403248:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x40324c:  add      x3, sp, #0x120                   
0x403250:  adrp     x0, #0x403000                    
0x403254:  add      x2, x0, #0xc48                   ; "InternetGatewayDevice.Layer3Forwarding"
0x403258:  mov      x1, #0x100                       
0x40325c:  mov      x0, x3                           
0x403260:  bl       #0x401210                        ; <snprintf>
0x403264:  ldr      x0, [sp, #0x348]                 
0x403268:  ldr      w0, [x0]                         
0x40326c:  mov      w1, w0                           
0x403270:  add      x0, sp, #0x120                   
0x403274:  mov      w2, w1                           
0x403278:  mov      x1, x0                           
0x40327c:  ldr      x0, [sp, #0x340]                 
0x403280:  bl       #0x401350                        ; <cmsgRequestSel>
0x403284:  add      x3, sp, #0x220                   
0x403288:  adrp     x0, #0x403000                    
0x40328c:  add      x2, x0, #0xb30                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1"
0x403290:  mov      x1, #0x100                       
0x403294:  mov      x0, x3                           
0x403298:  bl       #0x401210                        ; <snprintf>
0x40329c:  add      x0, sp, #0x220                   
0x4032a0:  mov      x3, x0                           
0x4032a4:  mov      w2, #-0x40000000                 
0x4032a8:  adrp     x0, #0x403000                    
0x4032ac:  add      x1, x0, #0xc70                   ; "DefaultConnectionService"
0x4032b0:  ldr      x0, [sp, #0x340]                 
0x4032b4:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4032b8:  add      x3, sp, #0x120                   
0x4032bc:  adrp     x0, #0x403000                    
0x4032c0:  add      x2, x0, #0xc90                   ; "InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding"
0x4032c4:  mov      x1, #0x100                       
0x4032c8:  mov      x0, x3                           
0x4032cc:  bl       #0x401210                        ; <snprintf>
0x4032d0:  ldr      x0, [sp, #0x348]                 
0x4032d4:  ldr      w0, [x0]                         
0x4032d8:  mov      w1, w0                           
0x4032dc:  add      x0, sp, #0x120                   
0x4032e0:  mov      w2, w1                           
0x4032e4:  mov      x1, x0                           
0x4032e8:  ldr      x0, [sp, #0x340]                 
0x4032ec:  bl       #0x401350                        ; <cmsgRequestSel>
0x4032f0:  add      x3, sp, #0x220                   
0x4032f4:  adrp     x0, #0x403000                    
0x4032f8:  add      x2, x0, #0xb30                   ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1"
0x4032fc:  mov      x1, #0x100                       
0x403300:  mov      x0, x3                           
0x403304:  bl       #0x401210                        ; <snprintf>
0x403308:  add      x0, sp, #0x220                   
0x40330c:  mov      x3, x0                           
0x403310:  mov      w2, #-0x40000000                 
0x403314:  adrp     x0, #0x403000                    
0x403318:  add      x1, x0, #0xc70                   ; "DefaultConnectionService"
0x40331c:  ldr      x0, [sp, #0x340]                 
0x403320:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x403324:  add      x3, sp, #0x120                   
0x403328:  adrp     x0, #0x403000                    
0x40332c:  add      x2, x0, #0xcc8                   ; "InternetGatewayDevice.ManagementServer"
0x403330:  mov      x1, #0x100                       
0x403334:  mov      x0, x3                           
0x403338:  bl       #0x401210                        ; <snprintf>
0x40333c:  ldr      x0, [sp, #0x348]                 
0x403340:  ldr      w0, [x0]                         
0x403344:  mov      w1, w0                           
0x403348:  add      x0, sp, #0x120                   
0x40334c:  mov      w2, w1                           
0x403350:  mov      x1, x0                           
0x403354:  ldr      x0, [sp, #0x340]                 
0x403358:  bl       #0x401350                        ; <cmsgRequestSel>
0x40335c:  add      x3, sp, #0x220                   
0x403360:  adrp     x0, #0x404000                    
0x403364:  add      x2, x0, #0x18                    ; "http://testacs.airtelbroadband.in:8103/"
0x403368:  mov      x1, #0x100                       
0x40336c:  mov      x0, x3                           
0x403370:  bl       #0x401210                        ; <snprintf>
0x403374:  add      x0, sp, #0x220                   
0x403378:  mov      x3, x0                           
0x40337c:  mov      w2, #-0x40000000                 
0x403380:  adrp     x0, #0x403000                    
0x403384:  add      x1, x0, #0xd18                   ; "URL"
0x403388:  ldr      x0, [sp, #0x340]                 
0x40338c:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x403390:  add      x0, sp, #0x327                   
0x403394:  mov      x3, x0                           
0x403398:  mov      w2, #1                           
0x40339c:  movk     w2, #0x2000, lsl #16             
0x4033a0:  adrp     x0, #0x403000                    
0x4033a4:  add      x1, x0, #0xd20                   ; "X_5067F0_OverIPv6"
0x4033a8:  ldr      x0, [sp, #0x340]                 
0x4033ac:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4033b0:  ldr      x0, [sp, #0x348]                 
0x4033b4:  ldr      w0, [x0]                         
0x4033b8:  mov      w1, w0                           
0x4033bc:  ldr      x0, [sp, #0x340]                 
0x4033c0:  bl       #0x401320                        ; <cmsgRequestSave>
0x4033c4:  mov      x2, #0xea60                      
0x4033c8:  ldr      w1, [sp, #0x33c]                 
0x4033cc:  ldr      x0, [sp, #0x340]                 
0x4033d0:  bl       #0x401270                        ; <cmsgSendRecv>
0x4033d4:  str      x0, [sp, #0x358]                 
0x4033d8:  ldr      x0, [sp, #0x340]                 
0x4033dc:  cmp      x0, #0                           
0x4033e0:  b.eq     #0x4033ec                        
0x4033e4:  ldr      x0, [sp, #0x340]                 
0x4033e8:  bl       #0x401470                        ; <cmsgFree>
0x4033ec:  ldr      x0, [sp, #0x358]                 
0x4033f0:  cmp      x0, #0                           
0x4033f4:  b.eq     #0x403400                        
0x4033f8:  ldr      x0, [sp, #0x358]                 
0x4033fc:  bl       #0x401470                        ; <cmsgFree>
0x403400:  str      wzr, [sp, #0x354]                
0x403404:  b        #0x403508                        
0x403408:  adrp     x0, #0x415000                    
0x40340c:  add      x0, x0, #0x1b4                   
0x403410:  ldr      w0, [x0]                         
0x403414:  add      w1, w0, #1                       
0x403418:  adrp     x0, #0x415000                    
0x40341c:  add      x0, x0, #0x1b4                   
0x403420:  str      w1, [x0]                         
0x403424:  mov      w0, #1                           
0x403428:  str      w0, [sp, #0x354]                 
0x40342c:  b        #0x403508                        
0x403430:  adrp     x0, #0x404000                    
0x403434:  add      x1, x0, #0x40                    ; "DISABLE"
0x403438:  ldr      x0, [sp, #0x18]                  
0x40343c:  bl       #0x401300                        ; <strcmp>
0x403440:  cmp      w0, #0                           
0x403444:  b.ne     #0x403508                        
0x403448:  bl       #0x4012d0                        ; <cmsgCreateRequest>
0x40344c:  str      x0, [sp, #0x340]                 
0x403450:  ldr      x0, [sp, #0x340]                 
0x403454:  cmp      x0, #0                           
0x403458:  b.eq     #0x4034dc                        
0x40345c:  add      x3, sp, #0x120                   
0x403460:  adrp     x0, #0x403000                    
0x403464:  add      x2, x0, #0x9c0                   ; "InternetGatewayDevice.X_5067F0_Ext.WANSwitch"
0x403468:  mov      x1, #0x100                       
0x40346c:  mov      x0, x3                           
0x403470:  bl       #0x401210                        ; <snprintf>
0x403474:  ldr      x0, [sp, #0x348]                 
0x403478:  ldr      w0, [x0]                         
0x40347c:  mov      w1, w0                           
0x403480:  add      x0, sp, #0x120                   
0x403484:  mov      w2, w1                           
0x403488:  mov      x1, x0                           
0x40348c:  ldr      x0, [sp, #0x340]                 
0x403490:  bl       #0x401350                        ; <cmsgRequestSel>
0x403494:  add      x0, sp, #0x326                   
0x403498:  mov      x3, x0                           
0x40349c:  mov      w2, #1                           
0x4034a0:  movk     w2, #0x2000, lsl #16             
0x4034a4:  adrp     x0, #0x403000                    
0x4034a8:  add      x1, x0, #0x9f8                   ; "WanAutoDetect"
0x4034ac:  ldr      x0, [sp, #0x340]                 
0x4034b0:  bl       #0x401190                        ; <cmsgRequestSetNoBE>
0x4034b4:  ldr      x0, [sp, #0x348]                 
0x4034b8:  ldr      w0, [x0]                         
0x4034bc:  mov      w1, w0                           
0x4034c0:  ldr      x0, [sp, #0x340]                 
0x4034c4:  bl       #0x401320                        ; <cmsgRequestSave>
0x4034c8:  mov      x2, #0xea60                      
0x4034cc:  ldr      w1, [sp, #0x33c]                 
0x4034d0:  ldr      x0, [sp, #0x340]                 
0x4034d4:  bl       #0x401270                        ; <cmsgSendRecv>
0x4034d8:  str      x0, [sp, #0x358]                 
0x4034dc:  ldr      x0, [sp, #0x340]                 
0x4034e0:  cmp      x0, #0                           
0x4034e4:  b.eq     #0x4034f0                        
0x4034e8:  ldr      x0, [sp, #0x340]                 
0x4034ec:  bl       #0x401470                        ; <cmsgFree>
0x4034f0:  ldr      x0, [sp, #0x358]                 
0x4034f4:  cmp      x0, #0                           
0x4034f8:  b.eq     #0x403504                        
0x4034fc:  ldr      x0, [sp, #0x358]                 
0x403500:  bl       #0x401470                        ; <cmsgFree>
0x403504:  str      wzr, [sp, #0x354]                
0x403508:  adrp     x0, #0x403000                    
0x40350c:  add      x0, x0, #0x998                   ; "linkdetection_rtk"
0x403510:  bl       #0x401260                        ; <cmsgUnRegisterModule>
0x403514:  ldr      x0, [sp, #0x348]                 
0x403518:  cmp      x0, #0                           
0x40351c:  b.eq     #0x403528                        
0x403520:  ldr      x0, [sp, #0x348]                 
0x403524:  bl       #0x401390                        ; <rdmDeInit>
0x403528:  ldr      w0, [sp, #0x354]                 
0x40352c:  ldp      x29, x30, [sp]                   
0x403530:  add      sp, sp, #0x360                   
0x403534:  ret                                       