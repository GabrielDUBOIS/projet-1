# -*- coding: Utf-8 -*-

# Importations des modules de la bibliotheque standard

# Importations des modules des bibliotheques tierces


class CommandAction(object):

    def open_csv(self=None):
        print("Ouverture d'une fichier CVS")

    def open_html(self=None):
        print("Ouverture d'un fichier HTML")

    def open_sgdb(self=None):
        print("Ouverture d'une base de données")

    def open_txt_utf8(self=None):
        print("Ouverture d'un fichier texte UTF8")

    def open_txt_latin9(self=None):
        print("Ouverture d'un fichier texte latin9")

    def save_file(self=None):
        print("Enregistrement du fichier")

    def save_file_as(self=None):
        print("Enregistrement du fichier sous un autre nom")

    def close_file(self=None):
        quit()

    def show_properties_file(self=None):
        print("Affichage des propriétés du fichier")


if __name__ == "__main__":
    action = CommandAction.__dict__['show_properties_file']
    action()
