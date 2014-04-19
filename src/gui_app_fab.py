# -*- coding: Utf-8 -*-

### Importations des modules de la bibliotheque standard
import tkinter as tk
import abc
import xml.etree.ElementTree as ET

### Importations des modules des bibliotheques tierces


### Importations des modules du projet
from def_app_cmd import *

### Déclarations de constantes
GUI_STRUCT_PATH = "./xml/gui_structure.xml" # ~ structure de l'interface

### Déclarations des classes
class XmlFunc:
    
    __rootUrl = GUI_STRUCT_PATH
    
    @staticmethod
    def get_xml_elt(theObject, xmlRoot = None):
        """
        Fonction retournant un objet xml de type Element.
        -- xmlRoot : type string - path d'un fichier xml, ou,
                     contenu xml '<a>...<b>...</b></a>'
        """
        # Obtention du document XML de description des structures
        if not theObject.__rootUrl : theObject.__rootUrl = GUI_STRUCT_PATH
        if not xmlRoot :
            return ET.parse(theObject.__rootUrl).getroot()
        elif type(xmlRoot) == str :
            try :
                return ET.fromstring(xmlRoot)
            except :
                try :
                    return ET.parse(xmlRoot).getroot()
                except :
                    raise ValueError('L\'argument passé de valeur %s et de type %s'
                                     ' n\'est pas supporté' % 
                                     (str(xmlRoot), type(xmlRoot)))
    
    @staticmethod
    def get_xml_root(theObject, xmlElt = None):
        """
        Fonction retournant une chaîne de caractère xml.
        -- xmlElt : type objet ET.Element
        """
        if not theObject.__rootUrl : theObject.__rootUrl = GUI_STRUCT_PATH
        if not xmlElt :
            xmlElt = ET.parse(theObject.__rootUrl).getroot()
        
        if type(xmlElt) == ET.Element :
            try :
                return ET.tostring(xmlElt, method='xml', encoding='unicode')
            except :
                raise ValueError('L\'argument passé de valeur %s et de type %s'
                                 ' n\'est pas supporté' % 
                                 (str(xmlElt), type(xmlElt)))
    
     ## Propriétés / Fonctions décoreés
    @property
    def rootUrl(self):
        """
        Obtenir l'URL du fichier xml décrivant l'interface utilisateur.
        """
        if not XmlFunc.__rootUrl:
            self.__rootUrl = GUI_STRUCT_PATH
        return XmlFunc.__rootUrl
    @rootUrl.setter
    def rootUrl(self, url):
        """Fixer une URL de fichier xml décrivant l'interface utilisateur."""
        print(url)
        self.__rootUrl = url
        print(self.__rootUrl)
        
    @property
    def myProps(self):
        """Obtient les options décoratives de l'objet depuis un type Element"""
        if not self._myProps:
            myEltOpt = self.myElt.find('./options')
            self._myProps = {props : val.lower() for props, val \
                             in myEltOpt.items()}
        return self._myProps
    @myProps.setter
    def myProps(self, theProps):
        self._myProp = theProps
        
    @property
    def myPos(self):
        """Obtient les options décoratives de l'objet depuis un type Element"""
        if not self._myPos:
            myEltPac = self.myElt.find('./pack')
            self._myPos = {pos : val.lower() for pos, val \
                           in myEltPac.items()}
        return self._myPos
    @myPos.setter
    def myPos(self, thePos):
        self._myPos = thePos

