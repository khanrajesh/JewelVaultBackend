from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
from backend.shared.utils import set as set_response
import re

logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]


def get_headers():
    """Return HTTP headers with rotating user-agent"""
    return {
        'User-Agent': USER_AGENTS[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def parse_price(price_str: str) -> str:
    """Extract numeric price from a string.

    Picks the first numeric occurrence (handles cases like '₹2,10,722.11-6531.67  (-3.01%)').
    Returns the number as a plain string without commas, or empty string when none found.
    """
    if not price_str:
        return ""
    s = price_str.replace("₹", "")
    m = re.search(r"[\d,]+(?:\.\d+)?", s)
    if not m:
        logger.warning(f"parse_price: no numeric price found in '{price_str}'")
        return ""
    return m.group(0).replace(",", "")


def extract_date_from_text(text: str):
    """Return a datetime parsed from date strings like 'Rate on 15 December 2025'."""
    m = re.search(r"(\d{1,2})\s*([A-Za-z]+)\s*(\d{4})", text)
    if not m:
        return None
    try:
        return datetime.strptime(" ".join(m.groups()), "%d %B %Y")
    except ValueError:
        return None


def get_table_headers_and_rows(table):
    """Return (headers, data_rows) for tables that sometimes use <td> for headers."""
    header_cells = table.find_all("th")
    if header_cells:
        headers = [cell.get_text(strip=True).lower() for cell in header_cells]
        rows = table.find_all("tr")[1:]
    else:
        first_row = table.find("tr")
        headers = (
            [cell.get_text(strip=True).lower() for cell in first_row.find_all(["th", "td"])]
            if first_row
            else []
        )
        rows = table.find_all("tr")[1:] if first_row else table.find_all("tr")
    return headers, rows


def fetch_gold_24k_angel_one() -> dict:
    """
    Fetch gold 24K price from AngelOne website.
    Returns dict with keys: source, metal, caratOrPurity, price, updatedDate
    """
    url = "https://www.angelone.in/gold-rates-today"
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        
        doc = BeautifulSoup(response.content, 'html.parser')
        table_rows = doc.select("tr.MuiTableRow-root")
        
        for row in table_rows:
            cells = row.select("td.MuiTableCell-root")
            
            if len(cells) >= 4:
                gram_text = cells[0].get_text(strip=True)
                price_24k_elem = cells[1].select_one("div")
                price_24k_text = price_24k_elem.get_text(strip=True) if price_24k_elem else ""
                
                if "1 gm" in gram_text.lower() and price_24k_text:
                    price = parse_price(price_24k_text)
                    logger.info(f"AngelOne fetched Gold 24K price: {price}")
                    return {
                        "source": "AngelOne",
                        "metal": "Gold",
                        "caratOrPurity": "24K",
                        "price": price,
                        "updatedDate": today
                    }
        
        logger.error(f"AngelOne no data found parsing gold rates from {url}")
        return {
            "source": "AngelOne",
            "metal": "Gold",
            "caratOrPurity": "24K",
            "price": "0",
            "error": "No data found",
            "updatedDate": today
        }
    except Exception as e:
        logger.warning(f"AngelOne fetch failed: {str(e)}")
        logger.error(f"AngelOne fetch exception for {url}: {e}")
        return {
            "source": "AngelOne",
            "metal": "Gold",
            "caratOrPurity": "24K",
            "price": "0",
            "error": str(e),
            "updatedDate": today
        }

def fetch_silver_1kg_angel_one() -> dict:
    """
    Fetch silver 1kg price from AngelOne website.
    Returns dict with keys: source, metal, caratOrPurity, price, updatedDate
    """
    url = "https://www.angelone.in/silver-rates-today"
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()

        doc = BeautifulSoup(response.content, "html.parser")

        # Look for "Silver / 1 kg" label
        label = doc.find(string=lambda t: t and "silver / 1 kg" in t.lower())

        if label:
            container = label.find_parent("div")

            # Search nearby for price
            for el in container.find_all_next("div", limit=10):
                text = el.get_text(strip=True)
                if "₹" in text:
                    price = parse_price(text)
                    logger.info(f"AngelOne fetched Silver 1Kg price: {price}")
                    return {
                        "source": "AngelOne",
                        "metal": "Silver",
                        "caratOrPurity": "1 Kg",
                        "price": price,
                        "updatedDate": today
                    }

        logger.error(f"AngelOne no data found parsing silver rates from {url}")
        return {
            "source": "AngelOne",
            "metal": "Silver",
            "caratOrPurity": "1 Kg",
            "price": "0",
            "error": "No data found",
            "updatedDate": today
        }

    except Exception as e:
        logger.warning(f"AngelOne silver fetch failed: {str(e)}")
        logger.error(f"AngelOne silver fetch exception for {url}: {e}")
        return {
            "source": "AngelOne",
            "metal": "Silver",
            "caratOrPurity": "1 Kg",
            "price": "0",
            "error": str(e),
            "updatedDate": today
        }

def fetch_gold_24k_good_returns() -> dict:
    cities = ["mumbai", "delhi", "bangalore", "chennai"]
    base_url = "https://www.goodreturns.in/gold-rates/"
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for city in cities:
        url = f"{base_url}{city}.html"

        try:
            logger.info(f"[GoodReturns Gold] Trying city: {city}")
            response = requests.get(url, headers=get_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"[GoodReturns Gold] {city} returned status {response.status_code}")
                continue

            doc = BeautifulSoup(response.content, "html.parser")
            table = doc.find("table")

            if not table:
                logger.warning(f"[GoodReturns Gold] No table found for {city}")
                continue

            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue

                purity = cells[0].get_text(strip=True).upper()
                price_text = cells[1].get_text(strip=True)

                if "24" in purity:
                    price = parse_price(price_text)
                    logger.info(f"[GoodReturns Gold] 24K fetched from {city}: {price}")

                    return {
                        "source": "GoodReturns",
                        "metal": "Gold",
                        "caratOrPurity": "24K",
                        "price": price,
                        "city": city.capitalize(),
                        "updatedDate": today
                    }

            logger.warning(f"[GoodReturns Gold] 24K not found for {city}")

        except Exception as e:
            logger.warning(f"[GoodReturns Gold] Failed for {city}: {str(e)}")
            continue

    logger.error("[GoodReturns Gold] All city attempts failed")

    return {
        "source": "GoodReturns",
        "metal": "Gold",
        "caratOrPurity": "24K",
        "price": "0",
        "error": "All city sources failed",
        "updatedDate": today
    }

def fetch_silver_1kg_good_returns() -> dict:
    cities = ["mumbai", "delhi", "bangalore", "chennai"]
    base_url = "https://www.goodreturns.in/silver-rates/"
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for city in cities:
        url = f"{base_url}{city}.html"

        try:
            logger.info(f"[GoodReturns Silver] Trying city: {city}")
            response = requests.get(url, headers=get_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"[GoodReturns Silver] {city} returned status {response.status_code}")
                continue

            doc = BeautifulSoup(response.content, "html.parser")
            table = doc.find("table")

            if not table:
                logger.warning(f"[GoodReturns Silver] No table found for {city}")
                continue

            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue

                qty_text = cells[0].get_text(strip=True).lower()
                price_text = cells[1].get_text(strip=True)

                if "1 kg" in qty_text or "1kg" in qty_text:
                    price = parse_price(price_text)
                    logger.info(
                        f"[GoodReturns Silver] 1Kg fetched from {city}: {price}"
                    )

                    return {
                        "source": "GoodReturns",
                        "metal": "Silver",
                        "caratOrPurity": "1 Kg",
                        "price": price,
                        "city": city.capitalize(),
                        "updatedDate": today
                    }

            logger.warning(f"[GoodReturns Silver] 1Kg not found for {city}")

        except Exception as e:
            logger.warning(f"[GoodReturns Silver] Failed for {city}: {str(e)}")
            continue

    logger.error("[GoodReturns Silver] All city attempts failed")

    return {
        "source": "GoodReturns",
        "metal": "Silver",
        "caratOrPurity": "1 Kg",
        "price": "0",
        "error": "All city sources failed",
        "updatedDate": today
    }


def fetch_gold_24k_bankbazaar() -> dict:
    """
    Fetch gold 24K price from BankBazaar gold rate page.
    Prefers the per-gram price in the Parameters table (latest dated row), with a city table fallback.
    """
    url = "https://www.bankbazaar.com/gold-rate-india.html"
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()

        doc = BeautifulSoup(response.content, "html.parser")

        best_price = None
        best_date = None

        # Primary: parameters table with per-gram 24K price
        for table in doc.find_all("table"):
            headers, rows = get_table_headers_and_rows(table)
            if not headers:
                continue
            if not any("gold price" in h and "24" in h for h in headers):
                continue

            try:
                price_idx = next(i for i, h in enumerate(headers) if "gold price" in h and "24" in h)
            except StopIteration:
                continue

            for row in rows:
                cells = row.find_all("td")
                if len(cells) <= price_idx:
                    continue

                label = cells[0].get_text(" ", strip=True)
                value_text = cells[price_idx].get_text(" ", strip=True)

                if "gram" not in value_text.lower():
                    continue

                price = parse_price(value_text)
                if not price:
                    continue

                row_date = extract_date_from_text(label)
                if row_date and (best_date is None or row_date > best_date):
                    best_date, best_price = row_date, price
                elif best_price is None:
                    best_price = price

            if best_price:
                break

        # Fallback: city table that lists 24K price for N grams (usually 8g)
        if not best_price:
            for table in doc.find_all("table"):
                headers, rows = get_table_headers_and_rows(table)
                if not headers:
                    continue

                header_text = " ".join(headers)
                if "24k gold rate" not in header_text:
                    continue

                gram_match = re.search(r"(\d+)\s*grams", header_text)
                grams = int(gram_match.group(1)) if gram_match else 8

                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        price_text = cells[2].get_text(" ", strip=True)
                        price = parse_price(price_text)
                        if price:
                            try:
                                per_gram = float(price) / grams
                                best_price = str(round(per_gram, 2))
                            except Exception:
                                best_price = price
                            break

                if best_price:
                    break

        if best_price:
            return {
                "source": "BankBazaar",
                "metal": "Gold",
                "caratOrPurity": "24K",
                "price": best_price,
                "updatedDate": today
            }

        return {
            "source": "BankBazaar",
            "metal": "Gold",
            "caratOrPurity": "24K",
            "price": "0",
            "error": "24K gold not found",
            "updatedDate": today
        }

    except Exception as e:
        return {
            "source": "BankBazaar",
            "metal": "Gold",
            "caratOrPurity": "24K",
            "price": "0",
            "error": str(e),
            "updatedDate": today
        }


def fetch_silver_1kg_bankbazaar() -> dict:
    """
    Fetch silver 1kg price from BankBazaar silver rate page.
    """
    url = "https://www.bankbazaar.com/silver-rate-india.html"
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()

        doc = BeautifulSoup(response.content, "html.parser")
        best_price = None
        best_date = None

        # Primary: parameters table with per-kg silver price
        for table in doc.find_all("table"):
            headers, rows = get_table_headers_and_rows(table)
            if not headers:
                continue
            if not any("silver price" in h and "kg" in h for h in headers):
                continue

            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue

                label = cells[0].get_text(" ", strip=True)
                value_text = cells[1].get_text(" ", strip=True)

                if "rate of silver on" not in label.lower():
                    continue

                price = parse_price(value_text)
                if not price:
                    continue

                row_date = extract_date_from_text(label)
                if row_date and (best_date is None or row_date > best_date):
                    best_date, best_price = row_date, price
                elif best_price is None:
                    best_price = price

            if best_price:
                break

        # Fallback: city table with price per 10 grams -> scale to 1kg
        if not best_price:
            for table in doc.find_all("table"):
                headers, rows = get_table_headers_and_rows(table)
                if not headers:
                    continue
                if not any("price per 10 grams" in h for h in headers):
                    continue

                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        price_text = cells[1].get_text(" ", strip=True)
                        price_10g = parse_price(price_text)
                        if price_10g:
                            try:
                                price_kg = float(price_10g) * 100
                                best_price = str(round(price_kg, 2))
                            except Exception:
                                best_price = price_10g
                            break

                if best_price:
                    break

        if best_price:
            return {
                "source": "BankBazaar",
                "metal": "Silver",
                "caratOrPurity": "1 Kg",
                "price": best_price,
                "updatedDate": today
            }

        return {
            "source": "BankBazaar",
            "metal": "Silver",
            "caratOrPurity": "1 Kg",
            "price": "0",
            "error": "Silver 1kg not found",
            "updatedDate": today
        }

    except Exception as e:
        return {
            "source": "BankBazaar",
            "metal": "Silver",
            "caratOrPurity": "1 Kg",
            "price": "0",
            "error": str(e),
            "updatedDate": today
        }


@require_GET
def metal_rate(request):    
    try:
        # Fetch rates from all sources in parallel would be ideal, but doing sequentially for now
        
        gold_angel_one = fetch_gold_24k_angel_one()
        silver_angel_one = fetch_silver_1kg_angel_one()

        # gold_good_returns = fetch_gold_24k_good_returns()
        # silver_good_returns = fetch_silver_1kg_good_returns()
        
        gold_bankbazaar = fetch_gold_24k_bankbazaar()
        silver_bankbazaar = fetch_silver_1kg_bankbazaar()
        
        # Select best available data (first valid non-zero price)
        def get_best_rate(sources):
            valid = [s for s in sources if s.get("price") not in (None, "", "0")]
            return valid[0] if valid else None

        # compute simplified response values using all sources
        gold_best = get_best_rate([gold_bankbazaar, gold_angel_one])
        silver_best = get_best_rate([silver_bankbazaar, silver_angel_one])

        # if not gold_best:
        #     logger.error(f"No valid gold price from sources. GoodReturns: {gold_good_returns.get('error')}, AngelOne: {gold_angel_one.get('error')}")

        # if not silver_best:
        #     logger.error(f"No valid silver price from sources. GoodReturns: {silver_good_returns.get('error')}, AngelOne: {silver_angel_one.get('error')}")

        def to_float_or_none(val):
            try:
                if val is None:
                    return None
                s = str(val)
                m = re.search(r"[\d,]+(?:\.\d+)?", s)
                if not m:
                    logger.warning(f"Failed to find numeric part for float conversion: {val}")
                    return None
                v = float(m.group(0).replace(",", ""))
                return v
            except Exception:
                logger.warning(f"Failed to convert price to float: {val}")
                return None

        # Gold: convert per gram price to 10gm total
        gold_price_per_gram = gold_best.get("price") if gold_best else None
        gold_val_num = to_float_or_none(gold_price_per_gram)
        gold_10gm = round(gold_val_num * 10, 2) if gold_val_num is not None else None

        # Silver: expecting 1kg price
        silver_price = silver_best.get("price") if silver_best else None
        silver_val_num = to_float_or_none(silver_price)
        silver_1kg = round(silver_val_num, 2) if silver_val_num is not None else None

        payload = {
            "timestamp": datetime.now().isoformat(),
            "rates": [
                {
                    "metal": "gold",
                    "unit_gm": 10,
                    "price": gold_10gm,
                },
                {
                    "metal": "silver",
                    "unit_gm": 1000,
                    "price": silver_1kg,
                },
            ],
        }

        logger.info(f"Computed rates payload: {payload}")

        return set_response(True, data=payload, status_code=200)
    except Exception as e:
        logger.error(f"Error in metal_rate endpoint: {str(e)}", exc_info=True)
        # on unexpected error return nulls as requested
        err_payload = {
            "timestamp": datetime.now().isoformat(),
            "rates": [
                {"metal": "gold", "unit_gm": 10, "price": None},
                {"metal": "silver", "unit_gm": 1000, "price": None},
            ],
        }
        return set_response(False, message=str(e), data=err_payload, status_code=500)

