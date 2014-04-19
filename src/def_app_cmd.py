# -*- coding: Utf-8 -*-

# Importations des modules de la bibliotheque standard

# Importations des modules des bibliotheques tierces


class CommandAction(object):

    @staticmethod
    def open_csv():
        print("Ouverture d'une fichier CVS")

    @staticmethod
    def open_html():
        print("Ouverture d'un fichier HTML")

    @staticmethod
    def open_sgdb():
        print("Ouverture d'une base de données")

    @staticmethod
    def open_txt_utf8():
        print("Ouverture d'un fichier texte UTF8")

    @staticmethod
    def open_txt_latin9():
        print("Ouverture d'un fichier texte latin9")

    @staticmethod
    def save_file():
        print("Enregistrement du fichier")

    @staticmethod
    def save_file_as():
        print("Enregistrement du fichier sous un autre nom")

    @staticmethod
    def close_file():
        quit()

    @staticmethod
    def show_properties_file():
        print("Affichage des propriétés du fichier")


if __name__ == "__main__":
    action = CommandAction.__dict__['show_properties_file']
    action()