class BarFactory(tk.Frame, XmlFunc, metaclass=abc.ABCMeta):
    """
    Fabrique de barres applicatives :
    -- barre de menus
    -- barre d'outils
    -- barre de status
    """
    ## Emplacements des variables d'instance
    __slots__ = ['myType', 'myElt', 'name', 'xmlDoc', '_myProps', '_myPos', \
                 'itemOrder', 'itemList']
    
    # État d'initialisation de l'objet
    initialized = False
    ## Associations {typeBar : classBar}
    _class_assoc = {'menu' : 'Menu', 'status' : 'Status', 'tools' : 'Tools'}
    
    ## Constructeur
    def __new__(cls, master, name, xmlDoc = None, url = None):
        """Retourne une instance de barre applicative du type demandé."""
        XmlFunc._XmlFunc__rootUrl = url
        print('rootUrl %s' % cls._XmlFunc__rootUrl)
        cls.myElt = XmlFunc.get_xml_elt(cls, xmlDoc).\
                    find('./bar[@label="%s"]' % name)
        cls.myType = 'Bar' + cls._class_assoc[cls.myElt.get('type')]
        try:
            oInst = object.__new__( \
            {c.__name__ : c for c in cls.__subclasses__()}[cls.myType])
            return oInst
        except :
            print('Impossible d\'instancier la classe %s' % cls.myType)
            return False
    
    def __init__(self, master, name, xmlDoc = None, url = None):
        """Initialisation et lancement de la construction de l'objet."""
        tk.Frame.__init__(self, master)
        # Mémorisation des propriétés de base de l'objet barre
        self.name = name
        self.master = master
        self.__release(self, self.myType) # Initialisation des propriétés objet

    ## Fonction internes cachées
    @staticmethod
    def __release(oInst, theType=None):
        """Fonction d'initialisation des propriétés."""
        if not oInst.initialized:
            oInst.itemOrder = []    # Ensemble ordonné des éléments de la barre
            oInst.itemList = {'itemOrder':oInst.itemOrder}
            oInst.myType = theType  # Réaf => id(cls.myType) <> id(self.myType)
            oInst.xmlDoc = XmlFunc.get_xml_root(oInst, oInst.myElt)
            oInst._myProps = {}     # Options décoratives (Widget options)
            oInst._myPos = {}       # Options de positionnement
            oInst.rootUrl = oInst.rootUrl
        else:
            oInst.__class__.myType = theType
        oInst.initialized = True
        
    def _build(self):
        """Construction des éléments génériques de la barre."""
        self.config(**self.myProps) # Application des options décoratives
        # Parcours des Elts composants la barre
        mySubElts = self.myElt.findall('./item')
        for anElt in mySubElts:
            self.itemOrder.append(anElt.get('label'))
            self._build_item(anElt)
        self.pack(**self.myPos)
        self.__release(self) # Ré-initialisation des propriétés de classe

    ## Méthodes abstraites
    
    @abc.abstractmethod
    def _build_item(self, theElt):
        return
        
class BarMenu(BarFactory):
    """
    Barre de menu.
    """    
    def _build_item(self, theElt):
        theMenub  = MenuButton(self, theElt)
        self.itemList[theElt.get('label')] = theMenub

        
class MenuButton(XmlFunc, tk.Menubutton):
    """
    Bouton de menu.
    """
    ## Emplacements des variables d'instance
    __slots__ = ['myElt', 'name', 'xmlDoc', '_myProps', '_myPos', \
                 'itemOrder']
    # État d'initialisation de l'objet
    initialized = False
    
    def __init__(self, master, theElt):
        self.myElt = theElt
        self.name = theElt.get('label')
        tk.Menubutton.__init__(self, master, text=self.name)
        self.__release(self, "MenuButton")
        self._build()
        
    ## Fonctions internes cachées
     
    @staticmethod
    def __release(oInst, theType=None):
        """Fonction d'initialisation des propriétés."""
        if not oInst.initialized:
            oInst._myProps = {}     # Options décoratives (Widget options)
            oInst._myPos = {}       # Options de positionnement
            oInst.myType = theType
            oInst.xmlDoc = XmlFunc.get_xml_root(oInst, oInst.myElt)
            oInst.initialized = True
        else:
            pass
    
    def _build(self):
        theElt = XmlFunc.get_xml_elt(self).find('./menu[@label="%s"]' % self.name)
        theMenu = MenuFactory(self, theElt, 'menu')
        self.configure(menu=theMenu)
        self.config(**self.myProps)
        self.pack(**self.myPos)
        
        
