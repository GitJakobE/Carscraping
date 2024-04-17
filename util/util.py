
def generate_urls(brand: str, page_nr: int, days: int) -> str:
    url = f"https://www.bilbasen.dk/brugt/bil/{brand}?IncludeEngrosCVR=false&PriceFrom=0&includeLeasing=false&NewAndUsed=2&WithInLast={days}&IncludeWithoutVehicleRegistrationTax=false&IncludeSellForCustomer=false&page={page_nr}"
    return url

