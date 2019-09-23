# DeepMeta
Ce projet à pour but de construire des modèles de segmentation automatique d'images IRM pour la détection des poumons et
métastases pulmonaires dans le cas du petit animal, la souris. 

Les méthodes utilisées pour ce projet sont issues du Deep Learning.

## Données
Les données sont des images IRM 3D 128x128x128 voxels, acquises par le RMSB, et représentent l'état de la maladie d'une souris 
à un instant donné. 

Les images peuvent être visualiser à l'aide du logiciel Fiji et sous différents axes (axial, coronal ou sagittal). 
Elles ont été acquises suivant le plan axial mais nous les avons traitées dans le sens coronal => meilleur visualisation des poumons.

Il est possible de définir trois types d'image : 
* Souris saine : aucune métastase présente dans les poumons.
* Souris en début de maladie : plusieurs petites métastases présentes dans les poumons.
* Souris en fin de maladie : de grosses métastases matures présentes dans les poumons.

Nous disposons en tout de : 
* 87 images de souris = 11136 slices. 
* 27 souris annotées pour la segmentation des poumons => 2128 slices présentants des poumons. 
* 8 souris annotées pour la segmentation des métastases => 620 slices présentants des poumons et 387 d'entres elles présentent des métastases

## Projet
Le dossier du projet est disponible sur /mnt/cbib/Projet_Detection_Metastase_Souris. Pour le récuperer : 

```
scp -r adresse_connexion_serveur_ssh:/mnt/cbib/Projet_Detection_Metastase_Souris chemin_ou_le_placer/
```

L'architecture de ce dossier est la suivante : 

*Projet_Detection_Metastase_Souris*
* Antoine_Git : 
  * Ensemble des script python (présentés dans la partie suivante) 
  * Poumons et Métastases : les modèles construits, résultats de segmentation et statistique sur les résultats.
* Data : L'ensemble des données brutes acquis par le RMSB contenant deux groupes de souris iL34_1c et LacZ.
* DATA : 
* Data_contraste
* Poumon_sain_seg
* Annotation_Meta


## Scripts 

* main.py
* model.py
* utils.py
* data.py
* Cnn-Lstm.py
* creative_meta.py
* filtre_debruiteur.py
* modif_jeu_data.py
* qualite.py
* stats_seg_poum_meta.py
* tab_csv.py
* train_model_poum.py
* train_model_meta.py
* Validation_croisee.py
* visualize.py
* weighted.py

### Avec console Python

J'ai construits l'ensemble de mes scripts avec la console python sur Pycharm ou Jupyter. 

Pour utiliser les scripts sur Pycharm, il suffit de spécifier le path (commenter) dans le main.py : 
```
ROOT_DIR = os.path.abspath("le_chemin_d'acces_en_entier/Projet_Detection_Metastase_Souris/") 
```

### Avec terminal
Pour lancer les script, il faut se placer dans le dossier Projet_Detection_Metastase_Souris puis lancer le script désiré : 
```
cd le_chemin_d'acces/Projet_Detection_Metastase_Souris
```
```
python main.py
```


