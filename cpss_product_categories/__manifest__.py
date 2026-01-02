{ 
    "name": "CPSS Product Categories",
    "version": "18.0.1.0.0",
    "summary": "Ajoute une arborescence de catégories produits pour magasin agricole",
    "description": "Module simple pour charger une classification de catégories et sous-catégories de produits agricoles (Produits phytosanitaires, Engrais, Semences, Matériel, Irrigation, Élevage, Outillage, Divers).",
    "author": "CPSS",
    "website": "https://cpss.com",
    "category": "Inventory/Products",
    "license": "LGPL-3",
    "depends": ["product", "point_of_sale"],
    "data": [
        "data/product_category_data.xml",
        "data/product_category_data_pos.xml"
    ],
    "installable": True,
    "application": False,
    "auto_install": False
}
