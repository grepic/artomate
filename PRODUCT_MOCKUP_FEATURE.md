# 🎨 Funkce realistických náhledů produktů - jako Printify

## Nová funkcionalita

Aplikace nyní podporuje **nahrání vlastního designu/loga** a zobrazení **reálných náhledů** na všech produktech - stejně jako to funguje v Printify!

## Co je nové?

### 1. Nahrání vlastního designu 📤
- Nahrajte PNG nebo JPG logo/vzor
- Podporuje transparentní pozadí (PNG s alfa kanálem)
- Automatické uložení do `data/assets/uploads/`

### 2. Živé náhledy na produktech 👁️
- Váš design se automaticky zobrazí na všech produktech
- Reálné mockup obrázky z `data/mockups/`
- Inteligentní umístění designu podle typu produktu:
  - **Oblečení**: design na hrudi (trika, mikiny)
  - **Nástěnné umění**: design vyplní rám (plakáty, plátna)
  - **Hrnky**: design na přední straně
  - **Polštáře & deky**: centrovaný design
  - **Doplňky**: optimalizované umístění

### 3. Výběr z vygenerovaných obrázků 🖼️
- Pokud jste vygenerovali více variant, můžete mezi nimi přepínat
- Miniatury pro rychlý výběr
- Okamžitá aktualizace náhledů

### 4. Smart cropping & scaling 🎯
- Automatické ořezání designu podle poměru stran produktu
- Inteligentní škálování podle typu pokrytí:
  - `transparent`: průhledné pozadí (trička, topy)
  - `full`: celoplošný tisk (plakáty, deky)
  - `centered`: centrovaný design (hrnky, tašky)

## Jak to použít

### Krok 1: Přejděte na "📦 Create Products"
```
Sidebar → 📦 Create Products
```

### Krok 2: Nahrajte svůj design
```
🎨 Nahrajte vlastní design nebo logo
[Vyberte obrázek (PNG, JPG)]
```

### Krok 3: Vyberte produkty
- Uvidíte váš design na každém produktu v reálném čase
- Produkty jsou seskupené podle kategorií
- Checkboxy pro výběr produktů

### Krok 4: Vytvořte produkty
```
🏭 Vytvořit všechny vybrané produkty
```

## Technické detaily

### Composite funkce
```python
composite_design_on_mockup(mockup_path, design_image_path, product_spec)
```

**Parametry:**
- `mockup_path`: cesta k mockup obrázku produktu
- `design_image_path`: cesta k uploadnutému/vybranému designu
- `product_spec`: specifikace produktu (print area, coverage type, etc.)

**Návratová hodnota:**
- PNG bytes pro base64 kódování a zobrazení v HTML

### Mockup konfigurace

Každý typ produktu má specifickou konfiguraci:
```python
mockup_configs = {
    'tshirt': {'scale': 0.20, 'pos_x': 0.5, 'pos_y': 0.40},
    'poster': {'scale': 0.65, 'pos_x': 0.5, 'pos_y': 0.5},
    'mug': {'scale': 0.22, 'pos_x': 0.42, 'pos_y': 0.45},
    # ... další
}
```

- **scale**: velikost designu relativně k mockupu (0.2 = 20%)
- **pos_x, pos_y**: pozice středu designu (0.5 = střed)

### RenderEngine integrace

Využívá `RenderEngine` pro:
- Smart cropping designu na správný aspect ratio
- Škálování na cílové rozměry
- Zachování průhlednosti (RGBA vs RGB)
- 300 DPI kvalita pro tisk

## Příklady použití

### 1. Logo na tričku
```
1. Nahrajte logo (PNG s průhledným pozadím)
2. Vyberte "Unisex Tričko"
3. Logo se zobrazí na hrudi
```

### 2. Vzor na plakát
```
1. Nahrajte vzor/artwork
2. Vyberte "Plakát 18×24"
3. Vzor vyplní celý rám
```

### 3. Design na hrnek
```
1. Nahrajte menší design/ikonu
2. Vyberte "Hrnek 11oz"
3. Design se zobrazí na přední straně
```

## Výhody oproti předchozí verzi

✅ **Realistické náhledy** místo placeholderů  
✅ **Okamžitá zpětná vazba** - vidíte výsledek před vytvořením  
✅ **Flexibilní design** - nahrajte libovolný obrázek  
✅ **Multi-asset podpora** - přepínejte mezi variantami  
✅ **Production-ready** - reálné mockupy z Printify

## Další vylepšení v plánu

🔮 3D rotace produktů  
🔮 Více barevných variant produktů  
🔮 Customizace pozice designu  
🔮 Batch processing více designů najednou  
🔮 Export mockupů pro marketing

---

**Aktualizováno:** 4. ledna 2026  
**Verze:** 0.2.0  
**Status:** ✅ Aktivní a funkční
