
# Exponential Moving Average
def EMA(df, column, span):
    return df[column].ewm(span=span, adjust=False).mean()

# Simple Moving Average
def SMA(df, column, span):
    return df[column].rolling(window=span).mean()

# Relative Strength Index
def RSI(df, column, period=14):
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
