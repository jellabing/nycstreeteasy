import requests
import time

def get_sales_listings(api_key, page_limit=5, delay=1):
    url = "https://streeteasy-api.p.rapidapi.com/sales/search"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "streeteasy-api.p.rapidapi.com"
    }

    all_sales = []
    offset = 0

    while True:
        print(f"Fetching page with offset {offset} ...")

        # Add you filters here
        # Supported filters https://streasy.gitbook.io/search-api
        query_params = {
            "limit": 100,
            "offset": offset,
            "areas": "chelsea",
            "maxPrice": 1500000
        }

        response = requests.get(url, headers=headers, params=query_params)

        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)
            break
        
        data = response.json()
        count = int(data.get("pagination").get("count"))

        if (offset >= count):
            break

        listings = data.get("listings", [])        
        all_sales.extend(listings)
        offset = offset + 100

    return all_sales


def get_sales_details(api_key, sale_id):
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "streeteasy-api.p.rapidapi.com"
    }

    details = requests.get(f"https://streeteasy-api.p.rapidapi.com/sales/{sale_id}", headers=headers)
    
    if details.status_code != 200:
        print(f"Details request failed for sale ID {sale_id} with status code {details.status_code}")
        return None
    
    rental_price = requests.get(f"https://streeteasy-api.p.rapidapi.com/sales/estimate/rent/1741373", headers=headers)
    if (rental_price.status_code != 200):
        print(rental_price.text)
        print(f"Rental price prediction request failed for sale ID {sale_id} with status code {rental_price.status_code}")
        return None

    ## Compute rental yield and other metrics
    price = details.json().get("price")
    rent  = rental_price.json().get("rental_price")
    yield_percentage = (rent * 12 / price) * 100

    data = {
        "url": f"streeteasy.com/sale/{sale_id}",
        "price": details.json().get("price"),
        "rental_price": rental_price.json().get("rental_price"),
        "rental_yield": yield_percentage
    }

    return data


if __name__ == "__main__":

    rapid_api_key = "<your_api_key>"

    all_sales = get_sales_listings(api_key=rapid_api_key)
    all_sales_details = [get_sales_details(rapid_api_key, sale["id"]) for sale in all_sales]
    top_leads = sorted(
        all_sales_details,
        key=lambda sale: sale.get("rental_yield", float('inf')),
        reverse=True
    )

    print(top_leads)


