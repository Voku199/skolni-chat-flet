import decimal

def compute_pi_bbp(digits):
    decimal.getcontext().prec = digits + 2
    pi = decimal.Decimal(0)

    for k in range(digits):
        pi += (decimal.Decimal(1)/(16**k)) * (
            (decimal.Decimal(4)/(8*k+1)) - (decimal.Decimal(2)/(8*k+4)) -
            (decimal.Decimal(1)/(8*k+5)) - (decimal.Decimal(1)/(8*k+6))
        )

    return str(pi)[:-1]

if __name__ == "__main__":
    num_digits = 1000  # Zde můžete změnit počet desetinných míst
    try:
        while True:
            pi_value = compute_pi_bbp(num_digits)
            print(f"π: {pi_value}")
            num_digits += 1000  # Zvyšuje přesnost o 10 desetinných míst při každém cyklu
    except KeyboardInterrupt:
        print("Konec výpočtu π.")