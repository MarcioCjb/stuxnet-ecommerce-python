# executar esse código adiciona itens no BD

import random
from banco import Banco
from modelos import criar_produto

banco = Banco()

componentes = {
    "Placas mãe": ((400, 1500), ["ASUS ROG STRIX B650", "Gigabyte B550 AORUS", "MSI MAG B760 Tomahawk", "ASRock B450M Pro4", "Biostar B450MH", "ASUS Prime H610M"]),
    "Memória RAM": ((100, 1000), ["Corsair Vengeance 16GB DDR4", "Kingston Fury 8GB DDR4", "G.Skill Trident Z 32GB DDR5", "Patriot Viper 16GB DDR5", "Crucial 16GB DDR4 3200", "TeamGroup T-Force 8GB DDR4"]),
    "Armazenamento": ((150, 1500), ["SSD Kingston NV2 1TB", "SSD Crucial P3 500GB", "HD Seagate Barracuda 2TB", "SSD Samsung 980 1TB", "SSD WD Green 480GB", "SSD ADATA XPG 2TB"]),
    "Refrigeração": ((80, 800), ["Cooler Hyper 212 Black", "Water cooler 240mm", "Cooler DeepCool AK400", "Water cooler 360mm RGB", "Cooler Noctua NH-U12S", "Pasta térmica Arctic MX-4"]),
    "Monitores": ((600, 3000), ["Monitor AOC 24G2 165Hz", 'Monitor LG UltraGear 27"', "Monitor Samsung Odyssey G5", "Monitor Dell 24 IPS", "Monitor Gigabyte G27Q", "Monitor Philips 23.8 Full HD"]),
    "Periféricos": ((40, 800), ["Teclado Redragon Kumara", "Mouse Logitech G203", "Headset HyperX Cloud II", "Mousepad Razer Goliathus", "Teclado Logitech K120", "Webcam Logitech C920"]),
}

total = 0
for categoria, (faixa, produtos) in componentes.items():
    for nome in produtos:
        preco = round(random.uniform(*faixa), 2)
        quantidade = random.randint(0, 30)
        banco.cadastrar_produto(criar_produto(categoria, nome=nome, preco=preco, quantidade=quantidade))

        total += 1

        print(f"{categoria:<14} | {nome:<30} | R$ {preco:>8.2f} | {quantidade} un")

print(f"\n{total} produtos adicionados.")
