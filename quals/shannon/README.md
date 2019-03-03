### Overview

This directory contains the tasks for Shannon qualification game. Every task
has a checker in `$TASK/checker.py`. See [`README`](../../README.md) in project
root for checker interface and general instructions.

### VirtualBox image

[`Shannon_20150406.ova.zip`](http://download.cdn.yandex.net/root4/Shannon_20150406.ova.zip), key: 9af1565b9937f693ecefdaf5e90b2683

### Tasks

1. [`SSL`](01_ssl)
Here is a private key and a certificate for a CA to generate your certificate:

 ```
 -----BEGIN RSA PRIVATE KEY-----
 MIICXAIBAAKBgQCjKwGnBHUwQtTzLb5uhrh+eRRAQyQwGzCg+n4XWzt8M+iX/OGx
 4QCG4GjKhi9Nqzhm41+AjPB5cndU3Oe5j1LrcvWvxe2n15FG7hPSLG5dHe97pzpj
 KVma8OkcrUc6WWIccZ48FlV21ZCeUFukthtqEDDEEw1CxEnwHgIydnynlwIDAQAB
 AoGADTAfrREmK6VrMtCCsMpAxTAiG+ORXDYGYyx73oVoNGy5ovc0gr0N3tjqf1wD
 HML3BxHfmTNLCHXhAUHtlMjpya7kkJELurrFgEQ9gkcdogcf8Iw/J6GjBpJG2WlX
 vVL4zEiYw0T5TULGI54Iest0ZQx88EX8r+6x1jI668RHCtECQQDYUPLf2K/0FUyk
 csXoKq1ECseSVpfhG5NITqsLOc93jh3xAQFYtSuM7E3CeHkP+ZoKY/SGd9QkWrhd
 QQFoGL5vAkEAwRoCwNqlUWwTVayGdgw/D/mxtFelKRYl8kj50MeMraBqHM/ijXZt
 +wF5exUmuPio+nF64UIqLA1VCYhnqJ49WQJAL3DJY0hdhnVpYqN9PeamK0cF79Un
 6AmpKnF+V67tDjZP4LwstGy/SV/FygGr41IFc4Pqa9c54mM3DdSk31SV5wJAHW9f
 mBI8PQsib17bKEd5nW/MfNcXYAn2QtaI7iBc+2KGilnOCQ5SeX6iC/cPbgbJi1Od
 DZVOZGSr38YhNvzYEQJBALoFJQEg6Xj44ClcJFIjbA+xyipk4h5JcmGvpUeKfaKF
 EBSJMECLR8wIa5XUkeRuM30JhTkd0s3WPUFaoBAvcvs=
 -----END RSA PRIVATE KEY-----

 -----BEGIN CERTIFICATE-----
 MIIDHzCCAoigAwIBAgIJALEwbIlKhnreMA0GCSqGSIb3DQEBBQUAMGkxCzAJBgNV
 BAYTAlJVMQ8wDQYDVQQIEwZNb3Njb3cxDzANBgNVBAcTBk1vc2NvdzEPMA0GA1UE
 ChMGWWFuZGV4MQ0wCwYDVQQLEwRSb290MRgwFgYDVQQDEw9yb290LnlhbmRleC5j
 b20wHhcNMTUwNDA2MTY0MzA5WhcNMTYwNDA1MTY0MzA5WjBpMQswCQYDVQQGEwJS
 VTEPMA0GA1UECBMGTW9zY293MQ8wDQYDVQQHEwZNb3Njb3cxDzANBgNVBAoTBllh
 bmRleDENMAsGA1UECxMEUm9vdDEYMBYGA1UEAxMPcm9vdC55YW5kZXguY29tMIGf
 MA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCjKwGnBHUwQtTzLb5uhrh+eRRAQyQw
 GzCg+n4XWzt8M+iX/OGx4QCG4GjKhi9Nqzhm41+AjPB5cndU3Oe5j1LrcvWvxe2n
 15FG7hPSLG5dHe97pzpjKVma8OkcrUc6WWIccZ48FlV21ZCeUFukthtqEDDEEw1C
 xEnwHgIydnynlwIDAQABo4HOMIHLMB0GA1UdDgQWBBQG+ykV13EVW9XxCTncLjLV
 YVX83TCBmwYDVR0jBIGTMIGQgBQG+ykV13EVW9XxCTncLjLVYVX83aFtpGswaTEL
 MAkGA1UEBhMCUlUxDzANBgNVBAgTBk1vc2NvdzEPMA0GA1UEBxMGTW9zY293MQ8w
 DQYDVQQKEwZZYW5kZXgxDTALBgNVBAsTBFJvb3QxGDAWBgNVBAMTD3Jvb3QueWFu
 ZGV4LmNvbYIJALEwbIlKhnreMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQAD
 gYEAmvNk8iAbV4+YMq/9oxkMeB6RxLs9m6jhYyAPuAI/dUhWSX+D+BnRcbsHWK4r
 a9G/riM1zerb5BD1apMz3faON2ydFJGB0thjlgr/KXfgaUXjp15QslEhsyhZIgEB
 Tak+0BQkkh5+cFAvJhGCZqajr6m2I8Dix3mF3Ey7nSx1GDU=
 -----END CERTIFICATE-----
 ```

2. [`MariaDB repair`](02_mariadb)
There is a MariaDB database in /var/lib/mysql. We had access there with login 'checker' and password 'masterkey', but something went wrong. Please fix it.
BTW, the `data` table structure was:

 ```
 +-------+---------+------+-----+---------+-------+
 | Field | Type    | Null | Key | Default | Extra |
 +-------+---------+------+-----+---------+-------+
 | name  | text    | YES  |     | NULL    |       |
 | hits  | int(11) | YES  |     | NULL    |       |
 | size  | int(11) | YES  |     | NULL    |       |
 +-------+---------+------+-----+---------+-------+
 ```

3. [`Binary`](03_mono)
Run 1.exe

4. [`Mongo`](04_mongo)
There is a database in /var/lib/db.tar.gz.
Make a root.features collection with 2 shards and make it available on the standard port.

5. [`Strange protocol`](05_rudp)
Set up an echo server on port 13000.

6. [`File`](06_lvm_btrfs)
There is a /root/file inside your image. Find a good root.txt file and make it available via http://image_ip/root.txt

7. [`MariaDB tuning`](07_tuning)
The repaired MariaDB is slow. Tune it up.

8. [`HG`](08_hg)
There is a HG repository in /root/repo.
Drop all .gz files in all revisions and make it available via http://ip:8000/

9. [`Strange file`](09_strange_file)
We got a strange file in ~tester/file. No one can change it. Fix it.
