from enum import Enum

class AccountType(str, Enum):
    CURRENT = "CURRENT"                    # Vadesiz

    SAVING_ACCOUNT = "SAVING_ACCOUNT"      # Tasarruf

    TERM_ACCOUNT = "TERM_ACCOUNT"          # Vadeli

    TREASURY_ACCOUNT = "TREASURY_ACCOUNT"  # Hazine/Treasury

    LOAN_ACCOUNT = "LOAN_ACCOUNT"          # Kredi hesabı

    CREDIT_CARD_ACCOUNT = "CREDIT_CARD_ACCOUNT"  # Kredi kartı

    SALARY_ACCOUNT = "SALARY_ACCOUNT"      # Maaş hesabı

    FOREIGN_CURRENCY_ACCOUNT = "FOREIGN_CURRENCY_ACCOUNT"  # Döviz hesabı

    JOINT_ACCOUNT = "JOINT_ACCOUNT"        # Müşterek hesap

    INVESTMENT_ACCOUNT = "INVESTMENT_ACCOUNT"  # Yatırım hesabı