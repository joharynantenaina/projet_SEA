#!/bin/bash

#========================== FONCTION ============================
nettoyage()
{
	clear
	mem_avant=$(df / | awk 'NR==2 {print $3}')
	#cherche tout les fichier temporaire, cache, et corbeille qui ont été la depui plus de 7 jours
	find /tmp /var/tmp ~/.local/share/Trash -type f -mtime +7 -exec rm -i {} \; #2> /dev/null
	#recherche de tout fichier de journal compressé qui peuvent occuper la memoire 
	find /var/log -name "*.gz" -type f -exec rm -i {} \; #2> /dev/null
	#vidage du trash
	rm -ri ~/.local/share/Trash/* #2> /dev/null
	apt clean #2> /dev/null
	apt autoremove -y #2> /dev/null
	recuperer=$((($mem_avant - $(df / | awk 'NR==2 {print $3}')) / $mem_avant * 100))
	if (( $(echo "$recuperer > 0" | bc -l) ))
	then
		echo "espace libérer : $recuperer%"
	else
		echo -e "\e[1;31mrien n'as été éffacer...\e[0m"
	fi
	read
}

attenuation()
{
	clear
	charge_cpu=$(top -bn1 | grep "%Cpu" | awk '{print 100 - $8}')
	charge_avant=$charge_cpu
	charge_cpu=${charge_cpu/,/.}
	echo -e "charge_cpu = \e[1m$charge_cpu%\e[0m"
	charge_avant=${Charge_avant/,/.}
	if (( $(echo "$charge_cpu > 50" | bc -l) ))
	then
		echo la charge actuel du cpu: $charge_cpu
		while (( $(echo "$charge_cpu > 50" | bc -l) ))
		do
			#recuperation du pid qui a la charge la plus haut
			cpu=$(top -bn1 -u=$USER | awk 'NR==8 {print $1}')
			kill -9 $cpu 2> /dev/null
			#reevaluation de la charge
			charge_cpu=$(top -bn1 | grep "%Cpu" | awk '{print 100 - $8}')
			charge_cpu=${charge_cpu/,/.}
			echo cpu=$charge_cpu
		done
		charge_actuel=$(top -bn1 | grep "%Cpu" | awk '{print 100 - $8}')
		charge_actuel=${charge_actuel/,/.}
		echo "la charge actuel : $charge_actuel"
		liberer=$(echo "$charge_avant - $charge_actuel" | bc)
		echo "la charge liberer : $liberer"
	else 
		echo "Le cpu n'est pas chargée"
	fi
	read
}

configuration_espace()
{
	clear
	read -p "Quelle est votre nom de group:" group
	addgroup $group
	read -p "Quelle est votre espace de travail:" workspace
	chown :$group $workspace
	chmod 770 $workspace
	echo "Tout les operation son fait..."
	echo "Maintenant, vous pouvez travailler tranquil"
	read
}


configuration_env()
{
	clear
	read -p "Quelle est le nom de votre variable d'environnement:" env
	read -p "Quelle est sa valuer:" value
	echo $env = $value
	read
	echo "export $env=$value" >> ~/.bashrc
	echo "Operation reussit"
	echo "Maintenant, vous pouvez travailler tranquil"
	read
}

#========================= \FONCTION ============================

#teste si le programme a été lancer par root ou non
if [ "$EUID" -ne 0 ]; then
    echo -e "\e[1;31mCe programme doit être exécuté en tant que root.\e[0m"
    exit 1
fi

clear
compt=0

echo -e "\e[1;32m=========================================\e[0m"
echo -e "\e[1;32mRECUPERATION ET INITIALISATION DU SYSTEME\e[0m"
echo -e "\e[1;32m=========================================\e[0m\n"
echo -e "\e[1;31mMENU:\e[0m"
echo -e "	\e[1m1\e[0m.Mission de nettoyage du système de fichiers\n	\e[1m2\e[0m.Atténuation des processus indésirables\n	\e[1m3\e[0m.Configuration de l'espace de travail sécurisé\n	\e[1m4\e[0m.Configuration de l'environnement de développement"
read -p "Entrez votre choix:" choix

while [[ ! $choix =~ ^[0-9]+$ ]];
do
	if [ $compt -ge 3 ];
	then
		exit		
	fi
	echo $choix
	read -p "Entrez votre choix:" choix
	((compt++))
done

case "$choix" in
	1)
		nettoyage
		;;
	2)
		attenuation
		;;
	3)
		configuration_espace
		;;
	4)
		configuration_env
		;;
	*)
		;;
esac


