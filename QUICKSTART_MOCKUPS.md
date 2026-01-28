# 🚀 Rychlý start - Mockup náhledy

## Vyzkoušejte novou funkci za 2 minuty!

### 1. Otevřete aplikaci
```
http://localhost:8501
```

### 2. Přejděte na "📦 Create Products"
V levém menu klikněte na **"📦 Create Products"**

### 3. Nahrajte testovací logo
```
🎨 Nahrajte vlastní design nebo logo
[Click "Browse files"]
→ Vyberte: test_images/test_logo.png
```

### 4. Sledujte živé náhledy! 👀
Scrollujte dolů a uvidíte:
- ✅ Logo na tričkách
- ✅ Logo na hrncích  
- ✅ Logo na plakátech
- ✅ Logo na polštářích
- ✅ A mnoho dalších!

### 5. Vyzkoušejte změnu designu
Klikněte **"🗑️ Smazat"** a nahrajte jiný obrázek:
```
test_images/test_pattern.png
```
→ Všechny náhledy se okamžitě aktualizují!

## Demo obrázky k dispozici

V `test_images/` najdete:
- **test_logo.png** - Jednoduché modré logo s textem
- **test_pattern.png** - Barevný vzor

## Co zkusit dál?

### Experimentujte s různými typy:
1. **Průhledné logo** (PNG s alfa kanálem)
   - Ideální pro: trička, mikiny, topy
   - Pozadí bude průhledné

2. **Celoplošný design** (bez průhlednosti)
   - Ideální pro: plakáty, plátna, polštáře
   - Vyplní celou plochu

3. **Ikona nebo malý design**
   - Ideální pro: hrnky, lahve, tašky
   - Centrované umístění

### Porovnejte kategorie:
- **👕 Oblečení** - design na hrudi
- **🖼️ Nástěnné umění** - design vyplní rám
- **☕ Nádobí** - design na přední straně
- **🏠 Domov** - centrovaný design
- **🎒 Doplňky** - optimalizované umístění

## Tipy pro nejlepší výsledky

✅ **Použijte vysoké rozlišení** (min. 1000×1000 px)  
✅ **PNG s průhledností** pro oblečení  
✅ **Čtverčí formát** funguje nejlépe  
✅ **Kontrastní barvy** jsou vidět lépe  
✅ **Jednoduchý design** funguje na všech produktech

## Troubleshooting

### Náhled se nezobrazuje?
- Zkontrolujte, že aplikace běží: http://localhost:8501
- Restartujte stránku (F5)
- Zkontrolujte konzoli v prohlížeči (F12)

### Obrázek je moc malý/velký?
- Každý produkt má automatické škálování
- Pro jemné doladění upravte config v `ui/streamlit_app.py`

### Chci jiné umístění designu?
- Upravte `mockup_configs` v `composite_design_on_mockup()`
- `scale`: 0.0-1.0 (velikost)
- `pos_x`, `pos_y`: 0.0-1.0 (pozice)

---

**Máte otázky?** Podívejte se do `PRODUCT_MOCKUP_FEATURE.md` pro detailní dokumentaci.