class MenuFactory(XmlFunc, metaclass=abc.ABCMeta):
    """
    Fabrique de menu retournant soit un (sous-)menu ou une commande de menu.
    """        
    ## Emplacements des variables d'instance
    __slots__ = ['myType', 'myElt', 'name', 'xmlDoc', '_myProps', '_myPos', \
                 'itemOrder', 'master']
    # État d'initialisation de l'objet
    initialized = False

    ## Associations {typeItem : classItem}
    _class_assoc = {'menu' : 'Menu', 'command' : 'CommandItem'}
    
    ## Constructeur
    def __new__(cls, master, theElt, theType = None):
        """Retourne une instance d'item de menu [(sub-)menu | command]"""
        cls.myElt = theElt
        if not theType:
            cls.myType = cls._class_assoc[cls.myElt.get('type')]
        else:
            cls.myType = cls._class_assoc[theType]
        try:
            oInst = object.__new__( \
            {c.__name__ : c for c in cls.__subclasses__()}[cls.myType])
            return oInst
        except :
            print('Impossible d\'instancier la classe %s' % cls.myType)
            return False
    
    def __init__(self, master, theElt, theType = None):
        """Initialisation et lancement de la construction de l'objet."""
        # Mémorisation des propriétés de base de l'objet
        self.name = theElt.get('label')
        self.master = master
        self.__release(self, self.myType) # Initialisation des propriétés objet
        self._build()        # Construction de l'objet
        self.__release(self) # Ré-initialisation des propriétés de classe
    
    ## Fonction internes cachées
    @staticmethod
    def __release(oInst, theType=None):
        """Fonction d'initialisation des propriétés."""
        if not oInst.initialized:
            oInst.itemOrder = []     # Ensemble ordonné des éléments du menu
            oInst.itemList = {'itemOrder':oInst.itemOrder}
            oInst.myType = theType  # Réaf => id(cls.myType) <> id(self.myType)
            oInst.xmlDoc = XmlFunc.get_xml_root(oInst, oInst.myElt)
            oInst._myProps = {}     # Options décoratives (Widget options)
            oInst._myPos = {}       # Options de positionnement
            oInst.rootUrl = oInst.rootUrl
        else:
            oInst.__class__.myType = theType
        oInst.initialized = True
        
    def _build(self):
        """Construction des éléments génériques du menu."""
        self._build_item(self.master)

    ## Méthodes abstraites
    
    @abc.abstractmethod
    def _build_item(self, theElt):
        return

class Menu(MenuFactory, tk.Menu):
    """
    Element composite constitué de sous-menu et de commandes.
    Fait un appel à MenuFactory pour lancer la récursivité.
    """
    def __init__(self, master, theElt, theType = None):
        tk.Menu.__init__(self, master)
        MenuFactory.__init__(self, master, theElt, theType)
        
    def _build_item(self, master):
        self.config(**self.myProps)
        # Parcours des Elts composants le menu
        mySubElts = self.myElt.findall('./item')
        for anElt in mySubElts:
            hisName = anElt.get('label')
            hisType = None
            if anElt.get('type') == 'menu':
                # Programmation de la récursivité
                anElt = XmlFunc.get_xml_elt(self).\
                        find('./menu[@label="%s"]' % hisName)
                hisType = 'menu'
            theItem = MenuFactory(self, anElt, hisType)
            self.itemOrder.append(hisName)
            self.itemList[hisName] = theItem
        if master.__class__.__name__ == "Menu" :
            master.add_cascade(label=self.name, menu=self)

class CommandItem(MenuFactory):
    """
    Element terminal du menu : commande.
    """
    def __init__(self, master, theElt, theType = None):
        MenuFactory.__init__(self, master, theElt, theType)
    
    def _build_item(self, master):
        myActionName = self.myElt.find('./command').get('value')
        myAction = CommandAction.__dict__[myActionName]
        master.add_command(label=self.name, command=myAction)
    
if __name__ == "__main__":
    tkRoot = tk.Tk()
    menuBar = BarFactory(tkRoot, "Barre de menus principale", url="./xml/gui_structure_2.xml")
    menuBar._build()
    menuBar2 = BarFactory(tkRoot, "Barre de menus principale", url="")
    menuBar2._build()
    tkRoot.mainloop()        
