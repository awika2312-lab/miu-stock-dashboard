for symbol in symbols:

    overview = get_overview(symbol)
    quote = get_quote(symbol)

    st.write(symbol, quote)

    quote_data = quote.get("Global Quote", {})

    price = quote_data.get("05. price", "N/A")
    change_pct = quote_data.get("10. change percent", "N/A")

    rows.append({
        "Ticker": symbol,
        "Company": overview.get("Name", "N/A"),
        "Price": price,
        "Change %": change_pct,
        "Market Cap": overview.get("MarketCapitalization", "N/A"),
        "P/E": overview.get("PERatio", "N/A"),
        "P/S": overview.get("PriceToSalesRatioTTM", "N/A")
    })
