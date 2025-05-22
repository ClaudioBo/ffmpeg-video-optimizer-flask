# Configuración de Samba
Comandos nomas para copiar y pegar que hueva jaja  
La verdad no se si esto esta bien configurado idk  
```sh
sudo apt install samba -y
sudo nano /etc/samba/smb.conf
```
Agregar esto hasta el final y guardar
```toml
[Optimizador]
   path = /mnt/media/optimizador
   browseable = yes
   writable = yes
   guest ok = yes
   force user = root
   force group = root
```
```sh
# previamente tener montado el disco en /mnt/media (o cambia la ruta como quieras, idk)
sudo mkdir /mnt/media/optimizador
sudo chown -R nobody:nogroup /mnt/media/optimizador
sudo chmod -R 0775 /mnt/media/optimizador
sudo service smbd restart
```
Ir a Windows -> `Este equipo` -> Clic derecho -> `Agregar una ubicación de red` -> Siguiente hasta que pida una ruta, la cual es:
```yml
\\IP_DEL_SERVIDOR\Optimizador
```