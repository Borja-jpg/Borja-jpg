#!/usr/bin/env python3
"""
=============================================================================
NEXARA JOB RADAR — Madrid (InfoJobs + LinkedIn)
Buscador automatizado de ofertas de empleo para técnicos de telefonía,
reparación, hardware y telecomunicaciones en la Comunidad de Madrid.
=============================================================================
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
OUTPUT_JSON = os.path.join(BASE_DIR, "jobs.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

# Búsquedas clave para el perfil de Borja
QUERIES = [
    "tecnico reparacion moviles",
    "tecnico reparacion telefonia",
    "tecnico electronico moviles",
    "reparacion telefonos",
    "tecnico hardware",
    "tecnico microelectronica",
    "tecnico informatica",
    "tecnico telecomunicaciones"
]

CHROME_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

# Palabras clave para puntuar afinidad con el CV de Borja
PROFILE_KEYWORDS = {
    "movil": 20, "moviles": 20, "telefonia": 20, "smartphone": 20,
    "reparacion": 18, "reparador": 18, "pantalla": 18, "pantallas": 18,
    "electronica": 12, "electronico": 12, "microelectronica": 18,
    "hardware": 12, "informatica": 10, "ordenador": 10, "ordenadores": 10,
    "anovo": 25, "mediamarkt": 20, "phone house": 20, "orange": 15,
    "san sebastian de los reyes": 25, "alcobendas": 20, "madrid": 10
}


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def calculate_match_score(title, description, city, company):
    text = f"{title} {description} {city} {company}".lower()
    score = 45  # base score
    for kw, points in PROFILE_KEYWORDS.items():
        if kw in text:
            score += points
    return min(score, 99)


def format_salary(salary_data):
    if not salary_data or not isinstance(salary_data, dict):
        return "A convenir / No especificado"
    
    range_info = salary_data.get("range", {})
    min_val = range_info.get("min")
    max_val = range_info.get("max")
    period = salary_data.get("period", "YEAR")
    period_str = "año" if period == "YEAR" else ("mes" if period == "MONTH" else "hora")
    
    if min_val and max_val and min_val != max_val:
        return f"{min_val:,.0f}€ - {max_val:,.0f}€ / {period_str}".replace(",", ".")
    elif min_val:
        return f"desde {min_val:,.0f}€ / {period_str}".replace(",", ".")
    elif max_val:
        return f"hasta {max_val:,.0f}€ / {period_str}".replace(",", ".")
    return "A convenir / No especificado"


# =============================================================================
# 1. SCRAPER INFOJOBS
# =============================================================================
def fetch_infojobs(query):
    url = f"https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword={urllib.parse.quote(query)}&provinceIds=33"
    req = urllib.request.Request(url, headers=CHROME_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            prefix = '__INITIAL_PROPS__ = JSON.parse("'
            if prefix in html:
                start = html.find(prefix) + len(prefix)
                end = html.find('");', start)
                raw = html[start:end].encode("utf-8").decode("unicode_escape")
                data = json.loads(raw)
                return data.get("offers", [])
    except Exception as e:
        print(f"  [!] Error InfoJobs '{query}': {e}")
    return []


# =============================================================================
# 2. SCRAPER LINKEDIN (Guest Jobs API)
# =============================================================================
def fetch_linkedin(query):
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={urllib.parse.quote(query)}&location=Madrid&start=0"
    headers = {
        "User-Agent": CHROME_HEADERS["User-Agent"],
        "Accept-Language": "es-ES,es;q=0.9"
    }
    req = urllib.request.Request(url, headers=headers)
    results = []
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # Extraer títulos, empresas y links
            titles = re.findall(r'<h3 class="base-search-card__title">([^<]+)</h3>', html)
            companies = re.findall(r'<h4 class="base-search-card__subtitle">\s*<a[^>]*>([^<]+)</a>', html)
            locations = re.findall(r'<span class="job-search-card__location">([^<]+)</span>', html)
            links = re.findall(r'<a class="base-card__full-link[^\"]*" href="([^\"?]+)', html)

            for i in range(min(len(titles), len(links))):
                comp = companies[i].strip() if i < len(companies) else "Confidencial"
                loc = locations[i].strip() if i < len(locations) else "Madrid"
                job_id = "li_" + (re.search(r'-([0-9]+)$', links[i]).group(1) if re.search(r'-([0-9]+)$', links[i]) else str(i))
                results.append({
                    "id": job_id,
                    "title": titles[i].strip().replace("&amp;", "&"),
                    "companyName": comp.replace("&amp;", "&"),
                    "city": loc,
                    "salary": None,
                    "link": links[i],
                    "contractType": "Ver en LinkedIn",
                    "description": f"Oferta publicada en LinkedIn para puesto técnico en {loc}.",
                    "source": "LinkedIn"
                })
    except Exception as e:
        print(f"  [!] Error LinkedIn '{query}': {e}")
    return results


# =============================================================================
# MOTOR PRINCIPAL
# =============================================================================
def run_radar():
    print(f"\n📡 [NEXARA JOB RADAR] Iniciando escaneo Madrid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    history = load_history()
    all_jobs = {}
    new_jobs = []

    # 1. Rastrear InfoJobs
    for q in QUERIES:
        print(f" -> [InfoJobs] Buscando: '{q}'...")
        ij_offers = fetch_infojobs(q)
        print(f"    Encontradas {len(ij_offers)} ofertas.")
        for item in ij_offers:
            code = item.get("code") or item.get("newBOId")
            if not code or code in all_jobs:
                continue

            raw_link = item.get("link", "")
            if raw_link.startswith("//"):
                full_link = "https:" + raw_link
            elif raw_link.startswith("/"):
                full_link = "https://www.infojobs.net" + raw_link
            else:
                full_link = raw_link

            title = item.get("title", "").strip()
            city = item.get("city", "Madrid").strip()
            company = item.get("companyName", "Confidencial").strip()
            salary_str = format_salary(item.get("salary"))
            desc = item.get("description", "").strip()
            published = item.get("publishedAt", "")
            contract = item.get("contractType", "Indefinido")

            is_first_time = code not in history
            score = calculate_match_score(title, desc, city, company)

            job_obj = {
                "id": code,
                "title": title,
                "company": company,
                "city": city,
                "salary": salary_str,
                "link": full_link,
                "contract": contract,
                "published": published,
                "description": desc[:280] + "..." if len(desc) > 280 else desc,
                "score": score,
                "source": "InfoJobs",
                "is_new": is_first_time,
                "first_seen": history.get(code, {}).get("first_seen", datetime.now().strftime("%Y-%m-%d %H:%M"))
            }

            all_jobs[code] = job_obj
            if is_first_time:
                new_jobs.append(job_obj)
                history[code] = {"title": title, "company": company, "first_seen": job_obj["first_seen"]}

        time.sleep(1)

    # 2. Rastrear LinkedIn
    for q in ["reparacion moviles", "tecnico hardware", "tecnico informatica", "tecnico telecomunicaciones"]:
        print(f" -> [LinkedIn] Buscando: '{q}'...")
        li_offers = fetch_linkedin(q)
        print(f"    Encontradas {len(li_offers)} ofertas.")
        for item in li_offers:
            code = item["id"]
            if code in all_jobs:
                continue

            title = item["title"]
            company = item["companyName"]
            city = item["city"]
            desc = item["description"]
            score = calculate_match_score(title, desc, city, company)

            is_first_time = code not in history
            job_obj = {
                "id": code,
                "title": title,
                "company": company,
                "city": city,
                "salary": "Ver en LinkedIn",
                "link": item["link"],
                "contract": item["contractType"],
                "published": "Reciente",
                "description": desc,
                "score": score,
                "source": "LinkedIn",
                "is_new": is_first_time,
                "first_seen": history.get(code, {}).get("first_seen", datetime.now().strftime("%Y-%m-%d %H:%M"))
            }

            all_jobs[code] = job_obj
            if is_first_time:
                new_jobs.append(job_obj)
                history[code] = {"title": title, "company": company, "first_seen": job_obj["first_seen"]}

        time.sleep(1)

    # Ordenar por afinidad y novedad
    sorted_jobs = sorted(all_jobs.values(), key=lambda x: (x["is_new"], x["score"]), reverse=True)
    
    save_history(history)

    # Guardar JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted_jobs, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Total ofertas consolidadas: {len(sorted_jobs)} | Nuevas hoy: {len(new_jobs)}")

    # Generar Dashboard Web Interactivo
    generate_html_dashboard(sorted_jobs, len(new_jobs))

    # Notificación Telegram (opcional)
    send_telegram_notification(new_jobs)

    return sorted_jobs, new_jobs


def generate_html_dashboard(jobs, new_count):
    now_str = datetime.now().strftime("%d/%m/%Y a las %H:%M")
    
    cards_html = ""
    for j in jobs:
        new_badge = '<span class="badge-new">⚡ NUEVA</span>' if j["is_new"] else ''
        high_badge = '<span class="badge-match">★ Gran Afinidad</span>' if j["score"] >= 70 else ''
        source_icon = 'fab fa-linkedin' if j['source'] == 'LinkedIn' else 'fas fa-briefcase'
        source_color = '#0a66c2' if j['source'] == 'LinkedIn' else '#ff6400'

        cards_html += f"""
        <article class="job-card {'is-new' if j['is_new'] else ''}" data-source="{j['source']}">
          <div class="job-card-header">
            <div class="job-meta-top">
              <span class="source-tag" style="background: {source_color}22; color: {source_color}; border-color: {source_color}44;">
                <i class="{source_icon}"></i> {j['source']}
              </span>
              <span class="job-company"><i class="fas fa-building"></i> {j['company']}</span>
              <span class="job-location"><i class="fas fa-location-dot"></i> {j['city']}</span>
              {new_badge}
              {high_badge}
            </div>
            <div class="job-score">
              <span class="score-val">{j['score']}%</span>
              <span class="score-lbl">Afinidad CV</span>
            </div>
          </div>

          <h3 class="job-title">{j['title']}</h3>
          
          <div class="job-perks">
            <span class="perk-tag salary"><i class="fas fa-wallet"></i> {j['salary']}</span>
            <span class="perk-tag contract"><i class="fas fa-file-contract"></i> {j['contract']}</span>
          </div>

          <p class="job-desc">{j['description']}</p>

          <div class="job-footer">
            <span class="job-date"><i class="far fa-clock"></i> Detectada: {j['first_seen']}</span>
            <a href="{j['link']}" target="_blank" class="btn-apply">
              <span>Postularme en {j['source']}</span>
              <i class="fas fa-arrow-up-right-from-square"></i>
            </a>
          </div>
        </article>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Radar de Empleo Técnico — Madrid | NEXARA</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />

  <style>
    :root {{
      --bg: #090a0f;
      --card-bg: #12141c;
      --border: rgba(255, 255, 255, 0.08);
      --accent: #38bdf8;
      --green: #10b981;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding-bottom: 4rem;
    }}
    header {{
      background: rgba(18, 20, 28, 0.85);
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(16px);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 1.25rem 1.5rem;
    }}
    .header-inner {{
      max-width: 960px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .brand-group {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .radar-pulse {{
      width: 12px;
      height: 12px;
      background: var(--green);
      border-radius: 50%;
      box-shadow: 0 0 12px var(--green);
      animation: pulse 1.8s infinite;
    }}
    @keyframes pulse {{
      0% {{ transform: scale(0.95); opacity: 0.7; }}
      50% {{ transform: scale(1.3); opacity: 1; }}
      100% {{ transform: scale(0.95); opacity: 0.7; }}
    }}
    h1 {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .meta-tag {{
      font-size: 0.82rem;
      color: var(--text-muted);
    }}
    .container {{
      max-width: 960px;
      margin: 2.5rem auto 0;
      padding: 0 1.5rem;
    }}
    .stats-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem;
    }}
    .stat-val {{
      font-size: 1.8rem;
      font-weight: 800;
      color: #fff;
    }}
    .stat-lbl {{
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .filter-bar {{
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.75rem;
      flex-wrap: wrap;
    }}
    .f-btn {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.4rem 1rem;
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .f-btn.active {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}
    .jobs-feed {{
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}
    .job-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.75rem;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .job-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(56, 189, 248, 0.35);
    }}
    .job-card.is-new {{
      border-color: rgba(16, 185, 129, 0.4);
      background: linear-gradient(180deg, rgba(16, 185, 129, 0.04) 0%, var(--card-bg) 100%);
    }}
    .job-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.75rem;
    }}
    .job-meta-top {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }}
    .source-tag {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      border: 1px solid;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }}
    .job-company {{
      font-weight: 700;
      color: #fff;
      font-size: 0.92rem;
    }}
    .job-location {{
      color: var(--text-muted);
      font-size: 0.84rem;
    }}
    .badge-new {{
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #34d399;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
    }}
    .badge-match {{
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: var(--accent);
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
    }}
    .job-score {{
      text-align: right;
    }}
    .score-val {{
      display: block;
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--accent);
    }}
    .score-lbl {{
      font-size: 0.68rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }}
    .job-title {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 0.75rem;
    }}
    .job-perks {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }}
    .perk-tag {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      padding: 0.3rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .perk-tag.salary {{
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.2);
    }}
    .job-desc {{
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
      line-height: 1.6;
    }}
    .job-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--border);
      padding-top: 1rem;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}
    .job-date {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}
    .btn-apply {{
      background: var(--accent);
      color: #000;
      font-weight: 700;
      font-size: 0.85rem;
      padding: 0.55rem 1.15rem;
      border-radius: 9999px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: background 0.2s, transform 0.2s;
    }}
    .btn-apply:hover {{
      background: #7dd3fc;
      transform: translateY(-1px);
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-inner">
      <div class="brand-group">
        <span class="radar-pulse"></span>
        <h1>NEXARA JOB RADAR</h1>
        <span class="meta-tag">· InfoJobs & LinkedIn Madrid</span>
      </div>
      <div class="meta-tag">
        Última actualización: <strong>{now_str}</strong>
      </div>
    </div>
  </header>

  <main class="container">
    
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-val">{len(jobs)}</div>
        <div class="stat-lbl">Ofertas Activas</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: #34d399;">+{new_count}</div>
        <div class="stat-lbl">Nuevas en este escaneo</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">Madrid & Norte</div>
        <div class="stat-lbl">Zona Geográfica</div>
      </div>
    </div>

    <div class="filter-bar">
      <button class="f-btn active" onclick="filterSource('all', this)">Todas las ofertas</button>
      <button class="f-btn" onclick="filterSource('InfoJobs', this)">Solo InfoJobs</button>
      <button class="f-btn" onclick="filterSource('LinkedIn', this)">Solo LinkedIn</button>
    </div>

    <section class="jobs-feed" id="jobsFeed">
      {cards_html}
    </section>

  </main>

  <script>
    function filterSource(source, btn) {{
      document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.job-card').forEach(card => {{
        if (source === 'all' || card.getAttribute('data-source') === source) {{
          card.style.display = 'block';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}
  </script>

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"📊 Dashboard HTML generado: {OUTPUT_HTML}")


def send_telegram_notification(new_jobs):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    # Si no están en variables de entorno, intentar cargar config.local.json
    local_cfg = os.path.join(BASE_DIR, "config.local.json")
    if (not bot_token or not chat_id) and os.path.exists(local_cfg):
        try:
            with open(local_cfg, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                bot_token = bot_token or cfg.get("TELEGRAM_BOT_TOKEN")
                chat_id = chat_id or cfg.get("TELEGRAM_CHAT_ID")
        except Exception:
            pass

    if not bot_token or not chat_id:
        return

    if not new_jobs:
        return

    print(f"📲 Enviando {len(new_jobs)} alertas a Telegram...")
    for j in new_jobs[:5]:
        msg = (
            f"🎯 <b>NUEVA OFERTA [{j['source']}]</b>\n\n"
            f"💼 <b>{j['title']}</b>\n"
            f"🏢 {j['company']} ({j['city']})\n"
            f"💶 {j['salary']}\n"
            f"📊 Afinidad con tu perfil: <b>{j['score']}%</b>\n\n"
            f"🔗 <a href='{j['link']}'>Ver oferta y postularme</a>"
        )

        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).encode("utf-8")

        req = urllib.request.Request(
            send_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                pass
        except Exception as e:
            print(f"  [!] Error Telegram: {e}")


if __name__ == "__main__":
    run_radar()
