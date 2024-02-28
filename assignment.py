import pandas as pd
import features as f

def main():
    df = pd.read_csv("./data.csv", parse_dates = True)

    df['tot_claim_cnt_l180d'] = df.apply(lambda row: f.calc_tot_claim(row["contracts"]), axis=1)
    df['disb_active_bank_loan_wo_tbc'] = df.apply(lambda row: f.calc_disb_active_bank_loan(row["contracts"]), axis=1)
    df['day_sinlastloan'] = df.apply(lambda row: f.calc_day_sinlastloan(row["contracts"]), axis=1)

    print(df)
    df.to_csv("./contract_features.csv")

main()
