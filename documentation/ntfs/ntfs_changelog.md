# Changelog du format NTFS

* Version 0.1 du 15/12/2014 : 
    * Ajout de la gestion des codes externes et des propriétés complémentaires génériques par objet
* Version 0.2 du 20/02/2015 :
    * Ajout des heures d'ouverture et de fermeture de la ligne
    * Ajout du taux d'émission de CO2 par mode physique et de la liste exhaustive des modes physiques
    * Ajout du type de circulation (fichier trips) pour permettre de spécifier le type de TAD
    * Ajout du fichier admin_stations.txt
    * Ajout de la gestion du TAD Zonal 
        * Ajout d'une URL dans le fichier odt_conditions.txt
        * Ajout dans le fichier stops.txt des zones géographiques et du type de zone
    * Ajout de 2 fichiers sur la gestion des propriétés complémentaires sur les objets
* Version 0.3 du 14/04/2015 :
    * Modification de la gestion du TAD : suppression des zones de TAD arrêt à arrêt
    * Modification du nom de fichier companies.txt
    * Remplacement de la géométrie dans le fichier stops.txt par une liaison vers le fichier de géométries
    * Ajout des modes BSS, car et bike pour la consommation de CO2 des modes de rabattement
    * Ajout d'un fichier feed_infos
    * Création du fichier comment_links pour associer plusieurs commentaires à un objet; inclusion du TAD dans les comment (avec un type) et ajout d'une URL
    * Ajout d'un champ stop_time_id optionnel pour permettre la liaison entre les notes et les horaires
    * Modification des fichiers object_codes et object_properties pour harmoniser le format (séparation de l'id et du type d'objet)
    * Suppression des champs "external_code" car à inclure dans object_codes
* Version 0.4 du 27/04/2015 :
    * Ajout d'une destination principale à la notion de parcours
    * Ajout de la notion de groupe de ligne
* Version 0.5 du 25/10/2015 (version technique, pas de modification effective de format)
    * Gestion du champ line_text_color
    * Gestion du fichier equipments.txt
