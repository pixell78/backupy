# Backupy - Versão 2.0

**TERMINALX - SOLUÇÕES OPEN SOURCE**  
**Bruno Carvalho - Diretor Tecnológico**  
- Email: bruno@terminalx.net.br  
- WhatsApp: +55 35 984413336  

## Descrição
Este script gera backups do sistema de arquivos em diferentes locais:

- Backup local - HD ou partição local
- Backup em rede local - Em algum compartilhamento de arquivo ou NAS local
- Backup em VPN - Em alguma rede remota via túnel OpenVPN, é necessário ter um servidor OpenVpn na ponta para receber o backup.

Requisitos para o funcionamento:
- OpenVpn Ok.
- Rsync Ok.
- Chave ssh compartilhada para acesso sem senha.

Utilizando o programa "rsync"+"OpenVPN"+"SSH", podemos fazer cópias incrementais dos estados das estruturas de diretórios e sincronizar com as atualizações diárias. Além das camadas de segurança do túnel criptografado, ainda temos a conexão segura do SSH.

Após o backup ser feito, um email é enviado ao Sysadmin.
