#!/usr/bin/env python3
"""Test kompletního workflow bez API - s 12 náhodnými obrázky."""

import random
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()


def create_dummy_image(width: int, height: int, text: str, output_path: Path) -> Path:
    """Vytvoří dummy obrázek s textem.
    
    Args:
        width: Šířka obrázku
        height: Výška obrázku
        text: Text na obrázku
        output_path: Cesta pro uložení
        
    Returns:
        Cesta k vytvořenému obrázku
    """
    # Random barva pozadí
    colors = [
        (255, 182, 193),  # Light pink
        (173, 216, 230),  # Light blue
        (144, 238, 144),  # Light green
        (255, 218, 185),  # Peach
        (221, 160, 221),  # Plum
        (255, 255, 224),  # Light yellow
        (255, 228, 196),  # Bisque
        (230, 230, 250),  # Lavender
    ]
    
    bg_color = random.choice(colors)
    
    # Vytvoř obrázek
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Přidej text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Vypočítej pozici textu (centrovaný)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Nakresli stín
    shadow_offset = 3
    draw.text(
        (position[0] + shadow_offset, position[1] + shadow_offset),
        text,
        fill=(0, 0, 0, 128),
        font=font
    )
    
    # Nakresli text
    draw.text(position, text, fill=(0, 0, 0), font=font)
    
    # Ulož
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    
    return output_path


def generate_mock_seo_data(animal: str, index: int) -> dict:
    """Generuje mock SEO data bez API.
    
    Args:
        animal: Název zvířete
        index: Index obrázku
        
    Returns:
        Dictionary s SEO daty
    """
    styles = ["Minimalist", "Watercolor", "Abstract", "Vintage", "Modern"]
    adjectives = ["Cute", "Majestic", "Playful", "Elegant", "Wild"]
    
    style = random.choice(styles)
    adjective = random.choice(adjectives)
    
    return {
        "title": f"{adjective} {animal} Wall Art - {style} Design #{index}",
        "description": f"Beautiful {style.lower()} {animal.lower()} artwork perfect for home decor. "
                      f"High-quality print featuring a {adjective.lower()} {animal.lower()} in stunning detail. "
                      f"Perfect for living room, bedroom, or office. Makes a great gift!",
        "tags": [
            animal.lower(),
            f"{animal.lower()} art",
            f"{animal.lower()} print",
            f"{style.lower()} art",
            "wall art",
            "home decor",
            "animal print",
            f"{adjective.lower()} {animal.lower()}",
            "gift idea",
            "printable art",
            f"{animal.lower()} poster",
            "digital download",
            "instant download"
        ][:13]  # Etsy limit
    }


def generate_mock_facts(animal: str, count: int = 3) -> list[str]:
    """Generuje mock fakty o zvířeti.
    
    Args:
        animal: Název zvířete
        count: Počet faktů
        
    Returns:
        List faktů
    """
    facts_templates = [
        f"{animal}s can sleep up to 16 hours a day! 😴",
        f"The average {animal.lower()} weighs about 4-5 kg 📏",
        f"{animal}s have been domesticated for over 4,000 years! 🏛️",
        f"A {animal.lower()}'s purr can help heal bones and reduce stress! 💚",
        f"{animal}s can rotate their ears 180 degrees! 👂",
        f"Ancient Egyptians worshipped {animal.lower()}s as sacred animals! 🐱",
        f"{animal}s spend 70% of their time sleeping or resting! 💤",
        f"A {animal.lower()}'s nose print is unique, like a human fingerprint! 🔍"
    ]
    
    return random.sample(facts_templates, min(count, len(facts_templates)))


