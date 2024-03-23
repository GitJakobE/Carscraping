def generate_urls(unique_brands):
    urls = []
    for brand in unique_brands:
        i = 1
        while True:
            url = f"https://www.bilbasen.dk/brugt/bil/{brand}?IncludeEngrosCVR=false&PriceFrom=0&includeLeasing=false&NewAndUsed=2&WithInLast=30&IncludeWithoutVehicleRegistrationTax=false&IncludeSellForCustomer=false&page={i}"
            urls.append(url)
            i += 1
            # Add logic to break the loop if necessary
            # if <condition>:
            #     break
    return urls