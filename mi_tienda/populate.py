from app import app, db, Product

def populate_products():
    productos = [
        # Bimbo
        {
            "supplier": "Bimbo",
            "name": "Mantecadas Vainilla",
            "description": "Deliciosas mantecadas sabor vainilla, suaves y esponjosas.",
            "price_cents": 3500,
            "image": "mantecadas_vainilla_625g.jpg",
            "brand": "Bimbo",
            "weight": "625g",
            "ingredients": "Harina de trigo, azúcar, huevo, aceite vegetal, saborizante de vainilla.",
            "allergens": "Gluten, huevo",
            "nutritional_info": "Energía: 350kcal por porción. Grasas: 15g. Azúcares: 20g.",
            "stock": 20
        },
        {
            "supplier": "Bimbo",
            "name": "Pan Blanco Grande",
            "description": "Pan blanco suave, ideal para sándwiches y tostadas.",
            "price_cents": 2800,
            "image": "pan_blanco_680g.jpg",
            "brand": "Bimbo",
            "weight": "680g",
            "ingredients": "Harina de trigo, agua, levadura, sal, azúcar.",
            "allergens": "Gluten",
            "nutritional_info": "Energía: 250kcal por porción. Fibra: 2g.",
            "stock": 30
        },
        {
            "supplier": "Bimbo",
            "name": "Donas Azucaradas",
            "description": "Donas cubiertas de azúcar, perfectas para acompañar tu café.",
            "price_cents": 3200,
            "image": "donas_azucaradas_6p.jpg",
            "brand": "Bimbo",
            "weight": "6 piezas",
            "ingredients": "Harina de trigo, azúcar, huevo, aceite vegetal.",
            "allergens": "Gluten, huevo",
            "nutritional_info": "Energía: 400kcal por porción. Azúcares: 22g.",
            "stock": 15
        },
        {
            "supplier": "Bimbo",
            "name": "Roles Canela",
            "description": "Roles de canela con glaseado dulce.",
            "price_cents": 4000,
            "image": "roles_canela_4p.jpg",
            "brand": "Bimbo",
            "weight": "4 piezas",
            "ingredients": "Harina de trigo, azúcar, canela, huevo, aceite vegetal.",
            "allergens": "Gluten, huevo",
            "nutritional_info": "Energía: 420kcal por porción. Azúcares: 24g.",
            "stock": 10
        },
        {
            "supplier": "Bimbo",
            "name": "Pan Integral",
            "description": "Pan integral saludable, fuente de fibra.",
            "price_cents": 3000,
            "image": "pan_integral_680g.jpg",
            "brand": "Bimbo",
            "weight": "680g",
            "ingredients": "Harina integral de trigo, agua, levadura, sal.",
            "allergens": "Gluten",
            "nutritional_info": "Energía: 220kcal por porción. Fibra: 5g.",
            "stock": 25
        },
        # Gamesa
        {
            "supplier": "Gamesa",
            "name": "Galletas Marías",
            "description": "Galletas clásicas Marías, perfectas para acompañar leche o café.",
            "price_cents": 1500,
            "image": "galletas_marias_170g.jpg",
            "brand": "Gamesa",
            "weight": "170g",
            "ingredients": "Harina de trigo, azúcar, huevo, aceite vegetal.",
            "allergens": "Gluten, huevo",
            "nutritional_info": "Energía: 120kcal por porción. Azúcares: 8g.",
            "stock": 40
        },
        {
            "supplier": "Gamesa",
            "name": "Galletas Emperador Chocolate",
            "description": "Galletas rellenas de chocolate, crujientes y deliciosas.",
            "price_cents": 2200,
            "image": "galletas_emperador_100g.jpg",
            "brand": "Gamesa",
            "weight": "100g",
            "ingredients": "Harina de trigo, azúcar, cacao, aceite vegetal.",
            "allergens": "Gluten",
            "nutritional_info": "Energía: 150kcal por porción. Azúcares: 10g.",
            "stock": 35
        },
        {
            "supplier": "Gamesa",
            "name": "Galletas Arcoiris",
            "description": "Galletas con chispas de colores, divertidas y sabrosas.",
            "price_cents": 2000,
            "image": "galletas_arcoiris_120g.jpg",
            "brand": "Gamesa",
            "weight": "120g",
            "ingredients": "Harina de trigo, azúcar, colorantes, aceite vegetal.",
            "allergens": "Gluten",
            "nutritional_info": "Energía: 130kcal por porción. Azúcares: 9g.",
            "stock": 20
        },
        {
            "supplier": "Gamesa",
            "name": "Galletas Saladitas",
            "description": "Galletas saladas crujientes, ideales para botanas.",
            "price_cents": 1800,
            "image": "galletas_saladitas_150g.jpg",
            "brand": "Gamesa",
            "weight": "150g",
            "ingredients": "Harina de trigo, sal, aceite vegetal.",
            "allergens": "Gluten",
            "nutritional_info": "Energía: 110kcal por porción. Sodio: 200mg.",
            "stock": 25
        },
        {
            "supplier": "Gamesa",
            "name": "Galletas Chokis",
            "description": "Galletas con chispas de chocolate, favoritas de todos.",
            "price_cents": 2500,
            "image": "galletas_chokis_90g.jpg",
            "brand": "Gamesa",
            "weight": "90g",
            "ingredients": "Harina de trigo, azúcar, chispas de chocolate.",
            "allergens": "Gluten",
            "nutritional_info": "Energía: 160kcal por porción. Azúcares: 12g.",
            "stock": 30
        },
        # Sabritas
        {
            "supplier": "Sabritas",
            "name": "Papas Clásicas",
            "description": "Papas fritas clásicas, crujientes y saladas.",
            "price_cents": 1800,
            "image": "papas_clasicas_45g.jpg",
            "brand": "Sabritas",
            "weight": "45g",
            "ingredients": "Papa, aceite vegetal, sal.",
            "allergens": "",
            "nutritional_info": "Energía: 150kcal por porción. Grasas: 10g.",
            "stock": 50
        },
        {
            "supplier": "Sabritas",
            "name": "Cheetos",
            "description": "Botana de maíz con queso, sabor intenso.",
            "price_cents": 1700,
            "image": "cheetos_40g.jpg",
            "brand": "Sabritas",
            "weight": "40g",
            "ingredients": "Maíz, queso, aceite vegetal.",
            "allergens": "Lácteos",
            "nutritional_info": "Energía: 140kcal por porción. Grasas: 8g.",
            "stock": 45
        },
        {
            "supplier": "Sabritas",
            "name": "Doritos Nacho",
            "description": "Totopos de maíz sabor nacho, perfectos para compartir.",
            "price_cents": 1900,
            "image": "doritos_nacho_52g.jpg",
            "brand": "Sabritas",
            "weight": "52g",
            "ingredients": "Maíz, queso, especias, aceite vegetal.",
            "allergens": "Lácteos",
            "nutritional_info": "Energía: 160kcal por porción. Grasas: 9g.",
            "stock": 40
        },
        {
            "supplier": "Sabritas",
            "name": "Ruffles Queso",
            "description": "Papas onduladas sabor queso, extra crujientes.",
            "price_cents": 2100,
            "image": "ruffles_queso_45g.jpg",
            "brand": "Sabritas",
            "weight": "45g",
            "ingredients": "Papa, queso, aceite vegetal.",
            "allergens": "Lácteos",
            "nutritional_info": "Energía: 170kcal por porción. Grasas: 11g.",
            "stock": 35
        },
        {
            "supplier": "Sabritas",
            "name": "Papas Adobadas",
            "description": "Papas fritas sabor adobadas, con especias mexicanas.",
            "price_cents": 2000,
            "image": "papas_adobadas_45g.jpg",
            "brand": "Sabritas",
            "weight": "45g",
            "ingredients": "Papa, especias, aceite vegetal.",
            "allergens": "",
            "nutritional_info": "Energía: 155kcal por porción. Grasas: 10g.",
            "stock": 30
        }
    ]

    with app.app_context():
        db.create_all()
        for prod in productos:
            existe = Product.query.filter_by(name=prod["name"], supplier=prod["supplier"]).first()
            if not existe:
                db.session.add(Product(**prod))
        db.session.commit()
        print("Productos reales agregados correctamente.")

if __name__ == "__main__":
    populate_products()