def simulate_workflow(num_images: int = 12):
    """Simuluje kompletní workflow bez API.
    
    Args:
        num_images: Počet obrázků k vygenerování
    """
    console.print(Panel.fit(
        "[bold cyan]🎨 Artomate Test Workflow (No API)[/]\n"
        f"Generuji {num_images} testovacích obrázků s kompletním workflow",
        border_style="cyan"
    ))
    
    # Zvířata pro test
    animals = [
        "Cat", "Dog", "Fox", "Bear", "Wolf", "Lion", 
        "Tiger", "Elephant", "Giraffe", "Panda", "Koala", "Rabbit"
    ]
    
    # Příprava složek
    base_dir = Path("/workspaces/artomate/test_output_no_api")
    images_dir = base_dir / "images"
    videos_dir = base_dir / "videos"
    mockups_dir = base_dir / "mockups"
    data_dir = base_dir / "data"
    
    for dir_path in [images_dir, videos_dir, mockups_dir, data_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        for i in range(num_images):
            animal = animals[i % len(animals)]
            
            task = progress.add_task(f"[cyan]Zpracovávám #{i+1}: {animal}...", total=None)
            
            # 1. Vytvoř dummy obrázek
            image_path = images_dir / f"{animal.lower()}_{i+1:02d}.png"
            create_dummy_image(
                width=1024,
                height=1024,
                text=f"{animal} #{i+1}",
                output_path=image_path
            )
            
            # 2. Generuj SEO data
            seo_data = generate_mock_seo_data(animal, i+1)
            
            # 3. Generuj fakty
            facts = generate_mock_facts(animal)
            
            # 4. "Vytvoř" video metadata (simulace)
            video_data = {
                "format": random.choice(["tiktok", "instagram_reel", "youtube_short"]),
                "duration": random.choice([15, 30, 60]),
                "has_music": True,
                "has_facts": True,
                "facts": facts
            }
            
            # 5. "Vytvoř" mockup data
            mockup_sizes = ["8x10", "11x14", "16x20", "24x36"]
            
            results.append({
                "index": i + 1,
                "animal": animal,
                "image_path": str(image_path.relative_to(base_dir)),
                "seo": seo_data,
                "video": video_data,
                "mockup_sizes": mockup_sizes,
                "facts": facts
            })
            
            progress.update(task, completed=True)
    
    # Uložit výsledky do JSON
    import json
    
    results_path = data_dir / "workflow_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Zobraz výsledky
    console.print(f"\n[bold green]✅ Hotovo! Vytvořeno {num_images} testovacích sad[/]\n")
    
    # Tabulka s výsledky
    table = Table(title="Výsledky testování")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Zvíře", style="magenta")
    table.add_column("Obrázek", style="green")
    table.add_column("SEO Title", style="yellow", width=40)
    table.add_column("Fakty", style="blue")
    table.add_column("Video", style="red")
    
    for result in results[:10]:  # Zobraz prvních 10
        table.add_row(
            str(result["index"]),
            result["animal"],
            "✅",
            result["seo"]["title"][:37] + "..." if len(result["seo"]["title"]) > 40 else result["seo"]["title"],
            f"{len(result['facts'])}x",
            result["video"]["format"]
        )
    
    if len(results) > 10:
        table.add_row("...", "...", "...", "...", "...", "...")
    
    console.print(table)
    
    # Statistiky
    console.print(f"\n[bold]📊 Statistiky:[/]")
    console.print(f"  • Celkem obrázků: [cyan]{num_images}[/]")
    console.print(f"  • SEO titulků: [cyan]{num_images}[/]")
    console.print(f"  • SEO popisů: [cyan]{num_images}[/]")
    console.print(f"  • SEO tagů: [cyan]{sum(len(r['seo']['tags']) for r in results)}[/]")
    console.print(f"  • Faktů celkem: [cyan]{sum(len(r['facts']) for r in results)}[/]")
    console.print(f"  • Video formátů: [cyan]{num_images}[/]")
    console.print(f"  • Mockup variant: [cyan]{num_images * len(mockup_sizes)}[/]")
    
    console.print(f"\n[bold green]📁 Výstupy uloženy v:[/] [cyan]{base_dir}[/]")
    console.print(f"  • Obrázky: [cyan]{images_dir}[/]")
    console.print(f"  • Data: [cyan]{results_path}[/]\n")
    
    # Ukázka jednoho produktu
    sample = results[0]
    console.print(Panel.fit(
        f"[bold]📦 Ukázka produktu #{sample['index']}:[/]\n\n"
        f"[yellow]Zvíře:[/] {sample['animal']}\n"
        f"[yellow]Title:[/] {sample['seo']['title']}\n"
        f"[yellow]Tagy:[/] {', '.join(sample['seo']['tags'][:5])}...\n"
        f"[yellow]Fakty:[/]\n" + "\n".join(f"  • {fact}" for fact in sample['facts'][:3]) + "\n"
        f"[yellow]Video:[/] {sample['video']['format']} ({sample['video']['duration']}s)\n"
        f"[yellow]Mockups:[/] {', '.join(sample['mockup_sizes'])}",
        title="🎨 Detail produktu",
        border_style="green"
    ))


def main():
    """Hlavní funkce."""
    try:
        console.print("\n[bold cyan]🚀 Starting Artomate No-API Test...[/]\n")
        simulate_workflow(num_images=12)
        console.print("\n[bold green]✅ Test dokončen![/]")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Test přerušen uživatelem[/]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Chyba: {e}[/]")
        raise


if __name__ == "__main__":
    main()
